import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.contrib.auth.models import User
from trips.models import Driver, Vehicle, Job
from django.utils import timezone
from datetime import timedelta

print("Creating sample data...")

admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'is_superuser': True,
        'is_staff': True,
        'first_name': 'Admin',
        'last_name': 'User'
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print("Created admin user: username='admin', password='admin123'")
else:
    print("Admin user already exists")

user1, created = User.objects.get_or_create(
    username='john',
    defaults={
        'first_name': 'John',
        'last_name': 'Smith'
    }
)
if created:
    user1.set_password('driver123')
    user1.save()
    print("Created driver user: username='john', password='driver123'")

user2, created = User.objects.get_or_create(
    username='sarah',
    defaults={
        'first_name': 'Sarah',
        'last_name': 'Johnson'
    }
)
if created:
    user2.set_password('driver123')
    user2.save()
    print("Created driver user: username='sarah', password='driver123'")

driver1, created = Driver.objects.get_or_create(
    user=user1,
    defaults={
        'phone': '+27 123 456 789',
        'license_number': 'DL12345'
    }
)
if created:
    print(f"Created driver: {driver1}")

driver2, created = Driver.objects.get_or_create(
    user=user2,
    defaults={
        'phone': '+27 987 654 321',
        'license_number': 'DL54321'
    }
)
if created:
    print(f"Created driver: {driver2}")

vehicle1, created = Vehicle.objects.get_or_create(
    registration_number='ABC123GP',
    defaults={
        'name': 'Bakkie #7',
        'vehicle_type': 'bakkie',
        'fuel_capacity': 80,
        'current_odometer': 45230.5
    }
)
if created:
    print(f"Created vehicle: {vehicle1}")

vehicle2, created = Vehicle.objects.get_or_create(
    registration_number='XYZ789GP',
    defaults={
        'name': 'Van #3',
        'vehicle_type': 'van',
        'fuel_capacity': 70,
        'current_odometer': 32150.2
    }
)
if created:
    print(f"Created vehicle: {vehicle2}")

now = timezone.now()

job1, created = Job.objects.get_or_create(
    job_number='JOB-00001',
    defaults={
        'customer_name': 'ABC Construction',
        'customer_phone': '+27 11 123 4567',
        'job_location': 'Sandton City, Johannesburg',
        'job_location_lat': -26.1076,
        'job_location_lng': 28.0567,
        'description': 'Install water pump at construction site',
        'instructions': 'Contact site manager John on arrival. Equipment in storage room A.',
        'expected_duration': 120,
        'scheduled_start': now + timedelta(hours=1),
        'assigned_driver': driver1,
        'assigned_vehicle': vehicle1,
        'status': 'assigned'
    }
)
if created:
    print(f"Created job: {job1}")

job2, created = Job.objects.get_or_create(
    job_number='JOB-00002',
    defaults={
        'customer_name': 'XYZ Manufacturing',
        'customer_phone': '+27 11 987 6543',
        'job_location': 'Midrand Industrial Park, Johannesburg',
        'job_location_lat': -25.9953,
        'job_location_lng': 28.1277,
        'description': 'Repair industrial pump',
        'instructions': 'Ask for Mr. Patel at reception. Park in loading zone.',
        'expected_duration': 90,
        'scheduled_start': now + timedelta(hours=3),
        'assigned_driver': driver2,
        'assigned_vehicle': vehicle2,
        'status': 'assigned'
    }
)
if created:
    print(f"Created job: {job2}")

job3, created = Job.objects.get_or_create(
    job_number='JOB-00003',
    defaults={
        'customer_name': 'Green Valley Estate',
        'customer_phone': '+27 11 555 7890',
        'job_location': 'Fourways, Johannesburg',
        'job_location_lat': -26.0167,
        'job_location_lng': 28.0004,
        'description': 'Routine maintenance check',
        'instructions': 'Security code: 4821. Ask for maintenance supervisor.',
        'expected_duration': 60,
        'scheduled_start': now + timedelta(days=1),
        'assigned_driver': driver1,
        'assigned_vehicle': vehicle1,
        'status': 'pending'
    }
)
if created:
    print(f"Created job: {job3}")

print("\nSample data created successfully!")
print("\n=== Login Credentials ===")
print("Admin Panel: username='admin', password='admin123'")
print("Driver 1: username='john', password='driver123'")
print("Driver 2: username='sarah', password='driver123'")
print("\nAccess the admin panel at: http://0.0.0.0:5000/admin/")
print("Access the driver interface at: http://0.0.0.0:5000/")
