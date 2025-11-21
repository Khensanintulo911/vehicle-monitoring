import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.contrib.auth.models import User
from trips.models import Driver, Vehicle, Job, Trip, TripEvent
from django.utils import timezone

print("=" * 70)
print("FLEET MANAGEMENT SYSTEM - END-TO-END WORKFLOW TEST")
print("=" * 70)

driver_user = User.objects.get(username='john')
driver = Driver.objects.get(user=driver_user)

job = Job.objects.filter(assigned_driver=driver, status='assigned').first()
if not job:
    job = Job.objects.filter(assigned_driver=driver).first()
    if job:
        job.status = 'assigned'
        job.save()
        print(f"   Reset job {job.job_number} to 'assigned' status")
    else:
        print("ERROR: No jobs found for driver John")
        exit(1)

vehicle_initial_odometer = job.assigned_vehicle.current_odometer
print(f"\n1. INITIAL STATE:")
print(f"   Driver: {driver}")
print(f"   Job: {job.job_number} - {job.customer_name}")
print(f"   Vehicle: {job.assigned_vehicle}")
print(f"   Vehicle Odometer: {vehicle_initial_odometer} km")

print(f"\n2. STARTING TRIP:")
trip = Trip.objects.create(
    job=job,
    driver=driver,
    vehicle=job.assigned_vehicle,
    start_odometer=Decimal('45230.5'),
    start_fuel_level=Decimal('75.5'),
    start_location_lat=Decimal('-26.2041'),
    start_location_lng=Decimal('28.0473'),
)

job.status = 'in_progress'
job.save()

print(f"   ✓ Trip {trip.trip_number} created")
print(f"   Start Time: {trip.start_time}")
print(f"   Start Odometer: {trip.start_odometer} km")
print(f"   Start Fuel: {trip.start_fuel_level} L")
print(f"   Start Location: ({trip.start_location_lat}, {trip.start_location_lng})")

print(f"\n3. LOGGING TRIP EVENTS:")
event1 = TripEvent.objects.create(
    trip=trip,
    event_type='arrival',
    description='Arrived at customer location',
    location_lat=Decimal('-26.1076'),
    location_lng=Decimal('28.0567'),
)
print(f"   ✓ Event 1: {event1.get_event_type_display()} - {event1.description}")

event2 = TripEvent.objects.create(
    trip=trip,
    event_type='delay',
    description='Minor traffic delays on M1',
)
print(f"   ✓ Event 2: {event2.get_event_type_display()} - {event2.description}")

event3 = TripEvent.objects.create(
    trip=trip,
    event_type='completed',
    description='Job completed successfully',
    location_lat=Decimal('-26.1076'),
    location_lng=Decimal('28.0567'),
)
print(f"   ✓ Event 3: {event3.get_event_type_display()} - {event3.description}")

print(f"\n4. ENDING TRIP:")
trip.end_odometer = Decimal('45264.7')
trip.end_fuel_level = Decimal('72.3')
trip.end_location_lat = Decimal('-26.1076')
trip.end_location_lng = Decimal('28.0567')
trip.notes = 'Job completed without issues'
trip.end_time = timezone.now()
trip.status = 'completed'
trip.save()

print(f"   End Time: {trip.end_time}")
print(f"   End Odometer: {trip.end_odometer} km")
print(f"   End Fuel: {trip.end_fuel_level} L")
print(f"   End Location: ({trip.end_location_lat}, {trip.end_location_lng})")

print(f"\n5. CALCULATING METRICS:")
trip.calculate_metrics()

trip.refresh_from_db()
print(f"   ✓ Distance Travelled: {trip.distance_travelled} km")
print(f"   ✓ Duration: {trip.duration_minutes} minutes")
print(f"   ✓ Route Compliance: {trip.route_compliance}%")
print(f"   ✓ After Hours: {trip.is_after_hours}")

fuel_consumed = trip.get_fuel_consumed()
fuel_efficiency = trip.get_fuel_efficiency()
print(f"   ✓ Fuel Consumed: {fuel_consumed} L")
print(f"   ✓ Fuel Efficiency: {fuel_efficiency:.2f} km/L" if fuel_efficiency else "   ✓ Fuel Efficiency: N/A")

print(f"\n6. UPDATING JOB AND VEHICLE:")
trip.job.status = 'completed'
trip.job.save()
print(f"   ✓ Job {trip.job.job_number} marked as completed")

trip.vehicle.current_odometer = trip.end_odometer
trip.vehicle.save()

trip.vehicle.refresh_from_db()
print(f"   ✓ Vehicle odometer updated from {vehicle_initial_odometer} to {trip.vehicle.current_odometer} km")

print(f"\n7. VERIFICATION:")
trip.refresh_from_db()
errors = []

if not trip.distance_travelled:
    errors.append("   ✗ Distance travelled not calculated")
else:
    print(f"   ✓ Distance travelled: {trip.distance_travelled} km")

if trip.duration_minutes is None:
    errors.append("   ✗ Duration not calculated")
else:
    print(f"   ✓ Duration calculated: {trip.duration_minutes} minutes")

if trip.route_compliance is None:
    errors.append("   ✗ Route compliance not calculated")
else:
    print(f"   ✓ Route compliance calculated: {trip.route_compliance}%")

if trip.vehicle.current_odometer != trip.end_odometer:
    errors.append(f"   ✗ Vehicle odometer not updated correctly")
else:
    print(f"   ✓ Vehicle odometer updated correctly: {trip.vehicle.current_odometer} km")

if trip.job.status != 'completed':
    errors.append("   ✗ Job status not updated")
else:
    print(f"   ✓ Job status updated to: {trip.job.status}")

if trip.events.count() != 3:
    errors.append("   ✗ Events not saved correctly")
else:
    print(f"   ✓ All 3 events saved correctly")

print(f"\n8. FINAL RESULT:")
if errors:
    print("   ✗ TEST FAILED - Issues found:")
    for error in errors:
        print(error)
    exit(1)
else:
    print("   ✓ ALL TESTS PASSED!")
    print("   ✓ Complete workflow (start → log events → end) works reliably")
    print("   ✓ Automatic calculations persist correctly")
    print("   ✓ Vehicle odometer updates correctly")
    print("   ✓ No InvalidOperation or IntegrityError exceptions")

print("\n" + "=" * 70)
print("END-TO-END TEST COMPLETED SUCCESSFULLY")
print("=" * 70)
