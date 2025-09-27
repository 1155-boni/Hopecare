from django.db import models
from accounts.models import User

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class StudentBookRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_read = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.book.title}"

class SchoolRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    subject = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)
    semester = models.CharField(max_length=50)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.student.username} - {self.subject} - {self.grade}"
