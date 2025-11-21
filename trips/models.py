from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from geopy.distance import geodesic


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=50, choices=[
        ('bakkie', 'Bakkie'),
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('car', 'Car'),
    ])
    fuel_capacity = models.DecimalField(max_digits=6, decimal_places=2, help_text='Litres')
    current_odometer = models.DecimalField(max_digits=10, decimal_places=1, default=0, help_text='Kilometers')
    is_active = models.BooleanField(default=True)
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
    customer_phone = models.CharField(max_length=20, blank=True)
    job_location = models.CharField(max_length=500)
    job_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    job_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    expected_duration = models.IntegerField(help_text='Expected duration in minutes')
    scheduled_start = models.DateTimeField()
    assigned_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    assigned_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.job_number:
            last_job = Job.objects.order_by('-id').first()
            if last_job:
                last_number = int(last_job.job_number.split('-')[1])
                self.job_number = f'JOB-{last_number + 1:05d}'
            else:
                self.job_number = 'JOB-00001'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-scheduled_start']


class Trip(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    trip_number = models.CharField(max_length=50, unique=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trips')
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    start_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    start_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    start_odometer = models.DecimalField(max_digits=10, decimal_places=1, help_text='Kilometers')
    end_odometer = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, help_text='Kilometers')
    
    start_fuel_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Litres or Percentage')
    end_fuel_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Litres or Percentage')
    
    distance_travelled = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Kilometers')
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    route_compliance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Percentage')
    is_after_hours = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trip_number} - {self.driver} - {self.job.job_number}"

    def save(self, *args, **kwargs):
        if not self.trip_number:
            last_trip = Trip.objects.order_by('-id').first()
            if last_trip:
                last_number = int(last_trip.trip_number.split('-')[1])
                self.trip_number = f'TRIP-{last_number + 1:05d}'
            else:
                self.trip_number = 'TRIP-00001'
        super().save(*args, **kwargs)

    def calculate_metrics(self):
        if self.end_time:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
            
            if self.end_odometer:
                self.distance_travelled = self.end_odometer - self.start_odometer
            
            if self.start_location_lat and self.start_location_lng and self.end_location_lat and self.end_location_lng:
                start_coords = (float(self.start_location_lat), float(self.start_location_lng))
                end_coords = (float(self.end_location_lat), float(self.end_location_lng))
                gps_distance = geodesic(start_coords, end_coords).kilometers
                
                if self.job.job_location_lat and self.job.job_location_lng and gps_distance > 0:
                    job_coords = (float(self.job.job_location_lat), float(self.job.job_location_lng))
                    expected_distance = geodesic(start_coords, job_coords).kilometers
                    
                    if expected_distance > 0:
                        self.route_compliance = min(100, (expected_distance / gps_distance) * 100)
                elif gps_distance == 0:
                    self.route_compliance = 100
            
            start_hour = self.start_time.hour
            if start_hour < 6 or start_hour >= 18 or self.start_time.weekday() >= 5:
                self.is_after_hours = True
            
            self.save()

    def get_fuel_consumed(self):
        if self.start_fuel_level and self.end_fuel_level:
            return float(self.start_fuel_level - self.end_fuel_level)
        return None

    def get_fuel_efficiency(self):
        fuel_consumed = self.get_fuel_consumed()
        if fuel_consumed and self.distance_travelled and fuel_consumed > 0:
            return float(self.distance_travelled) / fuel_consumed
        return None

    class Meta:
        ordering = ['-start_time']


class TripEvent(models.Model):
    EVENT_TYPES = [
        ('delay', 'Delay'),
        ('fuel_stop', 'Fuel Stop'),
        ('incident', 'Incident/Damage'),
        ('arrival', 'Arrived at Customer'),
        ('completed', 'Completed Job'),
        ('photo', 'Photo Upload'),
        ('other', 'Other'),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    photo = models.ImageField(upload_to='trip_events/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trip.trip_number} - {self.get_event_type_display()} - {self.timestamp}"

    class Meta:
        ordering = ['timestamp']


class GPSRoutePoint(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='gps_points')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='km/h')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trip.trip_number} - {self.timestamp}"

    class Meta:
        ordering = ['timestamp']
