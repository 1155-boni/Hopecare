from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .forms import UserProfileForm
from .models import User, AuditLog
from library.models import StudentBookRecord, SchoolRecord
from inventory.models import Stock

import logging

logger = logging.getLogger(__name__)

# Removed signup and student_dashboard views as per user request

def login_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        user = None
        # Try to find user by username or email (phone_number field does not exist)
        try:
            user_obj = User.objects.get(Q(username=name) | Q(email=name))
            user = authenticate(request, username=user_obj.email, password=password)
        except User.DoesNotExist:
            user = None
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

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
    if not request.user.is_authenticated or request.user.role != 'librarian':
        return redirect('home')
    students = User.objects.filter(role='student')
    book_records = StudentBookRecord.objects.all()
    context = {
        'students': students,
        'book_records': book_records,
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
    students = User.objects.filter(role='student')
    book_records = StudentBookRecord.objects.all()
    school_records = SchoolRecord.objects.all()
    stocks = Stock.objects.all()
    low_stock = stocks.filter(quantity__lt=10)
    expiring = stocks.filter(item__expiry_date__lt=timezone.now() + timedelta(days=30))
    context = {
        'users': users,
        'students': students,
        'book_records': book_records,
        'school_records': school_records,
        'stocks': stocks,
        'low_stock': low_stock,
        'expiring': expiring,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

def award_badge(request, student_id):
    if not request.user.is_authenticated or request.user.role not in ['librarian', 'admin']:
        return redirect('home')
    if request.method == 'POST':
        badge = request.POST.get('badge')
        student = User.objects.get(id=student_id)
        student.badge = badge
        student.save()
        AuditLog.objects.create(user=request.user, action='Award Badge', details=f'Awarded {badge} to {student.email}')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

def preview_student(request, student_id):
    if not request.user.is_authenticated or request.user.role not in ['librarian', 'admin']:
        return redirect('home')
    student = User.objects.get(id=student_id)
    book_records = StudentBookRecord.objects.filter(student=student)
    school_records = SchoolRecord.objects.filter(student=student)
    context = {
        'student': student,
        'book_records': book_records,
        'school_records': school_records,
    }
    return render(request, 'accounts/preview_student.html', context)

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

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html', {'user': request.user})
