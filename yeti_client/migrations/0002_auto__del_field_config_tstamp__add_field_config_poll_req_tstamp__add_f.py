# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Config.tstamp'
        db.delete_column(u'yeti_client_config', 'tstamp')

        # Adding field 'Config.poll_req_tstamp'
        db.add_column(u'yeti_client_config', 'poll_req_tstamp',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Config.poll_resp_tstamp'
        db.add_column(u'yeti_client_config', 'poll_resp_tstamp',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Config.tstamp'
        db.add_column(u'yeti_client_config', 'tstamp',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Config.poll_req_tstamp'
        db.delete_column(u'yeti_client_config', 'poll_req_tstamp')

        # Deleting field 'Config.poll_resp_tstamp'
        db.delete_column(u'yeti_client_config', 'poll_resp_tstamp')


    models = {
        u'yeti_client.config': {
            'Meta': {'object_name': 'Config'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inboxCollection': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'inboxPath': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'pollCollection': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'pollPath': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'pollRate': ('django.db.models.fields.IntegerField', [], {'default': '60', 'max_length': '5'}),
            'poll_req_tstamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'poll_resp_tstamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'polling': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '80', 'max_length': '5'}),
            'privFile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'pubFile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'server': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'useTLS': ('django.db.models.fields.CharField', [], {'default': "'mutual'", 'max_length': '6'})
        },
        u'yeti_client.event': {
            'Meta': {'object_name': 'Event'},
            'collection': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contents': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'server': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        u'yeti_client.receivedfile': {
            'Meta': {'object_name': 'ReceivedFile'},
            'collection': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'server': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['yeti_client']