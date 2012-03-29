from django.db import models

# Create your models here.

class Document_identification(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    document_name = models.FileField(upload_to='document/')

    def __str__(self):
        description=(' %s , %s ' % (self.name, self.description))
        return description


class News_and_Event(models.Model):
    title_name = models.CharField(max_length=100)
    article_descr = models.TextField()
    date_created  = models.DateTimeField(auto_now=False)
    article_image = models.ImageField(upload_to='photo_article/')

    def __str__(self):
        description=(' %s , %s ' % (self.title_name, self.date_created))
        return description

class ContactMessage(models.Model):
    name_sender = models.CharField(max_length=50)
    tel_sender =models.CharField(max_length=15)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    date_rec  = models.CharField(max_length=50)
	
    def __str__(self):
        description=(' %s , %s , %s ,%s ' % (self.name_sender, self.tel_sender , self.subject , self.message ))
        return description


class Location(models.Model):
    type_id = models.IntegerField()
    name= models.CharField(max_length=100)
    code= models.CharField(max_length=30)
    parent_id= models.IntegerField()
    latitude = models.DecimalField(max_digits=8, decimal_places=6)
    longitude = models.DecimalField(max_digits=8, decimal_places=6)
    
    def __str__(self):
        description=(' %s ' % (self.name))
        return description
