from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .forms import CustomUserCreationForm, UserProfileForm, UserDetailsForm
from .models import User, AuditLog
from library.models import StudentBookRecord, SchoolRecord
from inventory.models import Stock

import logging
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

logger = logging.getLogger(__name__)

from .forms import CustomUserCreationForm, UserProfileForm, UserDetailsForm, BroughtByForm

def signup(request):
    step = request.GET.get('step', '1')

    try:
        logger.debug(f"Signup view called with step: {step}")
        if step == '1':
            # Role selection step
            if request.method == 'POST':
                selected_role = request.POST.get('role')
                logger.debug(f"Selected role: {selected_role}")
                if selected_role:
                    request.session['selected_role'] = selected_role
                    if selected_role == 'student':
                        logger.debug("Redirecting to step 2 for student")
                        return redirect('/accounts/signup/?step=2')
                    else:
                        # For non-student roles, go directly to account creation
                        logger.debug("Redirecting to step 5 for non-student")
                        return redirect('/accounts/signup/?step=5')
            return render(request, 'accounts/role_selection.html')

        elif step == '2':
            # User details step (only for students)
            selected_role = request.session.get('selected_role')
            logger.debug(f"Session selected_role: {selected_role}")
            if not selected_role or selected_role != 'student':
                logger.debug("Redirecting to step 1 due to missing or invalid role")
                return redirect('/accounts/signup/?step=1')

            if request.method == 'POST':
                form = UserDetailsForm(request.POST)
                if form.is_valid():
                    logger.debug("UserDetailsForm is valid")
                    # Store user details in session
                    user_details = {
                        'first_name': form.cleaned_data['first_name'],
                        'middle_name': form.cleaned_data['middle_name'],
                        'last_name': form.cleaned_data['last_name'],
                        'date_of_birth': form.cleaned_data['date_of_birth'].strftime('%Y-%m-%d') if form.cleaned_data['date_of_birth'] else None,
                        'gender': form.cleaned_data['gender'],
                        'school_name': form.cleaned_data['school_name'],
                        'student_class': form.cleaned_data['student_class'],
                        'date_of_admission': form.cleaned_data['date_of_admission'].strftime('%Y-%m-%d') if form.cleaned_data['date_of_admission'] else None,
                        'time_of_admission': form.cleaned_data['time_of_admission'].strftime('%H:%M:%S') if form.cleaned_data['time_of_admission'] else None,
                        'admission_number': form.cleaned_data['admission_number'],
                    }
                    request.session['user_details'] = user_details
                    logger.debug(f"User details stored in session: {user_details}")
                    return redirect('/accounts/signup/?step=3')
                else:
                    logger.debug(f"UserDetailsForm errors: {form.errors}")
            else:
                form = UserDetailsForm()
            return render(request, 'accounts/user_details.html', {'form': form})

        elif step == '3':
            # Write Brought By details step (only for students)
            user_details = request.session.get('user_details')
            selected_role = request.session.get('selected_role')
            if not user_details or selected_role != 'student':
                return redirect('/accounts/signup/?step=1')

            if request.method == 'POST':
                form = BroughtByForm(request.POST)
                if form.is_valid():
                    brought_by_data = form.cleaned_data
                    # Create the user account
                    user = User.objects.create_user(
                        email=brought_by_data['email'],
                        password=brought_by_data['password1'],
                        first_name=user_details['first_name'],
                        middle_name=user_details['middle_name'],
                        last_name=user_details['last_name'],
                        date_of_birth=user_details['date_of_birth'],
                        gender=user_details['gender'],
                        school_name=user_details['school_name'],
                        student_class=user_details['student_class'],
                        date_of_admission=user_details['date_of_admission'],
                        time_of_admission=user_details['time_of_admission'],
                        admission_number=user_details['admission_number'],
                        role=selected_role
                    )
                    # Save brought_by data
                    BroughtBy.objects.create(
                        user=user,
                        id_number=brought_by_data.get('id_number'),
                        phone_number=brought_by_data.get('phone_number'),
                        first_name=brought_by_data.get('first_name'),
                        middle_name=brought_by_data.get('middle_name'),
                        last_name=brought_by_data.get('last_name'),
                        relationship=brought_by_data.get('relationship'),
                    )
                    # Clear session data
                    del request.session['user_details']
                    del request.session['selected_role']
                    login(request, user)
                    return redirect('home')
            else:
                form = BroughtByForm()
            return render(request, 'accounts/brought_by.html', {'form': form, 'step_name': 'Brought By'})

        elif step == '4':
            # Account creation for students
            user_details = request.session.get('user_details')
            brought_by_data = request.session.get('brought_by')
            selected_role = request.session.get('selected_role')
            if not user_details or not brought_by_data or selected_role != 'student':
                return redirect('/accounts/signup/?step=1')

            if request.method == 'POST':
                form = CustomUserCreationForm(request.POST)
                if form.is_valid():
                    user = form.save(commit=False)
                    # Set the user details from session
                    user.first_name = user_details['first_name']
                    user.middle_name = user_details['middle_name']
                    user.last_name = user_details['last_name']
                    user.date_of_birth = user_details['date_of_birth']
                    user.gender = user_details['gender']
                    user.school_name = user_details['school_name']
                    user.student_class = user_details['student_class']
                    user.date_of_admission = user_details['date_of_admission']
                    user.admission_number = user_details['admission_number']
                    user.role = selected_role
                    user.save()
                    # Save brought_by data
                    from .models import BroughtBy
                    BroughtBy.objects.create(
                        user=user,
                        id_number=brought_by_data.get('id_number'),
                        phone_number=brought_by_data.get('phone_number'),
                        first_name=brought_by_data.get('first_name'),
                        middle_name=brought_by_data.get('middle_name'),
                        last_name=brought_by_data.get('last_name'),
                        relationship=brought_by_data.get('relationship'),
                    )
                    # Clear session data
                    del request.session['user_details']
                    del request.session['brought_by']
                    del request.session['selected_role']
                    login(request, user)
                    return redirect('home')
            else:
                form = CustomUserCreationForm()
            return render(request, 'accounts/signup.html', {'form': form})

        elif step == '5':
            # Account creation for non-student roles
            selected_role = request.session.get('selected_role')
            if not selected_role or selected_role == 'student':
                return redirect('/accounts/signup/?step=1')

            if request.method == 'POST':
                form = CustomUserCreationForm(request.POST)
                if form.is_valid():
                    user = form.save(commit=False)
                    user.role = selected_role
                    user.save()
                    # Clear session data
                    del request.session['selected_role']
                    login(request, user)
                    return redirect('home')
            else:
                form = CustomUserCreationForm()
            return render(request, 'accounts/signup.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in signup view step {step}: {e}", exc_info=True)
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('/accounts/signup/?step=1')

def login_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        user = None
        if name and password:
            # Try to find user by first_name, middle_name, or last_name (case-insensitive)
            try:
                user = User.objects.get(
                    Q(first_name__iexact=name) | Q(middle_name__iexact=name) | Q(last_name__iexact=name)
                )
                if not user.check_password(password):
                    user = None
            except User.DoesNotExist:
                user = None
        if user is not None:
            login(request, user)
            AuditLog.objects.create(user=user, action='Login', details='User logged in')
            return redirect('home')
        else:
            messages.error(request, 'Invalid name or password.')
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
