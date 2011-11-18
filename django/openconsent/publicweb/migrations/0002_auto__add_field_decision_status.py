#@PydevCodeAnalysisIgnore
#pylint: disable-msg=W0613
# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Decision.status'
        db.add_column('publicweb_decision', 'status', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Decision.status'
        db.delete_column('publicweb_decision', 'status')


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
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['publicweb']
