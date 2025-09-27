from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('librarian', 'Librarian'),
        ('storekeeper', 'Storekeeper'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    BADGE_CHOICES = [
        ('none', 'None'),
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('diamond', 'Diamond'),
    ]
    badge = models.CharField(max_length=20, choices=BADGE_CHOICES, default='none')
    profile_picture = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
