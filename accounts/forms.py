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
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_picture', 'badge']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB max
                raise forms.ValidationError('Image file too large (max 5MB).')
            img = Image.open(profile_picture)
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size, Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=90)
                profile_picture.seek(0)
        return profile_picture
