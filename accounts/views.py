from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserCreationForm, UserProfileForm, UserDetailsForm
from .models import User, AuditLog
from library.models import StudentBookRecord, SchoolRecord
from inventory.models import Stock

def signup(request):
    step = request.GET.get('step', '1')

    if step == '1':
        if request.method == 'POST':
            form = UserDetailsForm(request.POST)
            if form.is_valid():
                # Store user details in session
                request.session['user_details'] = {
                    'first_name': form.cleaned_data['first_name'],
                    'middle_name': form.cleaned_data['middle_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'date_of_birth': form.cleaned_data['date_of_birth'].isoformat() if form.cleaned_data['date_of_birth'] else None,
                    'date_of_admission': form.cleaned_data['date_of_admission'].isoformat() if form.cleaned_data['date_of_admission'] else None,
                    'admission_number': form.cleaned_data['admission_number'],
                }
                return redirect('signup?step=2')
        else:
            form = UserDetailsForm()
        return render(request, 'accounts/user_details.html', {'form': form})

    elif step == '2':
        user_details = request.session.get('user_details')
        if not user_details:
            return redirect('signup?step=1')

        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                # Set the user details from session
                user.first_name = user_details['first_name']
                user.middle_name = user_details['middle_name']
                user.last_name = user_details['last_name']
                user.date_of_birth = user_details['date_of_birth']
                user.date_of_admission = user_details['date_of_admission']
                user.admission_number = user_details['admission_number']
                user.save()
                # Clear session data
                del request.session['user_details']
                login(request, user)
                return redirect('home')
        else:
            form = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            AuditLog.objects.create(user=user, action='Login', details='User logged in')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    AuditLog.objects.create(user=request.user, action='Logout', details='User logged out')
    logout(request)
    return redirect('home')

def home(request):
    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role == 'librarian':
            return redirect('librarian_dashboard')
        elif request.user.role == 'storekeeper':
            return redirect('storekeeper_dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
    return render(request, 'home.html', {'user': request.user})

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

def student_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('home')
    book_records = StudentBookRecord.objects.filter(student=request.user)
    school_records = SchoolRecord.objects.filter(student=request.user)
    progress_width = min(book_records.count() * 10, 100)  # Cap at 100%
    context = {
        'book_records': book_records,
        'school_records': school_records,
        'badge': request.user.badge,
        'progress_width': progress_width,
    }
    return render(request, 'accounts/student_dashboard.html', context)

def librarian_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'librarian':
        return redirect('home')
    students = User.objects.filter(role='student')
    book_records = StudentBookRecord.objects.all()
    context = {
        'students': students,
        'book_records': book_records,
    }
    return render(request, 'accounts/librarian_dashboard.html', context)

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
