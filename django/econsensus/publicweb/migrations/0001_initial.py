#@PydevCodeAnalysisIgnore
# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Decision'
        db.create_table('publicweb_decision', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('decided_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('effective_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('review_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('expiry_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('budget', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('people', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('tinymce.models.HTMLField')(blank=True)),
        ))
        db.send_create_signal('publicweb', ['Decision'])

        # Adding model 'Concern'
        db.create_table('publicweb_concern', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('decision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publicweb.Decision'])),
            ('description', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('resolved', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('publicweb', ['Concern'])


    def backwards(self, orm):
        
        # Deleting model 'Decision'
        db.delete_table('publicweb_decision')

        # Deleting model 'Concern'
        db.delete_table('publicweb_concern')


    models = {
        'publicweb.concern': {
            'Meta': {'object_name': 'Concern'},
            'decision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['publicweb.Decision']"}),
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resolved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
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
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['publicweb']
