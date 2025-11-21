from rest_framework import serializers
from .models import Driver, Vehicle, Job, Trip, TripEvent, GPSRoutePoint


class DriverSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Driver
        fields = ['id', 'full_name', 'username', 'phone', 'license_number', 'is_active']
    
    def get_full_name(self, obj):
        return str(obj)


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'registration_number', 'vehicle_type', 'fuel_capacity', 'current_odometer', 'is_active']


class JobSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField()
    vehicle_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ['id', 'job_number', 'customer_name', 'customer_phone', 'job_location', 
                  'job_location_lat', 'job_location_lng', 'description', 'instructions',
                  'expected_duration', 'scheduled_start', 'assigned_driver', 'driver_name',
                  'assigned_vehicle', 'vehicle_name', 'status', 'created_at']
    
    def get_driver_name(self, obj):
        return str(obj.assigned_driver) if obj.assigned_driver else None
    
    def get_vehicle_name(self, obj):
        return str(obj.assigned_vehicle) if obj.assigned_vehicle else None


class TripEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = TripEvent
        fields = ['id', 'trip', 'event_type', 'event_type_display', 'description', 
                  'location_lat', 'location_lng', 'photo', 'timestamp']


class GPSRoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSRoutePoint
        fields = ['id', 'trip', 'latitude', 'longitude', 'speed', 'timestamp']


class TripSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)
    driver_name = serializers.SerializerMethodField()
    vehicle_name = serializers.SerializerMethodField()
    fuel_consumed = serializers.SerializerMethodField()
    fuel_efficiency = serializers.SerializerMethodField()
    events = TripEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Trip
        fields = ['id', 'trip_number', 'job', 'job_details', 'driver', 'driver_name', 
                  'vehicle', 'vehicle_name', 'start_time', 'end_time',
                  'start_location_lat', 'start_location_lng', 'end_location_lat', 'end_location_lng',
                  'start_odometer', 'end_odometer', 'start_fuel_level', 'end_fuel_level',
                  'distance_travelled', 'duration_minutes', 'route_compliance', 'is_after_hours',
                  'notes', 'status', 'fuel_consumed', 'fuel_efficiency', 'events', 'created_at']
    
    def get_driver_name(self, obj):
        return str(obj.driver)
    
    def get_vehicle_name(self, obj):
        return str(obj.vehicle)
    
    def get_fuel_consumed(self, obj):
        return obj.get_fuel_consumed()
    
    def get_fuel_efficiency(self, obj):
        return obj.get_fuel_efficiency()
