from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'drivers', views.DriverViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'trips', views.TripViewSet)
router.register(r'trip-events', views.TripEventViewSet)
router.register(r'gps-points', views.GPSRoutePointViewSet)

urlpatterns = [
    path('', views.driver_dashboard, name='driver_dashboard'),
    path('start-trip/<int:job_id>/', views.start_trip, name='start_trip'),
    path('active-trip/<int:trip_id>/', views.active_trip, name='active_trip'),
    path('add-event/<int:trip_id>/', views.add_trip_event, name='add_trip_event'),
    path('end-trip/<int:trip_id>/', views.end_trip, name='end_trip'),
    path('api/', include(router.urls)),
]
