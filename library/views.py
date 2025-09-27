from django.shortcuts import render, redirect
from .forms import StudentBookRecordForm, SchoolRecordForm

def add_book_record(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('home')
    if request.method == 'POST':
        form = StudentBookRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.student = request.user
            record.save()
            return redirect('student_dashboard')
    else:
        form = StudentBookRecordForm()
    return render(request, 'library/add_book_record.html', {'form': form})

def add_school_record(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('home')
    if request.method == 'POST':
        form = SchoolRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.student = request.user
            record.save()
            return redirect('student_dashboard')
    else:
        form = SchoolRecordForm()
    return render(request, 'library/add_school_record.html', {'form': form})
