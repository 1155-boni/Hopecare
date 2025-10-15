from django.urls import path
from . import views

urlpatterns = [
    path('add-book-library/', views.add_book, name='add_book'),
]
