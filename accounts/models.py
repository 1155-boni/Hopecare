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
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_picture = CloudinaryField('image', blank=True, null=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    school_name = models.CharField(max_length=100, blank=True, null=True)
    student_class = models.CharField(max_length=20, blank=True, null=True)
    date_of_admission = models.DateField(blank=True, null=True)
    time_of_admission = models.TimeField(blank=True, null=True)
    admission_number = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.role})"

class BroughtBy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='brought_by')
    id_number = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    relationship = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Brought by {self.first_name} {self.last_name} for {self.user.email}"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.timestamp}"

class MedicalRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    record_date = models.DateField(auto_now_add=True)
    description = models.TextField()
    doctor_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Medical Record for {self.student.email} on {self.record_date}"
