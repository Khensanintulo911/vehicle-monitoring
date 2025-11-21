from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'drivers', views.DriverViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'trips', views.TripViewSet)
router.register(r'trip-events', views.TripEventViewSet)

urlpatterns = [
    path('', views.driver_dashboard, name='driver_dashboard'),
    path('start-trip/<int:job_id>/', views.start_trip, name='start_trip'),
    path('active-trip/<int:trip_id>/', views.active_trip, name='active_trip'),
    path('end-trip/<int:trip_id>/', views.end_trip, name='end_trip'),
    
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('api/', include(router.urls)),
]
