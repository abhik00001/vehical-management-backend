import os
from django.contrib.auth import get_user_model
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Backend.settings")
django.setup()
User = get_user_model()

# username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin1@gmail.com")
first_name = os.environ.get("DJANGO_SUPERUSER_FIRSTNAME", "Admin")
role = os.environ.get("DJANGO_SUPERUSER_ROLE", "admin")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin1")

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        first_name=first_name,
        role=role,
        password=password,
    )
    print("✅ Superuser created")
else:
    print("ℹ️ Superuser already exists")
