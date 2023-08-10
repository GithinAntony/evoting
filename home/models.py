from django.db import models

# Create your models here.
class Contact(models.Model):
    unique_id = models.AutoField(primary_key=True)    
    full_name = models.CharField(max_length=255)
    email_address = models.EmailField()
    message = models.TextField()
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True) 
    
    def __str__(self):
        return self.full_name