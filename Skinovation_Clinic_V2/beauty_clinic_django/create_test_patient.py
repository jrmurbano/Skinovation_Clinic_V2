"""
Script to create test patient user for Playwright tests
Run: python create_test_patient.py
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_clinic_django.settings')
django.setup()

from accounts.models import User

# Create or update patient user
user, created = User.objects.get_or_create(
    username='patient',
    defaults={
        'user_type': 'patient',
        'first_name': 'Test',
        'last_name': 'Patient',
        'email': 'patient@test.com',
        'is_active': True
    }
)

# Set password
user.set_password('defaultpassword123')
user.is_active = True
user.save()

if created:
    print("✅ Patient user created successfully!")
    print(f"   Username: patient")
    print(f"   Password: defaultpassword123")
else:
    print("✅ Patient user already exists - password updated!")
    print(f"   Username: patient")
    print(f"   Password: defaultpassword123")

# Verify the user can authenticate
from django.contrib.auth import authenticate
auth_user = authenticate(username='patient', password='defaultpassword123')
if auth_user:
    print("✅ Authentication test: SUCCESS")
else:
    print("❌ Authentication test: FAILED")






