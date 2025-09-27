from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from .models import AuditLog

User = get_user_model()

class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'teststudent',
            'email': 'test@example.com',
            'first_name': 'Test',
            'role': 'student',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }

    def test_user_creation(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'teststudent')
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.check_password('testpass123'))

    def test_signup_view(self):
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, 302)  # Redirect
        user = User.objects.get(username='teststudent')
        self.assertEqual(user.email, 'test@example.com')

    def test_login_view(self):
        User.objects.create_user(username='testuser', password='testpass123', role='student')
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_audit_log_creation(self):
        user = User.objects.create_user(username='audituser', password='pass', role='student')
        audit = AuditLog.objects.create(user=user, action='test_action', details='test details')
        self.assertEqual(audit.action, 'test_action')
