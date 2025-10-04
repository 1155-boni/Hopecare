from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from PIL import Image
import io

from .models import BroughtBy

class UserDetailsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'school_name', 'student_class', 'date_of_admission', 'time_of_admission', 'admission_number']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg rounded-pill'}),
            'gender': forms.Select(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'school_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'student_class': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'date_of_admission': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg rounded-pill'}),
            'time_of_admission': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-lg rounded-pill'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'admission_number': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
        }

class BroughtByForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg rounded-pill'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg rounded-pill'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg rounded-pill'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['email', 'password1', 'password2']:
                self.fields[field].required = True

    class Meta:
        model = BroughtBy
        fields = ['id_number', 'phone_number', 'first_name', 'middle_name', 'last_name', 'relationship']
        widgets = {
            'id_number': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('student', 'Student'), ('librarian', 'Librarian'), ('storekeeper', 'Storekeeper')])

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Remove badge field since it no longer exists in User model
        if 'badge' in self.fields:
            self.fields.pop('badge', None)

        # Add Bootstrap classes
        self.fields['first_name'].widget.attrs.update({'class': 'form-control form-control-lg rounded-pill'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control form-control-lg rounded-pill'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control form-control-lg'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_picture']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB max
                raise forms.ValidationError('Image file too large (max 5MB).')
        return profile_picture
