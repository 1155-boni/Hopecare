from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Beneficiary, BroughtBy, MedicalRecord
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

class BroughtByForm(forms.ModelForm):
    class Meta:
        model = BroughtBy
        fields = ['name', 'contact', 'id_number', 'relationship']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'contact': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
        }

class BeneficiaryForm(forms.ModelForm):
    # Additional fields for inline form
    brought_by_name = forms.CharField(max_length=255, label="Brought By Name")
    brought_by_contact = forms.CharField(max_length=255, required=False, label="Brought By Contact")
    brought_by_id_number = forms.CharField(max_length=100, required=False, label="Brought By ID Number")
    brought_by_relationship = forms.CharField(max_length=100, required=False, label="Relationship")

    class Meta:
        model = Beneficiary
        fields = [
            'first_name', 'middle_name', 'last_name', 'gender', 'date_of_birth',
            'date_of_admission', 'time_of_admission', 'admission_number',
            'school_name', 'student_class', 'residence_type',
            'has_relatives', 'relatives_count', 'has_siblings', 'siblings_count',
            'profile_picture', 'documents', 'brought_by'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'gender': forms.Select(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg rounded-pill'}),
            'date_of_admission': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg rounded-pill'}),
            'time_of_admission': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-lg rounded-pill'}),
            'admission_number': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'school_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'student_class': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'residence_type': forms.Select(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'has_relatives': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'relatives_count': forms.NumberInput(attrs={'class': 'form-control form-control-lg rounded-pill', 'min': '0'}),
            'has_siblings': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'siblings_count': forms.NumberInput(attrs={'class': 'form-control form-control-lg rounded-pill', 'min': '0'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control form-control-lg'}),
            'documents': forms.FileInput(attrs={'class': 'form-control form-control-lg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For editing, remove brought_by fields
        if self.instance and self.instance.pk:
            self.fields.pop('brought_by_name', None)
            self.fields.pop('brought_by_contact', None)
            self.fields.pop('brought_by_id_number', None)
            self.fields.pop('brought_by_relationship', None)
            # Make relatives_count and siblings_count required when checkboxes are checked
            if self.instance.has_relatives:
                self.fields['relatives_count'].required = True
            if self.instance.has_siblings:
                self.fields['siblings_count'].required = True

    def save(self, commit=True):
        # Only create BroughtBy for new instances
        if not self.instance.pk:
            # Create BroughtBy instance first
            brought_by = BroughtBy.objects.create(
                name=self.cleaned_data['brought_by_name'],
                contact=self.cleaned_data.get('brought_by_contact'),
                id_number=self.cleaned_data.get('brought_by_id_number'),
                relationship=self.cleaned_data.get('brought_by_relationship')
            )

            # Create Beneficiary instance
            beneficiary = super().save(commit=False)
            beneficiary.brought_by = brought_by
        else:
            # For editing, just save the beneficiary
            beneficiary = super().save(commit=False)

        if commit:
            beneficiary.save()
        return beneficiary

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['date', 'diagnosis', 'treatment', 'doctor_name', 'notes', 'medical_documents']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg rounded-pill'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control form-control-lg rounded-pill', 'rows': 3}),
            'treatment': forms.Textarea(attrs={'class': 'form-control form-control-lg rounded-pill', 'rows': 3}),
            'doctor_name': forms.TextInput(attrs={'class': 'form-control form-control-lg rounded-pill'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-lg rounded-pill', 'rows': 3}),
            'medical_documents': forms.FileInput(attrs={'class': 'form-control form-control-lg'}),
        }

    def clean_medical_documents(self):
        medical_documents = self.cleaned_data.get('medical_documents')
        if medical_documents:
            if medical_documents.size > 10 * 1024 * 1024:  # 10MB max
                raise forms.ValidationError('Medical document file too large (max 10MB).')
        return medical_documents
