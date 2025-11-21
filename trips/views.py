from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Driver, Vehicle, Job, Trip, TripEvent, GPSRoutePoint
from .serializers import (DriverSerializer, VehicleSerializer, JobSerializer,
                          TripSerializer, TripEventSerializer, GPSRoutePointSerializer)


@login_required
def driver_dashboard(request):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, 'You are not registered as a driver.')
        return redirect('admin:index')
    
    assigned_jobs = Job.objects.filter(assigned_driver=driver, status='assigned')
    active_trip = Trip.objects.filter(driver=driver, status='started').first()
    
    context = {
        'driver': driver,
        'assigned_jobs': assigned_jobs,
        'active_trip': active_trip,
    }
    return render(request, 'trips/driver_dashboard.html', context)


@login_required
def start_trip(request, job_id):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, 'You are not registered as a driver.')
        return redirect('driver_dashboard')
    
    job = get_object_or_404(Job, id=job_id, assigned_driver=driver)
    
    if request.method == 'POST':
        start_odometer = request.POST.get('start_odometer')
        start_fuel_level = request.POST.get('start_fuel_level')
        start_lat = request.POST.get('start_lat')
        start_lng = request.POST.get('start_lng')
        
        if not start_odometer:
            messages.error(request, 'Starting odometer reading is required.')
            return render(request, 'trips/start_trip.html', {'job': job, 'driver': driver})
        
        if not start_lat or not start_lng:
            messages.error(request, 'GPS location is required. Please enable location services.')
            return render(request, 'trips/start_trip.html', {'job': job, 'driver': driver})
        
        try:
            from decimal import Decimal, InvalidOperation
            start_odometer_value = Decimal(str(start_odometer))
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, 'Invalid odometer reading.')
            return render(request, 'trips/start_trip.html', {'job': job, 'driver': driver})
        
        try:
            start_lat_value = Decimal(str(start_lat))
            start_lng_value = Decimal(str(start_lng))
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, 'Invalid GPS coordinates. Please try again.')
            return render(request, 'trips/start_trip.html', {'job': job, 'driver': driver})
        
        start_fuel_value = None
        if start_fuel_level:
            try:
                start_fuel_value = Decimal(str(start_fuel_level))
            except (ValueError, TypeError, InvalidOperation):
                messages.error(request, 'Invalid fuel level.')
                return render(request, 'trips/start_trip.html', {'job': job, 'driver': driver})
        
        trip = Trip.objects.create(
            job=job,
            driver=driver,
            vehicle=job.assigned_vehicle,
            start_odometer=start_odometer_value,
            start_fuel_level=start_fuel_value,
            start_location_lat=start_lat_value,
            start_location_lng=start_lng_value,
        )
        
        job.status = 'in_progress'
        job.save()
        
        messages.success(request, f'Trip {trip.trip_number} started successfully!')
        return redirect('active_trip', trip_id=trip.id)
    
    context = {
        'job': job,
        'driver': driver,
    }
    return render(request, 'trips/start_trip.html', context)


@login_required
def active_trip(request, trip_id):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, 'You are not registered as a driver.')
        return redirect('driver_dashboard')
    
    trip = get_object_or_404(Trip, id=trip_id, driver=driver, status='started')
    events = trip.events.all()
    
    context = {
        'trip': trip,
        'events': events,
    }
    return render(request, 'trips/active_trip.html', context)


@login_required
@require_http_methods(["POST"])
def add_trip_event(request, trip_id):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        return JsonResponse({'error': 'Not a driver'}, status=403)
    
    trip = get_object_or_404(Trip, id=trip_id, driver=driver, status='started')
    
    event_type = request.POST.get('event_type', '').strip()
    description = request.POST.get('description', '').strip()
    location_lat = request.POST.get('location_lat')
    location_lng = request.POST.get('location_lng')
    photo = request.FILES.get('photo')
    
    if not event_type or not description:
        messages.error(request, 'Event type and description are required.')
        return redirect('active_trip', trip_id=trip.id)
    
    valid_event_types = ['delay', 'fuel_stop', 'incident', 'arrival', 'completed', 'photo', 'other']
    if event_type not in valid_event_types:
        messages.error(request, 'Invalid event type.')
        return redirect('active_trip', trip_id=trip.id)
    
    lat_value = None
    lng_value = None
    if location_lat and location_lng:
        try:
            from decimal import Decimal, InvalidOperation
            lat_value = Decimal(str(location_lat))
            lng_value = Decimal(str(location_lng))
        except (ValueError, TypeError, InvalidOperation):
            pass
    
    event = TripEvent.objects.create(
        trip=trip,
        event_type=event_type,
        description=description,
        location_lat=lat_value,
        location_lng=lng_value,
        photo=photo,
    )
    
    messages.success(request, f'{event.get_event_type_display()} event added successfully!')
    return redirect('active_trip', trip_id=trip.id)


