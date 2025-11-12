from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from .forms import UserProfileForm, BeneficiaryForm, MedicalRecordForm
from .models import User, AuditLog, Beneficiary, MedicalRecord, EmailVerificationCode
from inventory.models import Stock

import logging

logger = logging.getLogger(__name__)

# Removed signup and student_dashboard views as per user request

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        code = request.POST.get('code')
        action = request.POST.get('action')

        if action == 'send_code':
            # Step 1: Send verification code
            if not username or not email:
                messages.error(request, 'Please enter both username and email address.')
                return render(request, 'accounts/login.html', {'step': 'email'})

            try:
                user = User.objects.get(username=username, email=email)
                # Clean up expired codes for this user
                EmailVerificationCode.objects.filter(user=user, expires_at__lt=timezone.now()).delete()

                # Generate 6-digit code
                verification_code = ''.join(random.choices(string.digits, k=6))
                expires_at = timezone.now() + timedelta(minutes=10)

                # Save code
                EmailVerificationCode.objects.create(
                    user=user,
                    code=verification_code,
                    expires_at=expires_at
                )

                # Send email
                subject = 'Your Hopecare Login Code'
                message = f'Your verification code is: {verification_code}\n\nThis code will expire in 10 minutes.'
                from_email = settings.DEFAULT_FROM_EMAIL
                send_mail(subject, message, from_email, [email])

                messages.success(request, 'Verification code sent to your email.')
                return render(request, 'accounts/login.html', {'step': 'code', 'email': email, 'username': username})

            except User.DoesNotExist:
                messages.error(request, 'No account found with this username and email combination.')
                return render(request, 'accounts/login.html', {'step': 'email'})

        elif action == 'verify_code':
            # Step 2: Verify code and login
            if not username or not email or not code:
                messages.error(request, 'Please enter username, email, and verification code.')
                return render(request, 'accounts/login.html', {'step': 'code', 'email': email, 'username': username})

            try:
                user = User.objects.get(username=username, email=email)
                # Find valid code
                verification_code = EmailVerificationCode.objects.filter(
                    user=user,
                    code=code,
                    expires_at__gt=timezone.now()
                ).first()

                if verification_code:
                    # Code is valid, log in user
                    login(request, user)
                    # Clean up used code
                    verification_code.delete()
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid or expired verification code.')
                    return render(request, 'accounts/login.html', {'step': 'code', 'email': email, 'username': username})

            except User.DoesNotExist:
                messages.error(request, 'No account found with this username and email combination.')
                return render(request, 'accounts/login.html', {'step': 'email'})

    # Default: show username and email input
    return render(request, 'accounts/login.html', {'step': 'email'})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            AuditLog.objects.create(user=request.user, action='Update Profile', details='User updated profile')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user, user=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

def welfare_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'welfare':
        return redirect('home')
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST)
        if form.is_valid():
            beneficiary = form.save(commit=False)
            beneficiary.added_by = request.user
            beneficiary.save()
            messages.success(request, f'Beneficiary "{beneficiary.first_name} {beneficiary.last_name}" added successfully.')
            AuditLog.objects.create(user=request.user, action='Add Beneficiary', details=f'Added beneficiary {beneficiary.first_name} {beneficiary.last_name}')
            return redirect('welfare_dashboard')
    else:
        form = BeneficiaryForm()
    beneficiaries = Beneficiary.objects.all()
    context = {
        'form': form,
        'beneficiaries': beneficiaries,
    }
    return render(request, 'accounts/welfare_dashboard.html', context)

def storekeeper_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'storekeeper':
        return redirect('home')
    stocks = Stock.objects.all()
    low_stock = stocks.filter(quantity__lt=10)
    expiring = stocks.filter(item__expiry_date__lt=timezone.now() + timedelta(days=30))
    context = {
        'stocks': stocks,
        'low_stock': low_stock,
        'expiring': expiring,
    }
    return render(request, 'accounts/storekeeper_dashboard.html', context)

def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('home')
    users = User.objects.all()
    stocks = Stock.objects.all()
    low_stock = stocks.filter(quantity__lt=10)
    expiring = stocks.filter(item__expiry_date__lt=timezone.now() + timedelta(days=30))
    context = {
        'users': users,
        'stocks': stocks,
        'low_stock': low_stock,
        'expiring': expiring,
    }
    return render(request, 'accounts/admin_dashboard.html', context)



