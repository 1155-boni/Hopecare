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

def create_superusers():
    superusers = [
        {
            'email': 'dietboni@gmail.com',
            'username': 'admin',
            'password': 'admin@123',
            'role': 'admin'
        },
        {
            'email': 'dietboni@gmail.com',
            'username': 'storekeeper',
            'password': 'storekeeper@123',
            'role': 'storekeeper'
        },
        {
            'email': 'dietboni@gmail.com',
            'username': 'welfare',
            'password': 'welfare@123',
            'role': 'welfare'
        }
    ]

    for su in superusers:
        if not User.objects.filter(email=su['email']).exists():
            user = User.objects.create_superuser(
                email=su['email'],
                username=su['username'],
                password=su['password']
            )
            user.role = su['role']
            user.save()
            print(f"Superuser {su['username']} created successfully.")
        else:
            print(f"Superuser {su['username']} already exists.")

if __name__ == '__main__':
    create_superusers()
