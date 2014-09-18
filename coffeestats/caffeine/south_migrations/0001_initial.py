# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'caffeine_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cryptsum', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('timezone', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, blank=True)),
        ))
        db.send_create_signal(u'caffeine', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name(u'caffeine_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'caffeine.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name(u'caffeine_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'caffeine.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

        # Adding model 'Caffeine'
        db.create_table(u'caffeine_caffeine', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ctype', self.gf('django.db.models.fields.PositiveSmallIntegerField')(db_index=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['caffeine.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('entrytime', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now, db_index=True)),
            ('timezone', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, blank=True)),
        ))
        db.send_create_signal(u'caffeine', ['Caffeine'])

        # Adding model 'Action'
        db.create_table(u'caffeine_action', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['caffeine.User'])),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('validuntil', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('atype', self.gf('django.db.models.fields.PositiveSmallIntegerField')(db_index=True)),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'caffeine', ['Action'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'caffeine_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name(u'caffeine_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name(u'caffeine_user_user_permissions'))

        # Deleting model 'Caffeine'
        db.delete_table(u'caffeine_caffeine')

        # Deleting model 'Action'
        db.delete_table(u'caffeine_action')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'caffeine.action': {
            'Meta': {'object_name': 'Action'},
            'atype': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['caffeine.User']"}),
            'validuntil': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'caffeine.caffeine': {
            'Meta': {'object_name': 'Caffeine'},
            'ctype': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'entrytime': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['caffeine.User']"})
        },
        u'caffeine.user': {
            'Meta': {'object_name': 'User'},
            'cryptsum': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['caffeine']