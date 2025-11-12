#!/usr/bin/env python
"""
Test script for Medical Records functionality
"""
import os
import sys
import django
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hopecare_project.settings')
django.setup()

from accounts.models import Beneficiary, MedicalRecord, BroughtBy

User = get_user_model()

def create_test_image():
    """Create a test image file for upload testing"""
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile("test_image.jpg", img_io.getvalue(), content_type="image/jpeg")

def test_medical_records():
    print("Testing Medical Records Functionality...")

    # Create test client
    client = Client()

    # Get or create welfare user
    try:
        welfare_user = User.objects.get(email='welfare@hopecare.com')
        print("✓ Using existing welfare user")
    except User.DoesNotExist:
        welfare_user = User.objects.create_user(
            email='welfare@hopecare.com',
            password='password123',
            first_name='Welfare',
            last_name='User',
            role='welfare'
        )
        print("✓ Created welfare user")

    # Login
    login_success = client.login(email='welfare@hopecare.com', password='welfare@123')
    if login_success:
        print("✓ Welfare user logged in successfully")
    else:
        print("✗ Failed to login welfare user")
        return False

    # Get existing beneficiary or create one
    try:
        beneficiary = Beneficiary.objects.get(admission_number='TEST-001')
        print("✓ Using existing beneficiary")
    except Beneficiary.DoesNotExist:
        # Create brought_by first
        brought_by = BroughtBy.objects.create(
            name='Test Parent',
            contact='1234567890',
            id_number='ID123',
            relationship='Parent'
        )

        beneficiary = Beneficiary.objects.create(
            first_name='Test',
            last_name='Beneficiary',
            gender='male',
            date_of_birth='2010-01-01',
            date_of_admission='2024-01-01',
            time_of_admission='10:00:00',
            admission_number='TEST-001',
            residence_type='temporary',
            brought_by=brought_by,
            added_by=welfare_user
        )
        print("✓ Created test beneficiary")

    # Test 1: Access medical records list
    response = client.get(f'/accounts/beneficiary/{beneficiary.id}/medical-records/')
    if response.status_code == 200:
        print("✓ Medical records list page accessible")
    else:
        print(f"✗ Failed to access medical records list: {response.status_code}")
        return False

    # Test 2: Access add medical record form
    response = client.get(f'/accounts/beneficiary/{beneficiary.id}/medical-records/add/')
    if response.status_code == 200:
        print("✓ Add medical record form accessible")
    else:
        print(f"✗ Failed to access add form: {response.status_code}")
        return False

    # Test 3: Create medical record with file upload
    test_image = create_test_image()
    medical_data = {
        'date': '2024-10-15',
        'diagnosis': 'Common Cold',
        'treatment': 'Rest and fluids',
        'doctor_name': 'Dr. Smith',
        'notes': 'Patient showing improvement'
    }

    response = client.post(
        f'/accounts/beneficiary/{beneficiary.id}/medical-records/add/',
        data=medical_data,
        files={'medical_documents': test_image}
    )

    if response.status_code == 302:  # Redirect after success
        print("✓ Medical record created successfully with file upload")
    else:
        print(f"✗ Failed to create medical record: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        return False

    # Verify record was created
    medical_records = MedicalRecord.objects.filter(beneficiary=beneficiary)
    if medical_records.exists():
        record = medical_records.first()
        print("✓ Medical record saved to database")
        print(f"  - Diagnosis: {record.diagnosis}")
        print(f"  - Doctor: {record.doctor_name}")
        print(f"  - Has document: {bool(record.medical_documents)}")
    else:
        print("✗ Medical record not found in database")
        return False

    # Test 4: Edit medical record
    edit_data = {
        'date': '2024-10-16',
        'diagnosis': 'Common Cold - Improved',
        'treatment': 'Rest and fluids, medication prescribed',
        'doctor_name': 'Dr. Smith',
        'notes': 'Patient recovering well'
    }

    response = client.post(
        f'/accounts/beneficiary/{beneficiary.id}/medical-records/{record.id}/edit/',
        data=edit_data
    )

    if response.status_code == 302:
        print("✓ Medical record updated successfully")
    else:
        print(f"✗ Failed to update medical record: {response.status_code}")
        return False

    # Verify update
    record.refresh_from_db()
    if record.diagnosis == 'Common Cold - Improved':
        print("✓ Medical record update verified")
    else:
        print("✗ Medical record update not reflected")
        return False

    # Test 5: Access delete confirmation page
    response = client.get(f'/accounts/beneficiary/{beneficiary.id}/medical-records/{record.id}/delete/')
    if response.status_code == 200:
        print("✓ Delete confirmation page accessible")
    else:
        print(f"✗ Failed to access delete page: {response.status_code}")
        return False

    # Test 6: Delete medical record
    response = client.post(f'/accounts/beneficiary/{beneficiary.id}/medical-records/{record.id}/delete/')
    if response.status_code == 302:
        print("✓ Medical record deleted successfully")
    else:
        print(f"✗ Failed to delete medical record: {response.status_code}")
        return False

    # Verify deletion
    if not MedicalRecord.objects.filter(id=record.id).exists():
        print("✓ Medical record deletion verified")
    else:
        print("✗ Medical record still exists after deletion")
        return False

    # Test 7: Access control - try with non-welfare user
    try:
        admin_user = User.objects.get(role='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            email='admin@hopecare.com',
            password='password123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )

    client.logout()
    login_success = client.login(email='admin@hopecare.com', password='admin@123')
    if login_success:
        print("✓ Admin user logged in for access control test")
    else:
        print("✗ Failed to login admin user")
        return False

    # Try to access medical records (should be denied)
    response = client.get(f'/accounts/beneficiary/{beneficiary.id}/medical-records/')
    if response.status_code == 302:  # Should redirect to home
        print("✓ Access control working - non-welfare user redirected")
    else:
        print(f"✗ Access control failed - non-welfare user got {response.status_code}")
        return False

    print("\n🎉 All Medical Records tests passed!")
    return True

if __name__ == '__main__':
    success = test_medical_records()
    if success:
        print("\n✅ Medical Records functionality is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Medical Records functionality has issues!")
        sys.exit(1)
