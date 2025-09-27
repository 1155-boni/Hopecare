from django import forms
from .models import StudentBookRecord, SchoolRecord, Book

class StudentBookRecordForm(forms.ModelForm):
    class Meta:
        model = StudentBookRecord
        fields = ['book', 'custom_title', 'date_read', 'notes']
        widgets = {
            'date_read': forms.DateInput(attrs={'type': 'date'}),
            'custom_title': forms.TextInput(attrs={'placeholder': 'Enter custom book title if not in library'}),
        }

class SchoolRecordForm(forms.ModelForm):
    class Meta:
        model = SchoolRecord
        fields = ['subject', 'grade', 'semester', 'year']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
        }
