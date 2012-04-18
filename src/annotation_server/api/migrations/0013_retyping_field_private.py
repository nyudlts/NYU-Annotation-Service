# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # read all annotations and theirs private fields into memory.
        dic = {}
        for ann in orm['api.Annotation'].objects.all():
            dic[ann.id] = not bool(ann.private)

        # delete old column
        db.delete_column('api_annotation', 'private')
        # create new column with new type - Boolean
        db.add_column('api_annotation', 'private', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        orm['api.Annotation'].objects.filter(
            id__in=[id for id, priv in dic.items() if priv]
        ).update(
            private=True
        )

        del dic


    def backwards(self, orm):
        "Write your backwards methods here."
         # read all annotations and theirs private fields into memory.
        dic = {}
        for ann in orm['api.Annotation'].objects.all():
            dic[ann.id] = not int(ann.private)

        # delete old column
        db.delete_column('api_annotation', 'private')
        # create new column with new type - Boolean
        db.add_column('api_annotation', 'private', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        orm['api.Annotation'].objects.filter(
            id__in=[id for id, priv in dic.items() if priv]
        ).update(
            private=0
        )

        del dic
        #assert 0, "No backward migration available yet!"


    models = {
        'api.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 28, 7, 41, 54, 865734)', 'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'has_answers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 28, 7, 41, 54, 865764)', 'auto_now': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'target': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['api.Target']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Comment'", 'max_length': '10'})
        },
        'api.constraint': {
            'Meta': {'object_name': 'Constraint'},
            'annotation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'constraints'", 'to': "orm['api.Annotation']"}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'endOffset': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'startOffset': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'target': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['api.Target']", 'symmetrical': 'False'})
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
