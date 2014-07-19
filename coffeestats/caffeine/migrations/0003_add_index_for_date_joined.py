# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.create_index('caffeine_user', ['date_joined'])

    def backwards(self, orm):
        db.drop_index('caffeine_user', ['date_joined'])
