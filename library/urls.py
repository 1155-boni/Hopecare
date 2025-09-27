from django.urls import path
from . import views

urlpatterns = [
    path('add-book/', views.add_book_record, name='add_book_record'),
    path('add-school/', views.add_school_record, name='add_school_record'),
    path('add-book-library/', views.add_book, name='add_book'),
]
