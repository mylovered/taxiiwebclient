import os.path, logging, time, base64, email

from django.conf import settings
from django.db import models
from django.utils import timezone

from solo.models import SingletonModel

import libtaxii.clients as tc
import libtaxii as t
import libtaxii.messages_11 as tm11


logger = logging.getLogger(__name__)

MUTUAL = 'mutual'
SERVER = 'server'
NONE= 'none'
USE_TLS_CHOICES = (
    ( MUTUAL, 'mutual' ),
    ( SERVER, 'server' ),
    ( NONE, 'none' ),
)

PUSH = 'push'
PULL = 'pull'

SUPPORTED_BINDING_IDS = ['text/csv',
                         'application/vnd.ms-excel',
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         'urn:stix.mitre.org:xml:1.0.1',
                         'application/json']

RECEIVED_FILES_DIR = os.path.join(settings.MEDIA_ROOT, 'received')


class Config(SingletonModel):
    server = models.CharField(max_length=64)
    port = models.IntegerField(max_length=5, default=80)
    inboxPath = models.CharField('Inbox Path', max_length=128)
    inboxCollection = models.CharField('Inbox Collection', max_length=32)
    pollPath = models.CharField('Poll Path', max_length=128)
    pollCollection = models.CharField('Poll Collection', max_length=32)
    pollRate = models.IntegerField('Poll Rate (seconds)', max_length=5, default=60)
    useTLS = models.CharField('TLS Authentication', max_length=6,
                              choices=USE_TLS_CHOICES,
                              default=MUTUAL)
    privFile = models.FileField('Private Key File', upload_to='settings', blank=True)
    pubFile = models.FileField('Public Certificate', upload_to='settings', blank=True)
    polling = models.BooleanField(default=False)
    poll_req_tstamp = models.DateTimeField(blank=True, null=True)
    poll_resp_tstamp = models.DateTimeField(blank=True, null=True)

    # This is called every time the form is created
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        # Make sure the directory for received files exists
        if not os.path.exists(RECEIVED_FILES_DIR):
            os.makedirs(RECEIVED_FILES_DIR)

        if args:
            # Make sure the key and cert files exist, otherwise blank the fields
            if not os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.privFile.name)):
                self.privFile = None
            if not os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.pubFile.name)):
                self.pubFile = None

    # Gets called after a form is submitted to do form field validation
    def clean(self):
        # Service paths must have a leading slash
        if self.inboxPath and not self.inboxPath.startswith('/'):
            self.inboxPath = '/' + self.inboxPath
        
        if not self.inboxPath.endswith('/'):
            self.inboxPath += '/'
        
        if self.pollPath and not self.pollPath.startswith('/'):
            self.pollPath = '/' + self.pollPath

        if not self.pollPath.endswith('/'):
            self.pollPath += '/'

    def push_event(self, user, result, contents):
        self.create_event(PUSH, user, self.inboxCollection, result, contents)

    def pull_event(self, contents):
        self.create_event(PULL, '', self.pollCollection, '', contents)

    def create_event(self, operation, user, collection, result, contents):
        e = Event(user=user, server=self.server, collection=collection,
                  operation=operation, result=result, contents=contents)
        e.save()

    def call_inbox(self, content_block):
        inbox_message = tm11.InboxMessage(tm11.generate_message_id())
        inbox_message.content_blocks.append(content_block)
        logger.debug("Created Inbox Message for collection %s" % self.inboxCollection)
        return self.call_client(self.inboxPath + self.inboxCollection, inbox_message)
        
    def call_poll(self):
        poll_params = tm11.PollRequest.PollParameters(content_bindings = SUPPORTED_BINDING_IDS)
        poll_request = tm11.PollRequest(tm11.generate_message_id(),
                                        collection_name = self.pollCollection,
                                        exclusive_begin_timestamp_label = self.poll_resp_tstamp,
                                        poll_parameters = poll_params)
        logger.debug("Created Poll Request for collection %s" % self.pollCollection)
        return self.call_client(self.pollPath, poll_request)

    def call_client(self, path, taxii_message):
        client = tc.HttpClient()
        client.setUseHttps(True)
        client.setProxy('noproxy')

        if self.useTLS == MUTUAL:
            client.setAuthType(tc.HttpClient.AUTH_CERT)
            client.setAuthCredentials(
                {'key_file': os.path.join(settings.MEDIA_ROOT, self.privFile.name),
                 'cert_file': os.path.join(settings.MEDIA_ROOT, self.pubFile.name)
                })
        elif self.useTLS == SERVER:
            raise ValueError('SERVER auth type not yet implemented')

        logger.debug("Calling TAXII Service: %s:%s%s" % (self.server, self.port, path))

        resp = client.callTaxiiService2(self.server, path,
                                        t.VID_TAXII_XML_11, taxii_message.to_xml(),
                                        port=self.port)

        msg = t.get_message_from_http_response(resp, '0')
        return msg

    def poll_request(self):
        binding_ids = ['text/csv',
                   'application/vnd.ms-excel',
                   'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                   'urn:stix.mitre.org:xml:1.0.1',
                   'application/json']

        while 1:
            resp = self.call_poll()
            self.poll_req_tstamp = timezone.now()
            self.save()

            if not resp.message_type == tm11.MSG_STATUS_MESSAGE:
                self.poll_resp_tstamp = resp.inclusive_end_timestamp_label
                self.save()

                logger.debug('Timestamp label updated: %s' % self.poll_resp_tstamp)

                # Extract the contents and base64 decode
                logger.info("Received %s content blocks" % len(resp.content_blocks))

                for cb in resp.content_blocks:
                    filename = ''

                    if cb.content_binding.binding_id == "urn:xbis.mitre.org:base64":
                        msg_id = resp.message_id
                        collection = resp.collection_name
                        timestamp = timezone.now().isoformat().replace(':','')
                        filename = "_".join([ collection, msg_id, timestamp ]) + '.xls'

                        decoded = base64.b64decode(cb.content)
                        out_file = open(os.path.join(RECEIVED_FILES_DIR, filename), "wb")
                        out_file.write(bytearray(decoded))
                        out_file.flush()
                        out_file.close()
                    elif cb.content_binding.binding_id == "urn:stix.mitre.org:xml:1.0.1":
                        msg_id = resp.message_id
                        collection = resp.collection_name
                        timestamp = timezone.now().isoformat().replace(':','')
                        filename = "_".join(['stix101_', collection, msg_id, timestamp ]) + '.xml'
                        out_file = open(os.path.join(RECEIVED_FILES_DIR, filename), "w")
                        out_file.write(cb.content)
                        out_file.flush()
                        out_file.close()
                    elif cb.content_binding.binding_id in binding_ids:
                        mime_message = email.message_from_string(cb.content)
                        filename = mime_message.get_filename()
                        mime_payload = mime_message.get_payload(decode=True)
                        out_file = open(os.path.join(RECEIVED_FILES_DIR, filename), "wb")
                        out_file.write(bytearray(mime_payload))
                        out_file.flush()
                        out_file.close()
                    else:
                        logger.error('Unknown binding id: %s' % cb.content_binding.binding_id)

                    # Make sure the file doesn't already exist before creating the received file entry.
                    # This check prevents duplicates from showing up in the pulled files list.
                    if not os.path.isfile(filename):
                        received_file = ReceivedFile(
                            server = self.server,
                            collection = self.pollCollection,
                            filename = filename)
                        received_file.save()
                        self.pull_event('File: ' + filename)

            time.sleep(self.pollRate)

    def __unicode__(self):
        return u"Config"
    class Meta:
        verbose_name = "Config"
        verbose_name_plural = "Config"


class ReceivedFile(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    server = models.CharField(max_length=64)
    collection = models.CharField(max_length=32)
    filename = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Received Files"
        verbose_name_plural = "Received Files"


class Event(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=64, blank=True)
    server = models.CharField(max_length=64)
    collection = models.CharField(max_length=32)
    operation = models.CharField(max_length=10)
    result = models.CharField(max_length=32, blank=True)
    contents = models.TextField(blank=True)

    class Meta:
        verbose_name = "Event History"
        verbose_name_plural = "Event History"
