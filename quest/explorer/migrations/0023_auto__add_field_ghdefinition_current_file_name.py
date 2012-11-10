# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'GhDefinition.current_file_name'
        db.add_column('explorer_ghdefinition', 'current_file_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'GhDefinition.current_file_name'
        db.delete_column('explorer_ghdefinition', 'current_file_name')


    models = {
        'explorer.appdata': {
            'Meta': {'object_name': 'AppData'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_wakeup': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'explorer.definitionmaterial': {
            'Meta': {'object_name': 'DefinitionMaterial'},
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.GhDefinition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'material': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.Material']"})
        },
        'explorer.definitionparam': {
            'Meta': {'object_name': 'DefinitionParam'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.GhDefinition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'param_type': ('django.db.models.fields.CharField', [], {'default': "'FL'", 'max_length': '2'}),
            'range_end': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'range_start': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'readable_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'stage': ('django.db.models.fields.IntegerField', [], {}),
            'values': ('explorer.models.PickledObjectField', [], {'null': 'True', 'blank': 'True'})
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
            'base_definition': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['explorer.GhDefinition']", 'null': 'True', 'blank': 'True'}),
            'current_file_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'default_material': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.Material']"}),
            'file_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.IntegerField', [], {}),
            'scene_file': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'uploaded_file_a': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'use_cache': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'explorer.item': {
            'Meta': {'object_name': 'Item'},
            'base_param_hash': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'definition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.GhDefinition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'material': ('django.db.models.fields.CharField', [], {'default': "'Gold'", 'max_length': '20'}),
            'num_trials': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'param_hash': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'params': ('explorer.models.PickledObjectField', [], {'null': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.Item']", 'null': 'True'}),
            'parent_distance': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'CR'", 'max_length': '2'}),
            'textParam': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        'explorer.material': {
            'Meta': {'object_name': 'Material'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'readable_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['explorer']
