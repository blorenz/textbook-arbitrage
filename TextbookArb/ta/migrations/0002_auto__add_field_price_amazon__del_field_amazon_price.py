# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Price.amazon'
        db.add_column('ta_price', 'amazon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ta.Amazon'], null=True), keep_default=False)

        # Deleting field 'Amazon.price'
        db.delete_column('ta_amazon', 'price_id')


    def backwards(self, orm):
        
        # Deleting field 'Price.amazon'
        db.delete_column('ta_price', 'amazon_id')

        # Adding field 'Amazon.price'
        db.add_column('ta_amazon', 'price', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ta.Price'], null=True), keep_default=False)


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
            'buy': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sell': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
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
