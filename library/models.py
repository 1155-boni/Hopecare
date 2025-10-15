from django.db import models
from accounts.models import User
from cloudinary.models import CloudinaryField

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    cover = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.title


