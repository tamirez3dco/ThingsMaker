# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'DefinitionParam.index'
        db.add_column('explorer_definitionparam', 'index', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'DefinitionParam.index'
        db.delete_column('explorer_definitionparam', 'index')


    models = {
        'explorer.appdata': {
            'Meta': {'object_name': 'AppData'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_wakeup': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'explorer.definitionparam': {
            'Meta': {'object_name': 'DefinitionParam'},
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.GhDefinition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'readable_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'stage': ('django.db.models.fields.IntegerField', [], {})
        },
        'explorer.explorerconfig': {
            'Meta': {'object_name': 'ExplorerConfig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'k': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'v': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'explorer.ghdefinition': {
            'Meta': {'object_name': 'GhDefinition'},
            'accepts_text_params': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_names': ('explorer.models.PickledObjectField', [], {'null': 'True'}),
            'product': ('django.db.models.fields.IntegerField', [], {}),
            'scene_file': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'explorer.item': {
            'Meta': {'object_name': 'Item'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.GhDefinition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'material': ('django.db.models.fields.CharField', [], {'default': "'Gold'", 'max_length': '20'}),
            'params': ('explorer.models.PickledObjectField', [], {'null': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.Item']", 'null': 'True'}),
            'parent_distance': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'textParam': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['explorer']
