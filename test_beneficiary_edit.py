import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hopecare_project.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()
welfare_user = User.objects.get(email='welfare@hopecare.com')
login_success = client.login(email='welfare@hopecare.com', password='welfare@123')
print(f'Login success: {login_success}')

# Test 1: Check if the page loads and has the edit elements
response = client.get('/accounts/beneficiary/1/', HTTP_HOST='localhost')
print(f'Preview page status: {response.status_code}')
if response.status_code == 200:
    content = response.content.decode()
    checks = [
        ('Edit button in Personal Information', 'Edit' in content and 'Personal Information' in content),
        ('View mode div', 'beneficiary-view-mode' in content),
        ('Edit mode div', 'beneficiary-edit-mode' in content),
        ('Toggle function', 'toggleBeneficiaryEditMode()' in content),
        ('View mode initially visible', 'beneficiary-view-mode' in content and 'display: block' in content),
        ('Edit mode initially hidden', 'beneficiary-edit-mode' in content and 'display: none' in content),
        ('Form fields present', 'name="first_name"' in content and 'name="last_name"' in content),
        ('Action field', 'name="action" value="edit_beneficiary"' in content),
    ]
    for check_name, result in checks:
        status = '✓' if result else '✗'
        print(f'{status} {check_name}')
else:
    print(f'✗ Error loading page: {response.status_code}')

# Test 2: Test form submission with valid data
print('\n--- Testing Beneficiary Edit Form Submission ---')
response = client.post('/accounts/beneficiary/1/', {
    'action': 'edit_beneficiary',
    'first_name': 'Updated First Name',
    'last_name': 'Updated Last Name',
    'gender': 'M',
    'date_of_birth': '2010-05-15',
    'admission_date': '2023-09-01',
    'residence_type': 'Boarding',
    'profile_picture': '',
}, HTTP_HOST='localhost')
print(f'Edit POST status: {response.status_code}')
if response.status_code == 302:
    print('✓ Beneficiary edit successful, redirecting...')
    # Check if the changes were saved
    response = client.get('/accounts/beneficiary/1/', HTTP_HOST='localhost')
    content = response.content.decode()
    if 'Updated First Name' in content and 'Updated Last Name' in content:
        print('✓ Updated name appears in preview page')
    else:
        print('✗ Updated name not found in preview page')
else:
    print(f'✗ Error editing beneficiary: {response.status_code}')
    print(f'Content: {response.content.decode()[:500]}')

# Test 3: Test form validation with missing required fields
print('\n--- Testing Form Validation ---')
response = client.post('/accounts/beneficiary/1/', {
    'action': 'edit_beneficiary',
    'first_name': '',  # Missing required field
    'last_name': 'Test Last',
}, HTTP_HOST='localhost')
print(f'Validation test POST status: {response.status_code}')
if response.status_code == 200:
    content = response.content.decode()
    if 'This field is required' in content:
        print('✓ Form validation working - required fields enforced')
    else:
        print('✗ Form validation not working properly')
else:
    print(f'✗ Unexpected status code: {response.status_code}')

print('\n--- Beneficiary Edit Testing Complete ---')