@login_required
def delete_user(request, user_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('home')
    user_to_delete = User.objects.get(id=user_id)
    if user_to_delete == request.user or user_to_delete.is_superuser:
        messages.error(request, 'You cannot delete this user.')
        return redirect('admin_dashboard')
    if request.method == 'POST':
        AuditLog.objects.create(user=request.user, action='Delete User', details=f'Deleted user {user_to_delete.email}')
        user_to_delete.delete()
        messages.success(request, f'User {user_to_delete.email} has been deleted successfully.')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

@login_required
def delete_profile(request):
    if request.method == 'POST':
        AuditLog.objects.create(user=request.user, action='Delete Account', details='User deleted their account')
        request.user.delete()
        logout(request)
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    else:
        return redirect('profile')

def preview_beneficiary(request, beneficiary_id):
    if not request.user.is_authenticated or request.user.role != 'welfare':
        return redirect('home')
    try:
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    except Beneficiary.DoesNotExist:
        messages.error(request, 'Beneficiary not found.')
        return redirect('welfare_dashboard')

    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        if record_id:
            # Handle inline editing
            try:
                medical_record = MedicalRecord.objects.get(id=record_id, beneficiary=beneficiary)
                form = MedicalRecordForm(request.POST, request.FILES, instance=medical_record)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Medical record updated successfully.')
                    AuditLog.objects.create(user=request.user, action='Edit Medical Record', details=f'Updated medical record for {beneficiary.first_name} {beneficiary.last_name}')
                    return redirect('preview_beneficiary', beneficiary_id=beneficiary_id)
            except MedicalRecord.DoesNotExist:
                messages.error(request, 'Medical record not found.')
                return redirect('preview_beneficiary', beneficiary_id=beneficiary_id)
        elif request.POST.get('action') == 'edit_beneficiary':
            beneficiary_form = BeneficiaryForm(request.POST, instance=beneficiary)
            if beneficiary_form.is_valid():
                beneficiary_form.save()
                messages.success(request, 'Beneficiary information updated successfully.')
                AuditLog.objects.create(user=request.user, action='Edit Beneficiary', details=f'Updated beneficiary {beneficiary.first_name} {beneficiary.last_name}')
                return redirect('preview_beneficiary', beneficiary_id=beneficiary_id)
            else:
                form = MedicalRecordForm()
                medical_records = MedicalRecord.objects.filter(beneficiary=beneficiary)
                context = {
                    'beneficiary': beneficiary,
                    'form': form,
                    'beneficiary_form': beneficiary_form,
                    'medical_records': medical_records,
                }
                return render(request, 'accounts/preview_beneficiary.html', context)
        else:
            # Handle adding new record
            form = MedicalRecordForm(request.POST, request.FILES)
            if form.is_valid():
                medical_record = form.save(commit=False)
                medical_record.beneficiary = beneficiary
                medical_record.created_by = request.user
                medical_record.save()
                messages.success(request, 'Medical record added successfully.')
                AuditLog.objects.create(user=request.user, action='Add Medical Record', details=f'Added medical record for {beneficiary.first_name} {beneficiary.last_name}')
                return redirect('preview_beneficiary', beneficiary_id=beneficiary_id)
    else:
        form = MedicalRecordForm()

    medical_records = MedicalRecord.objects.filter(beneficiary=beneficiary)
    context = {
        'beneficiary': beneficiary,
        'form': form,
        'medical_records': medical_records,
    }
    return render(request, 'accounts/preview_beneficiary.html', context)

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html', {'user': request.user})

@login_required
def medical_records_list(request, beneficiary_id):
    if not request.user.is_authenticated or request.user.role != 'welfare':
        return redirect('home')
    try:
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    except Beneficiary.DoesNotExist:
        messages.error(request, 'Beneficiary not found.')
        return redirect('welfare_dashboard')

    medical_records = MedicalRecord.objects.filter(beneficiary=beneficiary)
    context = {
        'beneficiary': beneficiary,
        'medical_records': medical_records,
    }
    return render(request, 'accounts/medical_records_list.html', context)

@login_required
def add_medical_record(request, beneficiary_id):
    if not request.user.is_authenticated or request.user.role != 'welfare':
        return redirect('home')
    try:
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    except Beneficiary.DoesNotExist:
        messages.error(request, 'Beneficiary not found.')
        return redirect('welfare_dashboard')

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.beneficiary = beneficiary
            medical_record.created_by = request.user
            medical_record.save()
            messages.success(request, 'Medical record added successfully.')
            AuditLog.objects.create(user=request.user, action='Add Medical Record', details=f'Added medical record for {beneficiary.first_name} {beneficiary.last_name}')
            return redirect('medical_records_list', beneficiary_id=beneficiary_id)
    else:
        form = MedicalRecordForm()
    context = {
        'form': form,
        'beneficiary': beneficiary,
    }
    return render(request, 'accounts/medical_record_form.html', context)

@login_required
def edit_medical_record(request, beneficiary_id, record_id):
    if not request.user.is_authenticated or request.user.role != 'welfare':
        return redirect('home')
    try:
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
        medical_record = MedicalRecord.objects.get(id=record_id, beneficiary=beneficiary)
    except (Beneficiary.DoesNotExist, MedicalRecord.DoesNotExist):
        messages.error(request, 'Beneficiary or medical record not found.')
        return redirect('welfare_dashboard')

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES, instance=medical_record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medical record updated successfully.')
            AuditLog.objects.create(user=request.user, action='Edit Medical Record', details=f'Updated medical record for {beneficiary.first_name} {beneficiary.last_name}')
            return redirect('medical_records_list', beneficiary_id=beneficiary_id)
    else:
        form = MedicalRecordForm(instance=medical_record)
    context = {
        'form': form,
        'beneficiary': beneficiary,
        'medical_record': medical_record,
    }
    return render(request, 'accounts/medical_record_form.html', context)

@login_required
def delete_medical_record(request, beneficiary_id, record_id):
    if not request.user.is_authenticated or request.user.role != 'welfare':
        return redirect('home')
    try:
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
        medical_record = MedicalRecord.objects.get(id=record_id, beneficiary=beneficiary)
    except (Beneficiary.DoesNotExist, MedicalRecord.DoesNotExist):
        messages.error(request, 'Beneficiary or medical record not found.')
        return redirect('welfare_dashboard')

    if request.method == 'POST':
        AuditLog.objects.create(user=request.user, action='Delete Medical Record', details=f'Deleted medical record for {beneficiary.first_name} {beneficiary.last_name}')
        medical_record.delete()
        messages.success(request, 'Medical record deleted successfully.')
        return redirect('medical_records_list', beneficiary_id=beneficiary_id)

    context = {
        'beneficiary': beneficiary,
        'medical_record': medical_record,
    }
    return render(request, 'accounts/delete_medical_record.html', context)
