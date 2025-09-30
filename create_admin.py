#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hopecare_project.settings')

# Setup Django
django.setup()

from accounts.models import User

def create_admin():
    if not User.objects.filter(email='info.hopecarecenter@gmail.com').exists():
        User.objects.create_superuser(
            email='info.hopecarecenter@gmail.com',
            username='Hopecare',
            password='hope@care123'
        )
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")

if __name__ == '__main__':
    create_admin()
