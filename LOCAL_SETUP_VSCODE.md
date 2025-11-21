# Fleet Management System - VS Code Local Setup Guide

This guide will help you run this Django fleet management system on your local PC using VS Code.

## Prerequisites

Before starting, make sure you have these installed on your Windows PC:

1. **Python 3.11** - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   
2. **PostgreSQL 14 or higher** - Download from [postgresql.org](https://www.postgresql.org/download/windows/)
   - Remember the password you set for the `postgres` user
   - Default port is 5432
   
3. **VS Code** - Download from [code.visualstudio.com](https://code.visualstudio.com/)
   - Install the Python extension from Microsoft
   
4. **Git** (optional) - Download from [git-scm.com](https://git-scm.com/downloads)

## Step-by-Step Setup

### Step 1: Download Project Files

1. Download all project files to a folder on your PC (e.g., `C:\Projects\FleetManagement\`)
2. Open VS Code
3. Click `File > Open Folder` and select your project folder

### Step 2: Set Up PostgreSQL Database

1. Open **pgAdmin 4** (installed with PostgreSQL) or use Command Prompt
2. Create a new database for the project:

```sql
-- In pgAdmin or psql command line
CREATE DATABASE fleet_db;
```

### Step 3: Create Python Virtual Environment

1. Open VS Code Terminal (`Terminal > New Terminal` or `` Ctrl+` ``)
2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

```bash
# On Windows Command Prompt
venv\Scripts\activate

# On Windows PowerShell
venv\Scripts\Activate.ps1

# If PowerShell gives an error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` at the beginning of your terminal prompt.

### Step 4: Install Python Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

This will install Django, Django REST Framework, PostgreSQL driver, and other dependencies.

### Step 5: Configure Database Connection

Create a file named `.env` in your project root folder with the following content:

```env
# Database Configuration
PGDATABASE=fleet_db
PGUSER=postgres
PGPASSWORD=your_postgres_password_here
PGHOST=localhost
PGPORT=5432

# Django Secret Key
SESSION_SECRET=your-secret-key-change-this-in-production
```

**Important:** Replace `your_postgres_password_here` with the actual PostgreSQL password you set during installation.

### Step 6: Run Database Migrations

Apply database migrations to create all tables:

```bash
python manage.py migrate
```

You should see output like:
```
Applying contenttypes.0001_initial... OK
Applying auth.0001_initial... OK
...
Applying trips.0001_initial... OK
```

### Step 7: Create Sample Data

Populate the database with test data (drivers, vehicles, jobs):

```bash
python create_sample_data.py
```

This creates:
- Admin user: `admin` / `admin123`
- Driver 1: `john` / `driver123`
- Driver 2: `sarah` / `driver123`
- 2 vehicles
- 3 sample jobs

### Step 8: Run the Django Server

Start the development server:

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

### Step 9: Access the System

Open your browser and go to:

1. **Driver Interface**: http://127.0.0.1:8000/
   - Login as a driver (john / driver123 or sarah / driver123)
   - Start trips, log events, complete jobs
   
2. **Admin Panel**: http://127.0.0.1:8000/admin/
   - Login as admin (admin / admin123)
   - Manage drivers, vehicles, jobs, view all trips
   
3. **API**: http://127.0.0.1:8000/api/
   - Browse REST API endpoints
   - View drivers, vehicles, jobs, trips in JSON format

### Step 10: Run Analytics Dashboard (Optional)

In a **new terminal window** (while Django server is still running):

```bash
# Activate virtual environment first
venv\Scripts\activate

# Run Streamlit dashboard
streamlit run dashboard.py --server.port 8501
```

The dashboard will open automatically in your browser at `http://localhost:8501/`

## Common Issues and Solutions

### Issue 1: PostgreSQL Connection Error

**Error:** `connection to server at "localhost" (::1), port 5432 failed`

**Solution:**
- Make sure PostgreSQL service is running:
  - Open Windows Services (`services.msc`)
  - Find "postgresql-x64-14" (or your version)
  - Right-click and select "Start" if it's not running
- Check your `.env` file has the correct password
- Verify the database `fleet_db` exists in pgAdmin

### Issue 2: Virtual Environment Not Activating

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: Python Not Found

**Error:** `'python' is not recognized as an internal or external command`

**Solution:**
- Reinstall Python and check "Add Python to PATH"
- Or use `py` instead of `python` in commands
- Or add Python to PATH manually:
  1. Search "Environment Variables" in Windows
  2. Edit "Path" variable
  3. Add `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\`

### Issue 4: Port Already in Use

**Error:** `Error: That port is already in use.`

**Solution:**
- Use a different port: `python manage.py runserver 8080`
- Or kill the process using that port:
  ```bash
  # Find process
  netstat -ano | findstr :8000
  # Kill process (replace PID with the number from above)
  taskkill /PID <PID> /F
  ```

### Issue 5: Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'django'`

**Solution:**
- Make sure virtual environment is activated (you should see `(venv)`)
- Run `pip install -r requirements.txt` again

## Development Workflow

### Daily Development

1. Open VS Code
2. Open Terminal and activate virtual environment:
   ```bash
   venv\Scripts\activate
   ```
3. Start Django server:
   ```bash
   python manage.py runserver
   ```
4. Make your changes
5. Test in browser
6. Stop server with `Ctrl+C` when done

### Making Database Changes

If you modify models in `trips/models.py`:

```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

### Creating New Admin User

```bash
python manage.py createsuperuser
```

### Viewing Database

Use **pgAdmin 4** to browse the database:
1. Open pgAdmin
2. Connect to PostgreSQL
3. Navigate to: Servers > PostgreSQL > Databases > fleet_db > Schemas > public > Tables

### Running Tests

```bash
python test_complete_workflow.py
```

## VS Code Recommended Extensions

Install these extensions in VS Code for better development experience:

1. **Python** (Microsoft) - Python language support
2. **Pylance** (Microsoft) - Python language server
3. **Django** (Baptiste Darthenay) - Django template support
4. **PostgreSQL** (Chris Kolkman) - Database management
5. **REST Client** (Huachao Mao) - Test API endpoints

## Project Structure Explained

```
FleetManagement/
├── venv/                      # Virtual environment (don't commit)
├── fleet_management/          # Django project config
│   ├── settings.py           # Main settings
│   ├── urls.py               # URL routing
│   └── wsgi.py               # Server gateway
├── trips/                     # Main Django app
│   ├── models.py             # Database models
│   ├── views.py              # Views and API endpoints
│   ├── serializers.py        # API serializers
│   ├── admin.py              # Admin interface config
│   ├── urls.py               # App URLs
│   ├── templates/            # HTML templates
│   └── migrations/           # Database migrations
├── media/                     # User-uploaded files
├── staticfiles/               # Collected static files
├── manage.py                  # Django management
├── requirements.txt           # Python dependencies
├── dashboard.py               # Streamlit dashboard
├── create_sample_data.py      # Sample data script
└── .env                       # Environment variables (create this)
```

## Tips for Windows Development

1. **Use PowerShell or CMD** - Both work, but PowerShell is recommended
2. **Antivirus** - Add project folder to antivirus exclusions for better performance
3. **File Paths** - Use forward slashes `/` in Python code, works on all systems
4. **Environment Variables** - Use `.env` file instead of Windows environment variables

## Need Help?

Common commands reference:

```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Start Django server
python manage.py runserver

# Start Streamlit dashboard
streamlit run dashboard.py --server.port 8501

# Create admin user
python manage.py createsuperuser

# Load sample data
python create_sample_data.py

# Run tests
python test_complete_workflow.py
```

## Deploying to Production

For production deployment on Windows Server:

1. Use **Gunicorn** (Linux) or **Waitress** (Windows) instead of development server
2. Set `DEBUG = False` in settings.py
3. Configure proper `ALLOWED_HOSTS`
4. Use a proper secret key
5. Serve static files with WhiteNoise or nginx
6. Use proper PostgreSQL with backups
7. Set up SSL certificate

See Django deployment documentation for details.

---

**You're all set!** Start the Django server and begin using the fleet management system. Login as a driver to start logging trips, or as admin to manage the entire fleet.
