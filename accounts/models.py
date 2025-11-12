from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    ROLE_CHOICES = [
        ('welfare', 'Welfare'),
        ('storekeeper', 'Storekeeper'),
        ('admin', 'Admin'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='welfare')
    profile_picture = CloudinaryField('image', blank=True, null=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)


    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.role})"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.timestamp}"

class BroughtBy(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255, blank=True, null=True)
    id_number = models.CharField(max_length=100, blank=True, null=True)
    relationship = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Brought by: {self.name}"

class Beneficiary(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    RESIDENCE_CHOICES = [
        ('temporary', 'Temporary'),
        ('permanent', 'Permanent'),
    ]

    # Personal Information
    first_name = models.CharField(max_length=100, default='Unknown')
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, default='Unknown')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    # Admission Information
    date_of_admission = models.DateField(null=True, blank=True)
    time_of_admission = models.TimeField(null=True, blank=True)
    admission_number = models.CharField(max_length=50, unique=True, default='TEMP-001')

    # Brought By Information
    brought_by = models.OneToOneField(BroughtBy, on_delete=models.CASCADE, null=True, blank=True)

    # Educational Information
    school_name = models.CharField(max_length=255, blank=True, null=True)
    student_class = models.CharField(max_length=50, blank=True, null=True)

    # Residence Information
    residence_type = models.CharField(max_length=20, choices=RESIDENCE_CHOICES, default='temporary')

    # Family Information
    has_relatives = models.BooleanField(default=False)
    relatives_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    has_siblings = models.BooleanField(default=False)
    siblings_count = models.PositiveIntegerField(default=0, blank=True, null=True)

    # Documents and Profile
    profile_picture = CloudinaryField('image', blank=True, null=True)
    documents = CloudinaryField('file', blank=True, null=True)

    # Metadata
    date_added = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Admission: {self.admission_number})"

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            self.age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        super().save(*args, **kwargs)

class EmailVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Code for {self.user.email}: {self.code}"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

class MedicalRecord(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='medical_records')
    date = models.DateField()
    diagnosis = models.TextField()
    treatment = models.TextField()
    doctor_name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    medical_documents = CloudinaryField('file', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medical Record for {self.beneficiary.first_name} {self.beneficiary.last_name} - {self.date}"

    class Meta:
        ordering = ['-date']
