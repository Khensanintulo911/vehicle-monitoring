from rest_framework import serializers
from .models import Driver, Vehicle, Job, Trip, TripEvent, GPSRoutePoint

class DriverSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return obj.user.get_full_name()
    
    class Meta:
        model = Driver
        fields = ['id', 'name', 'phone', 'license_number', 'is_active']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'registration_number', 'vehicle_type', 'fuel_capacity', 'current_odometer']


class JobSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField()
    vehicle_name = serializers.SerializerMethodField()
    
    def get_driver_name(self, obj):
        return obj.assigned_driver.user.get_full_name() if obj.assigned_driver else None
    
    def get_vehicle_name(self, obj):
        return obj.assigned_vehicle.name if obj.assigned_vehicle else None
    
    class Meta:
        model = Job
        fields = [
            'id', 'job_number', 'customer_name', 'customer_phone', 'job_location',
            'job_location_lat', 'job_location_lng', 'description', 'instructions',
            'expected_duration', 'scheduled_start', 'assigned_driver', 'assigned_vehicle',
            'driver_name', 'vehicle_name', 'status'
        ]


class TripEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripEvent
        fields = ['id', 'trip', 'event_type', 'timestamp', 'description', 'location_lat', 'location_lng', 'photo']


class GPSRoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSRoutePoint
        fields = ['id', 'latitude', 'longitude', 'timestamp', 'speed']


class TripSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField()
    vehicle_name = serializers.SerializerMethodField()
    fuel_consumed = serializers.SerializerMethodField()
    fuel_efficiency = serializers.SerializerMethodField()
    
    def get_driver_name(self, obj):
        return obj.driver.user.get_full_name()
    
    def get_vehicle_name(self, obj):
        return obj.vehicle.name
    
    def get_fuel_consumed(self, obj):
        return obj.get_fuel_consumed()
    
    def get_fuel_efficiency(self, obj):
        return obj.get_fuel_efficiency()
    
    class Meta:
        model = Trip
        fields = [
            'id', 'trip_number', 'job', 'driver', 'vehicle', 'driver_name', 'vehicle_name',
            'start_time', 'start_odometer', 'start_fuel_level', 'start_location_lat', 'start_location_lng',
            'end_time', 'end_odometer', 'end_fuel_level', 'end_location_lat', 'end_location_lng',
            'distance_travelled', 'duration_minutes', 'route_compliance', 'is_after_hours',
            'fuel_consumed', 'fuel_efficiency', 'status', 'notes'
        ]
