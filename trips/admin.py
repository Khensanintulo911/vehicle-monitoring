from django.contrib import admin
from .models import Driver, Vehicle, Job, Trip, TripEvent, GPSRoutePoint


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'phone', 'license_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'phone', 'license_number']
    
    def get_full_name(self, obj):
        return str(obj)
    get_full_name.short_description = 'Driver Name'


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['name', 'registration_number', 'vehicle_type', 'current_odometer', 'is_active', 'created_at']
    list_filter = ['vehicle_type', 'is_active', 'created_at']
    search_fields = ['name', 'registration_number']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['job_number', 'customer_name', 'job_location', 'scheduled_start', 'assigned_driver', 'assigned_vehicle', 'status', 'created_at']
    list_filter = ['status', 'scheduled_start', 'created_at']
    search_fields = ['job_number', 'customer_name', 'job_location', 'description']
    raw_id_fields = ['assigned_driver', 'assigned_vehicle']
    date_hierarchy = 'scheduled_start'


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['trip_number', 'job', 'driver', 'vehicle', 'start_time', 'end_time', 'distance_travelled', 'status']
    list_filter = ['status', 'is_after_hours', 'start_time']
    search_fields = ['trip_number', 'job__job_number', 'job__customer_name', 'driver__user__first_name', 'driver__user__last_name']
    raw_id_fields = ['job', 'driver', 'vehicle']
    date_hierarchy = 'start_time'
    readonly_fields = ['trip_number', 'start_time', 'created_at', 'updated_at']


@admin.register(TripEvent)
class TripEventAdmin(admin.ModelAdmin):
    list_display = ['trip', 'event_type', 'description', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['trip__trip_number', 'description']
    raw_id_fields = ['trip']
    date_hierarchy = 'timestamp'


@admin.register(GPSRoutePoint)
class GPSRoutePointAdmin(admin.ModelAdmin):
    list_display = ['trip', 'latitude', 'longitude', 'speed', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['trip__trip_number']
    raw_id_fields = ['trip']
    date_hierarchy = 'timestamp'
