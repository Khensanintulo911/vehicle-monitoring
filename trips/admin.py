from django.contrib import admin
from .models import Driver, Vehicle, Job, Trip, TripEvent, GPSRoutePoint

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'license_number', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__first_name', 'user__last_name', 'license_number', 'phone']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['name', 'registration_number', 'vehicle_type', 'current_odometer']
    list_filter = ['vehicle_type']
    search_fields = ['name', 'registration_number']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['job_number', 'customer_name', 'job_location', 'scheduled_start', 'assigned_driver', 'status']
    list_filter = ['status', 'scheduled_start']
    search_fields = ['job_number', 'customer_name', 'job_location']
    date_hierarchy = 'scheduled_start'


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['trip_number', 'driver', 'vehicle', 'start_time', 'distance_travelled', 'status']
    list_filter = ['status', 'start_time', 'is_after_hours']
    search_fields = ['trip_number', 'driver__user__first_name', 'driver__user__last_name']
    date_hierarchy = 'start_time'
    readonly_fields = ['trip_number', 'distance_travelled', 'duration_minutes', 'route_compliance']


@admin.register(TripEvent)
class TripEventAdmin(admin.ModelAdmin):
    list_display = ['trip', 'event_type', 'timestamp', 'description']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['trip__trip_number', 'description']
    date_hierarchy = 'timestamp'


@admin.register(GPSRoutePoint)
class GPSRoutePointAdmin(admin.ModelAdmin):
    list_display = ['trip', 'latitude', 'longitude', 'timestamp', 'speed']
    list_filter = ['timestamp']
    search_fields = ['trip__trip_number']
    date_hierarchy = 'timestamp'
