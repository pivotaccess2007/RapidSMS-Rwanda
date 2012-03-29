from django.db import models

# Create your models here.
class Document_identification(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    document_name = models.FileField(upload_to='document/')

    def __str__(self):
        description=(' %s , %s ' % (self.name, self.description))
        return description
