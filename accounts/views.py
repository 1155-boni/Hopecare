from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserCreationForm
from .models import User
from library.models import StudentBookRecord, SchoolRecord
from inventory.models import Stock

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home or dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def home(request):
    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role == 'librarian':
            return redirect('librarian_dashboard')
        elif request.user.role == 'storekeeper':
            return redirect('storekeeper_dashboard')
        elif request.user.role == 'admin' and request.user.email == 'admin@example.com':
            return redirect('admin_dashboard')
    return render(request, 'home.html', {'user': request.user})

def student_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('home')
    book_records = StudentBookRecord.objects.filter(student=request.user)
    school_records = SchoolRecord.objects.filter(student=request.user)
    context = {
        'book_records': book_records,
        'school_records': school_records,
        'badge': request.user.badge,
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
    if not request.user.is_authenticated or request.user.role != 'admin' or request.user.email != 'admin@example.com':
        return redirect('home')
    users = User.objects.all()
    book_records = StudentBookRecord.objects.all()
    school_records = SchoolRecord.objects.all()
    stocks = Stock.objects.all()
    context = {
        'users': users,
        'book_records': book_records,
        'school_records': school_records,
        'stocks': stocks,
    }
    return render(request, 'accounts/admin_dashboard.html', context)
