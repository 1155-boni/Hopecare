#!/usr/bin/env python
import os
import sys
import django
from datetime import date, time

# Add the project directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hopecare_project.settings')

# Setup Django
django.setup()

from accounts.models import User, Beneficiary, BroughtBy
from accounts.forms import BeneficiaryForm
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_beneficiary_form():
    print("Testing Beneficiary Form Submission...")

    # Create a test user
    try:
        user = User.objects.get(email='welfare@hopecare.com')
        print(f"Using existing welfare user: {user.email}")
    except User.DoesNotExist:
        print("Welfare user not found. Please run create_superusers.py first.")
        return

    # Test form data
    form_data = {
        'first_name': 'John',
        'middle_name': 'Michael',
        'last_name': 'Doe',
        'gender': 'male',
        'date_of_birth': '2010-05-15',
        'admission_number': 'TEST-001',
        'date_of_admission': '2024-10-15',
        'time_of_admission': '09:30',
        'brought_by_name': 'Jane Doe',
        'brought_by_contact': '0712345678',
        'brought_by_id_number': '12345678',
        'brought_by_relationship': 'Mother',
        'school_name': 'Hope Primary School',
        'student_class': 'Grade 5',
        'residence_type': 'temporary',
        'has_relatives': True,
        'relatives_count': 2,
        'has_siblings': True,
        'siblings_count': 1,
    }

    # Create form instance
    form = BeneficiaryForm(data=form_data)

    if form.is_valid():
        print("✓ Form is valid")
        # Save the beneficiary
        beneficiary = form.save(commit=False)
        beneficiary.added_by = user
        beneficiary.save()
        print(f"✓ Beneficiary saved: {beneficiary.first_name} {beneficiary.last_name}")
        print(f"  - Admission Number: {beneficiary.admission_number}")
        print(f"  - Age: {beneficiary.age}")
        print(f"  - School: {beneficiary.school_name}")
        print(f"  - Residence: {beneficiary.residence_type}")

        # Check BroughtBy
        brought_by = beneficiary.brought_by
        print(f"  - Brought By: {brought_by.name} ({brought_by.relationship})")

        return beneficiary
    else:
        print("✗ Form is invalid")
        for field, errors in form.errors.items():
            print(f"  - {field}: {', '.join(errors)}")
        return None

def test_beneficiary_display():
    print("\nTesting Beneficiary Display...")

    beneficiaries = Beneficiary.objects.all()
    if beneficiaries.exists():
        print(f"✓ Found {beneficiaries.count()} beneficiaries")
        for beneficiary in beneficiaries:
            print(f"  - {beneficiary.first_name} {beneficiary.last_name} ({beneficiary.admission_number})")
    else:
        print("✗ No beneficiaries found")

def test_preview_beneficiary():
    print("\nTesting Beneficiary Preview...")

    try:
        beneficiary = Beneficiary.objects.first()
        if beneficiary:
            print(f"✓ Preview beneficiary: {beneficiary.first_name} {beneficiary.last_name}")
            print(f"  - Full Name: {beneficiary.first_name} {beneficiary.middle_name or ''} {beneficiary.last_name}")
            print(f"  - Gender: {beneficiary.gender}")
            print(f"  - DOB: {beneficiary.date_of_birth}")
            print(f"  - Age: {beneficiary.age}")
            print(f"  - Admission: {beneficiary.admission_number} on {beneficiary.date_of_admission}")
            print(f"  - School: {beneficiary.school_name}, Class: {beneficiary.student_class}")
            print(f"  - Residence: {beneficiary.residence_type}")
            print(f"  - Relatives: {'Yes' if beneficiary.has_relatives else 'No'} ({beneficiary.relatives_count})")
            print(f"  - Siblings: {'Yes' if beneficiary.has_siblings else 'No'} ({beneficiary.siblings_count})")
            print(f"  - Brought By: {beneficiary.brought_by.name}")
        else:
            print("✗ No beneficiary to preview")
    except Exception as e:
        print(f"✗ Error previewing beneficiary: {e}")

if __name__ == '__main__':
    # Run tests
    beneficiary = test_beneficiary_form()
    test_beneficiary_display()
    test_preview_beneficiary()

    print("\nTest completed!")
