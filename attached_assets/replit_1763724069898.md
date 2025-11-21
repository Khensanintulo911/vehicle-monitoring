# Fleet Management System

## Overview
A comprehensive fleet management system with trip logging capabilities for drivers and analytics dashboard for managers. Built with Django backend and Streamlit dashboard.

## Recent Changes
**November 21, 2025**
- Initial project setup complete
- Django backend with PostgreSQL database configured
- Mobile-friendly driver interface created
- REST API endpoints for data access
- Streamlit analytics dashboard implemented
- Sample data populated for testing

## Project Architecture

### Backend (Django)
- **Framework**: Django 4.2.7 with Django REST Framework
- **Database**: PostgreSQL (Replit-hosted)
- **Key Models**:
  - Driver: Driver information linked to User model
  - Vehicle: Fleet vehicle details and odometer tracking
  - Job: Customer jobs assigned to drivers
  - Trip: Trip sheets with automatic metrics calculation
  - TripEvent: Events logged during trips (delays, fuel stops, incidents, photos)
  - GPSRoutePoint: GPS tracking points for route visualization

### Frontend
- **Mobile Interface**: Django templates with Bootstrap 5 and Leaflet.js for maps
- **Dashboard**: Streamlit with Plotly charts and Folium maps
- **REST API**: Available at `/api/` for dashboard and future integrations

### Key Features Implemented
1. Job assignment system with customer details and locations
2. Trip logging (start → events → end) with GPS tracking
3. Automatic calculations:
   - Distance travelled (GPS + odometer)
   - Duration and fuel consumption
   - Route compliance checking
   - After-hours detection
   - Fuel efficiency (km/L)
4. Event logging during trips (delays, fuel stops, incidents, photos)
5. Admin interface for managers to assign jobs and view all data
6. Analytics dashboard with performance metrics and route visualization

## Access & Credentials

### Admin Panel
URL: http://0.0.0.0:5000/admin/
- Username: `admin`
- Password: `admin123`

### Driver Interface
URL: http://0.0.0.0:5000/
- Driver 1: username `john`, password `driver123`
- Driver 2: username `sarah`, password `driver123`

### Streamlit Dashboard
Run with: `streamlit run dashboard.py --server.port 8501`
Connects to Django API at http://0.0.0.0:5000/api/

## Sample Data
The system includes:
- 2 drivers (John Smith, Sarah Johnson)
- 2 vehicles (Bakkie #7, Van #3)
- 3 jobs assigned to drivers

## File Structure
```
fleet_management/          # Django project configuration
  settings.py             # Database, apps, and middleware config
  urls.py                 # Main URL routing
trips/                    # Main app
  models.py              # Database models
  views.py               # Mobile interface and API views
  serializers.py         # REST API serializers
  admin.py               # Admin interface configuration
  templates/trips/       # Mobile interface templates
    driver_dashboard.html
    start_trip.html
    active_trip.html
    end_trip.html
  templates/registration/
    login.html
dashboard.py             # Streamlit analytics dashboard
create_sample_data.py    # Script to populate test data
manage.py                # Django management script
requirements.txt         # Python dependencies
```

## API Endpoints
All endpoints available at `/api/`:
- `/api/drivers/` - List all drivers
- `/api/vehicles/` - List all vehicles
- `/api/jobs/` - List all jobs
- `/api/trips/` - List all trips
- `/api/trips/<id>/` - Trip details
- `/api/trips/<id>/gps-route/` - GPS route points for a trip
- `/api/trip-events/` - List all trip events

## Development Notes
- Django server runs on port 5000 (accessible to drivers)
- Streamlit dashboard can run on port 8501
- PostgreSQL database automatically configured via environment variables
- Media files stored in `media/` directory for trip event photos
- GPS coordinates captured automatically using browser geolocation API

## Next Steps
- Add real-time GPS tracking during active trips
- Implement automated alerts for route deviations
- Create comprehensive reporting features
- Add batch export functionality (PDF, CSV)
- Implement maintenance scheduling based on odometer readings
