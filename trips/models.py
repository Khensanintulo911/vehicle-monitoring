from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from geopy.distance import geodesic
from datetime import datetime, time

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.license_number}"
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('bakkie', 'Bakkie'),
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('sedan', 'Sedan'),
    ]
    
    name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    fuel_capacity = models.DecimalField(max_digits=6, decimal_places=2)
    current_odometer = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.registration_number})"
    
    class Meta:
        ordering = ['name']


class Job(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    job_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    job_location = models.CharField(max_length=255)
    job_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    job_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    expected_duration = models.IntegerField(help_text="Expected duration in minutes")
    scheduled_start = models.DateTimeField()
    assigned_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, related_name='jobs')
    assigned_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.job_number} - {self.customer_name}"
    
    class Meta:
        ordering = ['-scheduled_start']


class Trip(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    trip_number = models.CharField(max_length=50, unique=True, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trips')
    
    start_time = models.DateTimeField(auto_now_add=True)
    start_odometer = models.DecimalField(max_digits=10, decimal_places=2)
    start_fuel_level = models.DecimalField(max_digits=5, decimal_places=2)
    start_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    start_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    end_time = models.DateTimeField(null=True, blank=True)
    end_odometer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    end_fuel_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    end_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    distance_travelled = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    route_compliance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_after_hours = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.trip_number:
            last_trip = Trip.objects.order_by('-id').first()
            if last_trip and last_trip.trip_number:
                last_num = int(last_trip.trip_number.split('-')[1])
                self.trip_number = f"TRIP-{last_num + 1:05d}"
            else:
                self.trip_number = "TRIP-00001"
        super().save(*args, **kwargs)
    
    def calculate_metrics(self):
        if self.end_time and self.end_odometer:
            self.distance_travelled = self.end_odometer - self.start_odometer
            
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
            
            if self.start_location_lat and self.start_location_lng and self.end_location_lat and self.end_location_lng:
                start_coords = (float(self.start_location_lat), float(self.start_location_lng))
                end_coords = (float(self.end_location_lat), float(self.end_location_lng))
                job_coords = (float(self.job.job_location_lat), float(self.job.job_location_lng)) if self.job.job_location_lat else None
                
                if job_coords:
                    direct_distance = geodesic(start_coords, job_coords).km + geodesic(job_coords, end_coords).km
                    actual_distance = float(self.distance_travelled)
                    
                    if actual_distance > 0:
                        self.route_compliance = min(Decimal('100'), Decimal(str((direct_distance / actual_distance) * 100)))
            
            start_hour = self.start_time.time()
            work_start = time(7, 0)
            work_end = time(18, 0)
            self.is_after_hours = start_hour < work_start or start_hour > work_end
            
            self.save()
    
    def get_fuel_consumed(self):
        if self.end_fuel_level:
            return self.start_fuel_level - self.end_fuel_level
        return None
    
    def get_fuel_efficiency(self):
        fuel_consumed = self.get_fuel_consumed()
        if fuel_consumed and self.distance_travelled and fuel_consumed > 0:
            return float(self.distance_travelled) / float(fuel_consumed)
        return None
    
    def __str__(self):
        return f"{self.trip_number} - {self.driver.user.get_full_name()}"
    
    class Meta:
        ordering = ['-start_time']


class TripEvent(models.Model):
    EVENT_TYPES = [
        ('departure', 'Departure'),
        ('arrival', 'Arrival at Job Site'),
        ('delay', 'Delay'),
        ('fuel_stop', 'Fuel Stop'),
        ('incident', 'Incident'),
        ('photo', 'Photo'),
        ('completed', 'Job Completed'),
        ('other', 'Other'),
    ]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    photo = models.ImageField(upload_to='trip_events/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.trip.trip_number}"
    
    class Meta:
        ordering = ['timestamp']


class GPSRoutePoint(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='gps_points')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"GPS Point for {self.trip.trip_number} at {self.timestamp}"
    
    class Meta:
        ordering = ['timestamp']
