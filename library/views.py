from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Book, StudentBookRecord, SchoolRecord
from .forms import BookForm, StudentBookRecordForm, SchoolRecordForm
from accounts.models import User
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from datetime import datetime

@login_required
def add_book(request):
    if request.user.role != 'librarian':
        return redirect('home')
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('librarian_dashboard')
    else:
        form = BookForm()
    return render(request, 'library/add_book.html', {'form': form})

@login_required
def add_book_record(request):
    if request.user.role != 'student':
        return redirect('home')
    if request.method == 'POST':
        form = StudentBookRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.student = request.user
            record.save()
            messages.success(request, 'Book record added successfully!')
            return redirect('student_dashboard')
    else:
        form = StudentBookRecordForm()
    return render(request, 'library/add_book_record.html', {'form': form})

@login_required
def add_school_record(request):
    if request.user.role != 'student':
        return redirect('home')
    if request.method == 'POST':
        form = SchoolRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.student = request.user
            record.save()
            messages.success(request, 'School record added successfully!')
            return redirect('student_dashboard')
    else:
        form = SchoolRecordForm()
    return render(request, 'library/add_school_record.html', {'form': form})

@login_required
def generate_books_pdf(request):
    if request.user.role not in ['librarian', 'admin']:
        return redirect('home')
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.drawString(100, height - 100, "Hopecare Library - Books Report")
    p.drawString(100, height - 120, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    y = height - 150
    books = Book.objects.all()
    for book in books:
        p.drawString(100, y, f"Title: {book.title}")
        p.drawString(100, y - 20, f"Author: {book.author}")
        p.drawString(100, y - 40, f"ISBN: {book.isbn}")
        y -= 80
        if y < 100:
            p.showPage()
            y = height - 50
    
    p.save()
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="books_report.pdf"'
    return response
