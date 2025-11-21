from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import Driver, Vehicle, Job, Trip, TripEvent, GPSRoutePoint
from .serializers import (
    DriverSerializer, VehicleSerializer, JobSerializer,
    TripSerializer, TripEventSerializer, GPSRoutePointSerializer
)


@login_required
def driver_dashboard(request):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, "You are not registered as a driver.")
        return redirect('/admin/')
    
    assigned_jobs = Job.objects.filter(assigned_driver=driver, status='assigned')
    active_trip = Trip.objects.filter(driver=driver, status='started').first()
    completed_trips = Trip.objects.filter(driver=driver, status='completed')[:5]
    
    context = {
        'driver': driver,
        'assigned_jobs': assigned_jobs,
        'active_trip': active_trip,
        'completed_trips': completed_trips,
    }
    return render(request, 'trips/driver_dashboard.html', context)


@login_required
def start_trip(request, job_id):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, "You are not registered as a driver.")
        return redirect('/admin/')
    
    job = get_object_or_404(Job, id=job_id, assigned_driver=driver)
    
    if Trip.objects.filter(driver=driver, status='started').exists():
        messages.error(request, "You already have an active trip. Please complete it first.")
        return redirect('driver_dashboard')
    
    if request.method == 'POST':
        start_odometer = request.POST.get('start_odometer')
        start_fuel_level = request.POST.get('start_fuel_level')
        start_lat = request.POST.get('start_lat')
        start_lng = request.POST.get('start_lng')
        
        trip = Trip.objects.create(
            job=job,
            driver=driver,
            vehicle=job.assigned_vehicle,
            start_odometer=Decimal(start_odometer),
            start_fuel_level=Decimal(start_fuel_level),
            start_location_lat=Decimal(start_lat) if start_lat else None,
            start_location_lng=Decimal(start_lng) if start_lng else None,
        )
        
        job.status = 'in_progress'
        job.save()
        
        messages.success(request, f"Trip {trip.trip_number} started successfully!")
        return redirect('active_trip', trip_id=trip.id)
    
    context = {
        'job': job,
        'vehicle': job.assigned_vehicle,
    }
    return render(request, 'trips/start_trip.html', context)


@login_required
def active_trip(request, trip_id):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, "You are not registered as a driver.")
        return redirect('/admin/')
    
    trip = get_object_or_404(Trip, id=trip_id, driver=driver, status='started')
    
    if request.method == 'POST':
        action_type = request.POST.get('action')
        
        if action_type == 'add_event':
            event_type = request.POST.get('event_type')
            description = request.POST.get('description')
            location_lat = request.POST.get('location_lat')
            location_lng = request.POST.get('location_lng')
            photo = request.FILES.get('photo')
            
            TripEvent.objects.create(
                trip=trip,
                event_type=event_type,
                description=description,
                location_lat=Decimal(location_lat) if location_lat else None,
                location_lng=Decimal(location_lng) if location_lng else None,
                photo=photo,
            )
            
            messages.success(request, "Event logged successfully!")
            return redirect('active_trip', trip_id=trip.id)
    
    events = trip.events.all()
    
    context = {
        'trip': trip,
        'events': events,
    }
    return render(request, 'trips/active_trip.html', context)


@login_required
def end_trip(request, trip_id):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, "You are not registered as a driver.")
        return redirect('/admin/')
    
    trip = get_object_or_404(Trip, id=trip_id, driver=driver, status='started')
    
    if request.method == 'POST':
        end_odometer = request.POST.get('end_odometer')
        end_fuel_level = request.POST.get('end_fuel_level')
        end_lat = request.POST.get('end_lat')
        end_lng = request.POST.get('end_lng')
        notes = request.POST.get('notes', '')
        
        trip.end_odometer = Decimal(end_odometer)
        trip.end_fuel_level = Decimal(end_fuel_level)
        trip.end_location_lat = Decimal(end_lat) if end_lat else None
        trip.end_location_lng = Decimal(end_lng) if end_lng else None
        trip.end_time = timezone.now()
        trip.notes = notes
        trip.status = 'completed'
        trip.save()
        
        trip.calculate_metrics()
        
        trip.job.status = 'completed'
        trip.job.save()
        
        trip.vehicle.current_odometer = trip.end_odometer
        trip.vehicle.save()
        
        messages.success(request, f"Trip {trip.trip_number} completed successfully!")
        return redirect('driver_dashboard')
    
    context = {
        'trip': trip,
    }
    return render(request, 'trips/end_trip.html', context)


class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class TripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    
    @action(detail=True, methods=['get'])
    def gps_route(self, request, pk=None):
        trip = self.get_object()
        gps_points = trip.gps_points.all()
        serializer = GPSRoutePointSerializer(gps_points, many=True)
        return Response(serializer.data)


class TripEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TripEvent.objects.all()
    serializer_class = TripEventSerializer
