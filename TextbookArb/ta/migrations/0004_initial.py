# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Amazon_Textbook_Section'
        db.create_table('ta_amazon_textbook_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250, null=True)),
            ('url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ta', ['Amazon_Textbook_Section'])

        # Adding model 'Book'
        db.create_table('ta_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ta.Amazon_Textbook_Section'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('isbn', self.gf('django.db.models.fields.CharField')(max_length=250, null=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=250, null=True)),
        ))
        db.send_create_signal('ta', ['Book'])

        # Adding model 'Unique_Seller'
        db.create_table('ta_unique_seller', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('ta', ['Unique_Seller'])

        # Adding model 'Seller'
        db.create_table('ta_seller', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ta.Book'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('seller', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ta.Unique_Seller'], null=True)),
        ))
        db.send_create_signal('ta', ['Seller'])

        # Adding model 'Amazon'
        db.create_table('ta_amazon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ta.Book'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ta', ['Amazon'])

        # Adding model 'Price'
        db.create_table('ta_price', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amazon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ta.Amazon'], null=True)),
            ('buy', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
            ('sell', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('ta', ['Price'])

        # Adding model 'Proxy'
        db.create_table('ta_proxy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('proxy_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('ip_and_port', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal('ta', ['Proxy'])


    def backwards(self, orm):
        
        # Deleting model 'Amazon_Textbook_Section'
        db.delete_table('ta_amazon_textbook_section')

        # Deleting model 'Book'
        db.delete_table('ta_book')

        # Deleting model 'Unique_Seller'
        db.delete_table('ta_unique_seller')

        # Deleting model 'Seller'
        db.delete_table('ta_seller')

        # Deleting model 'Amazon'
        db.delete_table('ta_amazon')

        # Deleting model 'Price'
        db.delete_table('ta_price')

        # Deleting model 'Proxy'
        db.delete_table('ta_proxy')


    models = {
        'ta.amazon': {
            'Meta': {'object_name': 'Amazon'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'ta.amazon_textbook_section': {
            'Meta': {'object_name': 'Amazon_Textbook_Section'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'})
        },
        'ta.book': {
            'Meta': {'object_name': 'Book'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Amazon_Textbook_Section']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'ta.price': {
            'Meta': {'object_name': 'Price'},
            'amazon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Amazon']", 'null': 'True'}),
            'buy': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sell': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'ta.proxy': {
            'Meta': {'object_name': 'Proxy'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_and_port': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'proxy_type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'ta.seller': {
            'Meta': {'object_name': 'Seller'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            'seller': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Unique_Seller']", 'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ta.unique_seller': {
            'Meta': {'object_name': 'Unique_Seller'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        }
    }

    complete_apps = ['ta']
