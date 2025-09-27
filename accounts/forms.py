from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from PIL import Image
import io

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('student', 'Student'), ('librarian', 'Librarian'), ('storekeeper', 'Storekeeper')])

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role not in ['librarian', 'admin']:
            self.fields.pop('badge', None)

        # Add Bootstrap classes
        self.fields['first_name'].widget.attrs.update({'class': 'form-control form-control-lg rounded-pill'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control form-control-lg rounded-pill'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control form-control-lg'})
        if 'badge' in self.fields:
            self.fields['badge'].widget.attrs.update({'class': 'form-select form-select-lg rounded-pill'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_picture', 'badge']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB max
                raise forms.ValidationError('Image file too large (max 5MB).')
        return profile_picture
