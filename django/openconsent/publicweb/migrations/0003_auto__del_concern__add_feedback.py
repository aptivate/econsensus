# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Concern'
        db.delete_table('publicweb_concern')

        # Adding model 'Feedback'
        db.create_table('publicweb_feedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('decision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publicweb.Decision'])),
            ('description', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('resolved', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('publicweb', ['Feedback'])


    def backwards(self, orm):
        
        # Adding model 'Concern'
        db.create_table('publicweb_concern', (
            ('resolved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('decision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publicweb.Decision'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('publicweb', ['Concern'])

        # Deleting model 'Feedback'
        db.delete_table('publicweb_feedback')


    models = {
        'publicweb.decision': {
            'Meta': {'object_name': 'Decision'},
            'budget': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'decided_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'effective_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'people': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'review_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'publicweb.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'decision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['publicweb.Decision']"}),
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resolved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['publicweb']
