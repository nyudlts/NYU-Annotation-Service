# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Annotation.creation_date'
        db.delete_column('api_annotation', 'creation_date')

        # Adding field 'Annotation.created_at'
        db.add_column('api_annotation', 'created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 7, 3, 52, 4, 103789), auto_now_add=True, blank=True), keep_default=False)

        # Adding field 'Annotation.modified_at'
        db.add_column('api_annotation', 'modified_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 7, 3, 52, 4, 103817), auto_now=True, blank=True), keep_default=False)

        # Adding field 'Annotation.deleted'
        db.add_column('api_annotation', 'deleted', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Annotation.deleted_at'
        db.add_column('api_annotation', 'deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Annotation.creation_date'
        db.add_column('api_annotation', 'creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2011, 10, 7, 3, 52, 36, 530705), blank=True), keep_default=False)

        # Deleting field 'Annotation.created_at'
        db.delete_column('api_annotation', 'created_at')

        # Deleting field 'Annotation.modified_at'
        db.delete_column('api_annotation', 'modified_at')

        # Deleting field 'Annotation.deleted'
        db.delete_column('api_annotation', 'deleted')

        # Deleting field 'Annotation.deleted_at'
        db.delete_column('api_annotation', 'deleted_at')


    models = {
        'api.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 7, 3, 52, 4, 103789)', 'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 7, 3, 52, 4, 103817)', 'auto_now': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'target': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['api.Target']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Comment'", 'max_length': '10'})
        },
        'api.constraint': {
            'Meta': {'object_name': 'Constraint'},
            'blob': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['api.Target']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'api.profile': {
            'Meta': {'object_name': 'Profile', '_ormbases': ['auth.User']},
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'api.target': {
            'Meta': {'object_name': 'Target'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['api']
