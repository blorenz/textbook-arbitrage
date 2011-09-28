from django.db import models
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey

# Create your models here.

# Amazon Textbook Sections

class Amazon_Textbook_Section(models.Model):
    title = models.CharField(max_length=250, null=True)
    url = models.CharField(max_length=250, unique=True)
    timestamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.title

class ATS_Middle(models.Model):
    section = models.ForeignKey('Amazon_Textbook_Section')
    page = models.IntegerField()
    
class Book(models.Model):
    pckey = models.CharField(primary_key=True,max_length=250)
    section = models.ForeignKey('Amazon_Textbook_Section')  
    title= models.CharField(max_length=250)
    isbn= models.CharField(max_length=250,null=True)
    isbn10=models.CharField(max_length=250,null=True)
    author = models.CharField(max_length=250,null=True)
    def __unicode__(self):
        return self.title
    
class Unique_Seller(models.Model):
    name = models.CharField(max_length=250)
    def __unicode__(self):
        return self.name
    
class Seller(models.Model):
    book = models.ForeignKey('Book')
    price = models.DecimalField(null=True,max_digits=7, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey('Unique_Seller', null=True)
    def __unicode__(self):
        return self.seller.name

class AmazonRankCategory(models.Model):
    category = models.CharField(max_length=250)   

    
class Amazon(models.Model):
    book = models.ForeignKey('Book')
    productcode = models.CharField(primary_key=True,max_length=250)
    timestamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.book.title
    
class AmazonRank(models.Model):
    amazon = models.ForeignKey('Amazon')
    rank = models.IntegerField()
    category = models.ForeignKey('AmazonRankCategory')
    timestamp = models.DateTimeField(auto_now=True)
    
    
class Price(models.Model):
    amazon = models.ForeignKey('Amazon', null=True)
    buy = models.DecimalField(null=True,max_digits=8,decimal_places=2)
    sell = models.DecimalField(null=True,max_digits=8,decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Proxy(models.Model):
    proxy_type = models.CharField(max_length=10)
    ip_and_port = models.CharField(max_length=25)
