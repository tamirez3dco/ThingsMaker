# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GhDefinition'
        db.create_table('explorer_ghdefinition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('param_names', self.gf('explorer.models.PickledObjectField')(null=True)),
            ('scene_file', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('product', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('explorer', ['GhDefinition'])

        # Adding model 'Item'
        db.create_table('explorer_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
            ('image_url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['explorer.Item'], null=True)),
            ('definition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['explorer.GhDefinition'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('params', self.gf('explorer.models.PickledObjectField')(null=True)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('selected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('parent_distance', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('explorer', ['Item'])

        # Adding model 'ExplorerConfig'
        db.create_table('explorer_explorerconfig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('k', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('v', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('explorer', ['ExplorerConfig'])

        # Adding model 'AppData'
        db.create_table('explorer_appdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('last_wakeup', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('explorer', ['AppData'])


    def backwards(self, orm):
        
        # Deleting model 'GhDefinition'
        db.delete_table('explorer_ghdefinition')

        # Deleting model 'Item'
        db.delete_table('explorer_item')

        # Deleting model 'ExplorerConfig'
        db.delete_table('explorer_explorerconfig')

        # Deleting model 'AppData'
        db.delete_table('explorer_appdata')


    models = {
        'explorer.appdata': {
            'Meta': {'object_name': 'AppData'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_wakeup': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'explorer.explorerconfig': {
            'Meta': {'object_name': 'ExplorerConfig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'k': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'v': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'explorer.ghdefinition': {
            'Meta': {'object_name': 'GhDefinition'},
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
            'params': ('explorer.models.PickledObjectField', [], {'null': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['explorer.Item']", 'null': 'True'}),
            'parent_distance': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['explorer']
