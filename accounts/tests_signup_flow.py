from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_student_signup_flow(self):
        # Step 1: Role selection
        response = self.client.post(reverse('signup') + '?step=1', {'role': 'student'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/signup/?step=2', response.url)

        # Step 2: User details
        user_details = {
            'first_name': 'John',
            'middle_name': 'M',
            'last_name': 'Doe',
            'date_of_birth': '2000-01-01',
            'gender': 'male',
            'school_name': 'Test School',
            'student_class': '10A',
            'date_of_admission': '2018-01-01',
            'time_of_admission': '09:00:00',
            'admission_number': 'ADM123',
        }
        response = self.client.post(reverse('signup') + '?step=2', user_details)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/signup/?step=3', response.url)

        # Step 3: Brought by details and account creation
        brought_by_data = {
            'id_number': 'ID123456',
            'phone_number': '1234567890',
            'first_name': 'Jane',
            'middle_name': 'A',
            'last_name': 'Doe',
            'relationship': 'Mother',
            'email': 'john.doe@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        }
        response = self.client.post(reverse('signup') + '?step=3', brought_by_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('student_dashboard'))

        # Verify user created
        user = User.objects.get(email='john.doe@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.admission_number, 'ADM123')
        self.assertEqual(user.role, 'student')

    def test_non_student_signup_flow(self):
        # Step 1: Role selection non-student
        response = self.client.post(reverse('signup') + '?step=1', {'role': 'librarian'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/signup/?step=2', response.url)

        # Step 2: User details (optional for non-student)
        user_details = {
            'first_name': 'Lib',
            'last_name': 'Rarian',
            'date_of_birth': '',
            'gender': '',
            'school_name': '',
            'student_class': '',
            'date_of_admission': '',
            'time_of_admission': '',
            'admission_number': '',
        }
        response = self.client.post(reverse('signup') + '?step=2', user_details)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/signup/?step=5', response.url)

        # Step 5: Account creation for non-student
        account_data = {
            'email': 'lib@example.com',
            'first_name': 'Lib',
            'last_name': 'Rarian',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        }
        response = self.client.post(reverse('signup') + '?step=5', account_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('librarian_dashboard'))

        # Verify user created
        user = User.objects.get(email='lib@example.com')
        self.assertEqual(user.role, 'librarian')
