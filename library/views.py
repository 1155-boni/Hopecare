from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Book
from .forms import BookForm
from accounts.models import User
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from datetime import datetime

@login_required
def add_book(request):
    if request.user.role != 'welfare':
        return redirect('home')
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('welfare_dashboard')
    else:
        form = BookForm()
    return render(request, 'library/add_book.html', {'form': form})



@login_required
def generate_books_pdf(request):
    if request.user.role not in ['welfare', 'admin']:
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
