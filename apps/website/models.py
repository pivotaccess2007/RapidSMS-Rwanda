from django.db import models

# Create your models here.

class Document_identification(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    document_name = models.FileField(upload_to='apps/webapp/static/statsupp/document/')

    def __str__(self):
        description=(' %s , %s ' % (self.name, self.description))
        return description


class News_and_Event(models.Model):
    title_name = models.CharField(max_length=100)
    article_descr = models.TextField()
    date_created  = models.DateTimeField(auto_now=False)
    article_image = models.ImageField(upload_to='apps/webapp/static/statsupp/photo_article/')

    def __str__(self):
        description=(' %s , %s ' % (self.title_name, self.date_created))
        return description

class ContactMessage(models.Model):
    AUTO_CHOICES = ( ('Yes', 'Yes'), ('No', 'No') )
    name_sender = models.CharField(max_length=50)
    tel_sender =models.CharField(max_length=15)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    approved = models.CharField(max_length=5, choices = AUTO_CHOICES,blank=True)
    date_rec  = models.CharField(max_length=50)
	
    def __str__(self):
        description=(' %s , %s , %s ' % (self.name_sender, self.tel_sender , self.subject ))
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


class About_us_info(models.Model):
    title = models.CharField(max_length=50)
    content_part1 = models.TextField()
    content_part2 = models.TextField()
    founder_picture  = models.ImageField(upload_to='apps/webapp/static/statsupp/photo_aboutus/')
    minister_picture = models.ImageField(upload_to='apps/webapp/static/statsupp/photo_aboutus/')
    additional_info = models.CharField(max_length=100,blank=True)
    date_created  = models.DateTimeField(auto_now=True)    

    def __str__(self):
        description=(' %s , %s ' % (self.date_created,self.title))
        return description

class Faq(models.Model):
    question_descr = models.TextField()
    answer_descr = models.TextField()
    additional_info = models.CharField(max_length=100)
    date_created  = models.DateTimeField(auto_now=True)    

    def __str__(self):
        description=(' %s , %s ' % (self.date_created,self.question_descr))
        return description


class Join_us(models.Model):
    AUTO_CHOICES = ( ('Yes', 'Yes'), ('No', 'No') )
    full_name = models.CharField(max_length=50)
    username = models.CharField(max_length=15)
    email = models.TextField()
    phone_number = models.CharField(max_length=20)
    approved = models.CharField(max_length=5, choices = AUTO_CHOICES,blank=True)
    date_created  = models.DateTimeField(auto_now=True)    

    def __str__(self):
        description=(' %s , %s ' % (self.full_name,self.approved))
        return description


