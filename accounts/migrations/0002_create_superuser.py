# accounts/migrations/0002_create_superuser.py

from django.db import migrations
import os

def create_superuser(apps, schema_editor):
    # We need to get the CustomUser model from the 'accounts' app
    User = apps.get_model('accounts', 'CustomUser')

    # Get superuser details from environment variables on Render
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    # Only run this logic if all three environment variables are set
    if all([username, email, password]):
        # Check if a superuser with that username already exists to avoid errors on re-deploys
        if not User.objects.filter(username=username).exists():
            print(f"Creating superuser '{username}'")
            # Create the superuser using the details from the environment variables
            User.objects.create_superuser(username=username, email=email, password=password)
        else:
            print(f"Superuser '{username}' already exists. Skipping creation.")
    else:
        print("Superuser environment variables not set. Skipping superuser creation.")


class Migration(migrations.Migration):

    dependencies = [
        # This should depend on the migration that created your CustomUser model.
        # It's usually the first one. Check your migrations folder for the name.
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]