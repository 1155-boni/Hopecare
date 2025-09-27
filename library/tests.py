from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Book, StudentBookRecord
from accounts.models import User

User = get_user_model()

class LibraryTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='teststudent', password='testpass123', role='student')
        self.librarian = User.objects.create_user(username='testlibrarian', password='testpass123', role='librarian')
        self.book = Book.objects.create(title='Test Book', author='Test Author', isbn='1234567890')

    def test_book_creation(self):
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.author, 'Test Author')

    def test_student_book_record_creation(self):
        record = StudentBookRecord.objects.create(student=self.student, book=self.book, date_read='2025-09-27')
        self.assertEqual(record.student.username, 'teststudent')
        self.assertEqual(record.book.title, 'Test Book')

    def test_add_book_view(self):
        self.client.login(username='testlibrarian', password='testpass123')
        response = self.client.post(reverse('add_book'), {'title': 'New Book', 'author': 'New Author', 'isbn': '0987654321'})
        self.assertEqual(response.status_code, 302)
        book = Book.objects.get(title='New Book')
        self.assertEqual(book.author, 'New Author')
