import os, logging, string

from django import forms
from django.template.loader import render_to_string
from django.core.validators import RegexValidator

from models import Config

from email.mime.nonmultipart import MIMENonMultipart
from email.encoders import encode_base64

import libtaxii as t
import libtaxii.messages_11 as tm11


logger = logging.getLogger(__name__)

class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        exclude = [ 'polling', 'poll_req_tstamp', 'poll_resp_tstamp' ]

class PushFileForm(forms.Form):
    content_file = forms.FileField(label='Please select file:')

    def get_content_block(self, f):
        binding_map = {
            '.xlsx': ('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            '.xls': ('application', 'vnd.ms-excel'),
            '.csv': ('text', 'csv'),
            '.json': ('application', 'json'),
            '.syslog': ('text', 'syslog')
        }

        # Check the file extension to see if it is a supported type
        name_part, ext_part = os.path.splitext(f.name)

        if ext_part.lower() == '.xml':
            cb = tm11.ContentBlock(tm11.ContentBinding(t.CB_STIX_XML_101), f.read())
        else:
            binding_tuple = binding_map.get(ext_part.lower(), None)
            if not binding_tuple:
                logger.error('File extension not supported: %s. Supported extensions: %s' % (ext_part, binding_map.keys()))
                return

            # Read the file and create a MIME message for it
            maintype = binding_tuple[0]
            subtype = binding_tuple[1] # Note: This is MIME subtype, not TAXII subtype
            mime_msg = MIMENonMultipart(maintype, subtype)
            mime_msg.add_header('Content-Disposition', 'attachment', filename=f.name)
            mime_msg.set_payload(f.read())
            encode_base64(mime_msg)

            cb = tm11.ContentBlock('%s/%s' % (maintype, subtype), mime_msg.as_string())

        return cb

class PushStixIPForm(forms.Form):
    ip_list = forms.CharField(label='Value',
                              max_length=255,
                              validators=[RegexValidator(regex='^(([12]?[0-9]{1,2}\.){3}[0-9]{1,3}[;,]?\s*)+$', message='Value must be comma or semicolon separated IPs')])
    desc = forms.CharField(label='Description', max_length=512, required=False)

    def get_content_block(self):
        stix_ip_list = self.cleaned_data['ip_list']
        stix_ip_list = string.replace(stix_ip_list, ",", "##comma##")
        stix_ip_list = string.replace(stix_ip_list, ";", "##comma##")
        stix_ip_list = string.replace(stix_ip_list, " ", "")
        xml = render_to_string('stix-ip-list.xml',
                               {
                                   'stix_ip_list': stix_ip_list,
                                   'description' : self.cleaned_data['desc']
                                })
        cb = tm11.ContentBlock(t.CB_STIX_XML_101, xml)
        return cb

class PushStixEmailForm(forms.Form):
    email_list = forms.CharField(label='Value',
                              max_length=255,
                              validators=[RegexValidator(regex='^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-.]+[;,]?\s*)+$', message='Value must be comma or semicolon separated E-mails')])
    desc = forms.CharField(label='Description', max_length=512, required=False)

    def get_content_block(self):
        stix_email_list = self.cleaned_data['email_list']
        stix_email_list = string.replace(stix_email_list, ",", "##comma##")
        stix_email_list = string.replace(stix_email_list, ";", "##comma##")
        stix_email_list = string.replace(stix_email_list, " ", "")
        xml = render_to_string('stix-email-list.xml',
                               {
                                   'stix_email_list': stix_email_list,
                                   'description' : self.cleaned_data['desc']
                                })
        cb = tm11.ContentBlock(t.CB_STIX_XML_101, xml)
        return cb