@login_required
def end_trip(request, trip_id):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, 'You are not registered as a driver.')
        return redirect('driver_dashboard')
    
    trip = get_object_or_404(Trip, id=trip_id, driver=driver, status='started')
    
    if request.method == 'POST':
        end_odometer = request.POST.get('end_odometer')
        end_lat = request.POST.get('end_lat')
        end_lng = request.POST.get('end_lng')
        end_fuel_level = request.POST.get('end_fuel_level')
        
        if not end_odometer:
            messages.error(request, 'Ending odometer reading is required.')
            return render(request, 'trips/end_trip.html', {'trip': trip})
        
        if not end_lat or not end_lng:
            messages.error(request, 'GPS location is required. Please enable location services.')
            return render(request, 'trips/end_trip.html', {'trip': trip})
        
        try:
            from decimal import Decimal, InvalidOperation
            end_odometer_value = Decimal(str(end_odometer))
            if end_odometer_value < trip.start_odometer:
                messages.error(request, 'Ending odometer cannot be less than starting odometer.')
                return render(request, 'trips/end_trip.html', {'trip': trip})
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, 'Invalid odometer reading.')
            return render(request, 'trips/end_trip.html', {'trip': trip})
        
        try:
            end_lat_value = Decimal(str(end_lat))
            end_lng_value = Decimal(str(end_lng))
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, 'Invalid GPS coordinates. Please try again.')
            return render(request, 'trips/end_trip.html', {'trip': trip})
        
        end_fuel_value = None
        if end_fuel_level:
            try:
                end_fuel_value = Decimal(str(end_fuel_level))
            except (ValueError, TypeError, InvalidOperation):
                messages.error(request, 'Invalid fuel level.')
                return render(request, 'trips/end_trip.html', {'trip': trip})
        
        trip.end_odometer = end_odometer_value
        trip.end_fuel_level = end_fuel_value
        trip.end_location_lat = end_lat_value
        trip.end_location_lng = end_lng_value
        trip.notes = request.POST.get('notes', '')
        
        from django.utils import timezone
        trip.end_time = timezone.now()
        trip.status = 'completed'
        trip.save()
        
        trip.calculate_metrics()
        
        trip.job.status = 'completed'
        trip.job.save()
        
        trip.vehicle.current_odometer = trip.end_odometer
        trip.vehicle.save()
        
        messages.success(request, f'Trip {trip.trip_number} completed successfully!')
        return redirect('driver_dashboard')
    
    context = {
        'trip': trip,
    }
    return render(request, 'trips/end_trip.html', context)


class DriverViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Driver.objects.filter(is_active=True)
    serializer_class = DriverSerializer


class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vehicle.objects.filter(is_active=True)
    serializer_class = VehicleSerializer


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    
    @action(detail=False, methods=['get'])
    def by_driver(self, request):
        driver_id = request.query_params.get('driver_id')
        if driver_id:
            jobs = self.queryset.filter(assigned_driver_id=driver_id)
            serializer = self.get_serializer(jobs, many=True)
            return Response(serializer.data)
        return Response({'error': 'driver_id parameter required'}, status=400)


class TripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    
    @action(detail=True, methods=['get'])
    def gps_route(self, request, pk=None):
        trip = self.get_object()
        points = trip.gps_points.all()
        serializer = GPSRoutePointSerializer(points, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_driver(self, request):
        driver_id = request.query_params.get('driver_id')
        if driver_id:
            trips = self.queryset.filter(driver_id=driver_id)
            serializer = self.get_serializer(trips, many=True)
            return Response(serializer.data)
        return Response({'error': 'driver_id parameter required'}, status=400)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        active_trips = self.queryset.filter(status='started')
        serializer = self.get_serializer(active_trips, many=True)
        return Response(serializer.data)


class TripEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TripEvent.objects.all()
    serializer_class = TripEventSerializer
    
    @action(detail=False, methods=['get'])
    def by_trip(self, request):
        trip_id = request.query_params.get('trip_id')
        if trip_id:
            events = self.queryset.filter(trip_id=trip_id)
            serializer = self.get_serializer(events, many=True)
            return Response(serializer.data)
        return Response({'error': 'trip_id parameter required'}, status=400)


class GPSRoutePointViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GPSRoutePoint.objects.all()
    serializer_class = GPSRoutePointSerializer
