from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from .models import AuditLog, BroughtBy, MedicalRecord
from library.models import StudentBookRecord, SchoolRecord

User = get_user_model()

class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'teststudent',
            'email': 'test@example.com',
            'first_name': 'Test',
            'role': 'student',
            'password': 'testpass123',
        }

    def test_user_creation(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'teststudent')
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.check_password('testpass123'))

    # Removed signup and login tests as per user request

    def test_audit_log_creation(self):
        user = User.objects.create_user(username='audituser', password='pass', role='student')
        audit = AuditLog.objects.create(user=user, action='test_action', details='test details')
        self.assertEqual(audit.action, 'test_action')

    def test_profile_view_get(self):
        user = User.objects.create_user(username='testuser', password='testpass123', role='student', first_name='Test')
        self.client.force_login(user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_view_post(self):
        user = User.objects.create_user(username='testuser', password='testpass123', role='student')
        self.client.force_login(user)
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        response = self.client.post(reverse('profile'), data)
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')

    def test_delete_profile_view(self):
        user = User.objects.create_user(username='testuser', password='testpass123', role='student', first_name='TestUser')
        # Create related records
        BroughtBy.objects.create(
            user=user,
            first_name='Parent',
            last_name='Name',
            relationship='Parent'
        )
        AuditLog.objects.create(user=user, action='test', details='test')
        MedicalRecord.objects.create(student=user, description='Test record')
        from datetime import date
        StudentBookRecord.objects.create(student=user, book=None, date_read=date.today())
        SchoolRecord.objects.create(student=user, subject='Math', grade='A', semester='Fall', year=2023)

        self.client.force_login(user)
        response = self.client.post(reverse('delete_profile'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

        # Verify user is deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='testuser')

        # Verify related records are deleted (cascade deletion)
        self.assertEqual(BroughtBy.objects.filter(user=user).count(), 0)
        self.assertEqual(AuditLog.objects.filter(user=user).count(), 0)
        self.assertEqual(MedicalRecord.objects.filter(student=user).count(), 0)
        self.assertEqual(StudentBookRecord.objects.filter(student=user).count(), 0)
        self.assertEqual(SchoolRecord.objects.filter(student=user).count(), 0)

    def test_delete_profile_view_get_request(self):
        user = User.objects.create_user(username='testuser', password='testpass123', role='student')
        self.client.force_login(user)
        response = self.client.get(reverse('delete_profile'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile'))
