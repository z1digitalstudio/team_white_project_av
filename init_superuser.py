import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoAlvaroValero.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv('DJANGO_SUPERUSER_USERNAME', '')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '')

if username and email and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"✅ Superuser '{username}' created successfully!")
    else:
        print(f"⚠️  The superuser '{username}' already exists!")
else:
    print("⚠️  Environment variables for superuser not configured. Skipping creation.")

