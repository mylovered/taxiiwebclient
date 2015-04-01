# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Config'
        db.create_table(u'yeti_client_config', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=80, max_length=5)),
            ('inboxPath', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('inboxCollection', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('pollPath', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('pollCollection', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('pollRate', self.gf('django.db.models.fields.IntegerField')(default=60, max_length=5)),
            ('useTLS', self.gf('django.db.models.fields.CharField')(default='mutual', max_length=6)),
            ('privFile', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('pubFile', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('polling', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tstamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'yeti_client', ['Config'])

        # Adding model 'ReceivedFile'
        db.create_table(u'yeti_client_receivedfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('server', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('collection', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'yeti_client', ['ReceivedFile'])

        # Adding model 'Event'
        db.create_table(u'yeti_client_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('server', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('collection', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('operation', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('contents', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'yeti_client', ['Event'])


    def backwards(self, orm):
        # Deleting model 'Config'
        db.delete_table(u'yeti_client_config')

        # Deleting model 'ReceivedFile'
        db.delete_table(u'yeti_client_receivedfile')

        # Deleting model 'Event'
        db.delete_table(u'yeti_client_event')


    models = {
        u'yeti_client.config': {
            'Meta': {'object_name': 'Config'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inboxCollection': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'inboxPath': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'pollCollection': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'pollPath': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'pollRate': ('django.db.models.fields.IntegerField', [], {'default': '60', 'max_length': '5'}),
            'polling': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '80', 'max_length': '5'}),
            'privFile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'pubFile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'server': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'tstamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'user': ('django.db.models.fields.CharField', [], {'max_length': '64'})
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