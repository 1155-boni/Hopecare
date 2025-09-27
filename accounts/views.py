from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from library.models import StudentBookRecord, SchoolRecord

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
