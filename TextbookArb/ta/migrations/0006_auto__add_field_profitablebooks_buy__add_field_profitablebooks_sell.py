# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ProfitableBooks.buy'
        db.add_column('ta_profitablebooks', 'buy', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2), keep_default=False)

        # Adding field 'ProfitableBooks.sell'
        db.add_column('ta_profitablebooks', 'sell', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ProfitableBooks.buy'
        db.delete_column('ta_profitablebooks', 'buy')

        # Deleting field 'ProfitableBooks.sell'
        db.delete_column('ta_profitablebooks', 'sell')


    models = {
        'ta.amazon': {
            'Meta': {'object_name': 'Amazon'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Book']"}),
            'productcode': ('django.db.models.fields.CharField', [], {'max_length': '250', 'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ta.amazon_textbook_section': {
            'Meta': {'object_name': 'Amazon_Textbook_Section'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'})
        },
        'ta.amazonrank': {
            'Meta': {'object_name': 'AmazonRank'},
            'amazon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Amazon']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.AmazonRankCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ta.amazonrankcategory': {
            'Meta': {'object_name': 'AmazonRankCategory'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'ta.ats_middle': {
            'Meta': {'object_name': 'ATS_Middle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.IntegerField', [], {}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Amazon_Textbook_Section']"})
        },
        'ta.book': {
            'Meta': {'object_name': 'Book'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'isbn10': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'pckey': ('django.db.models.fields.CharField', [], {'max_length': '250', 'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Amazon_Textbook_Section']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'ta.metatable': {
            'Meta': {'object_name': 'MetaTable'},
            'float_field': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'int_field': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'metakey': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'metatype': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'string_field': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'ta.price': {
            'Meta': {'object_name': 'Price'},
            'amazon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Amazon']", 'null': 'True'}),
            'buy': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sell': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'ta.profitablebooks': {
            'Meta': {'object_name': 'ProfitableBooks'},
            'buy': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'price': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ta.Price']", 'primary_key': 'True'}),
            'sell': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'})
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
