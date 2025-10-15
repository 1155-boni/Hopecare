from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Beneficiary
from PIL import Image
import io
    
class UserDetailsForm(forms.ModelForm):
    
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg rounded-pill'}),
            'gender': forms.Select(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

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

class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = ['name', 'contact_info', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'address': forms.Textarea(attrs={'class': 'form-control form-control-lg rounded-pill', 'rows': 3}),
        }
