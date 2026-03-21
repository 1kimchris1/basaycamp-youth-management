# CRCCIMI Youth Camp Management System

A secure Django-based management system for youth camp administration with authentication and role-based access control.

## Features

- **Secure Authentication**: Django built-in authentication system
- **Role-Based Access**: Admin and Staff user roles
- **Modern UI**: Responsive design with Bootstrap 5
- **Protected Routes**: All internal pages require authentication
- **Dashboard**: Overview with key statistics and metrics
- **Module Management**: Participants, Churches, Activities, Finances, and Scoring

## Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (default Django)
- **Authentication**: Django built-in authentication
- **Templates**: Django Template Engine

## Installation

1. **Clone/Download the project to your local machine**

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (admin account):**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

6. **Create staff users (optional):**
   ```bash
   python manage.py shell
   ```
   Then run:
   ```python
   from django.contrib.auth.models import User
   # Create staff user
   staff_user = User.objects.create_user('staff1', 'staff1@example.com', 'password123')
   staff_user.is_staff = True
   staff_user.save()
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Login with your created credentials

## Default User Roles

### Admin
- Full system access
- Can manage all modules
- Access to Admin Scoring System

### Staff
- Can manage participants
- Can manage activities
- Can update scores
- Can record expenses

## Project Structure

```
Basaycamp/
├── manage.py
├── requirements.txt
├── README.md
├── basaycamp_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── youthcamp/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── tests.py
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── participants.html
    ├── churches.html
    ├── activities.html
    ├── finances.html
    └── admin_scoring.html
```

## Security Features

- CSRF protection enabled
- Password hashing (Django default)
- Session-based authentication
- Protected routes with login required
- Input validation and sanitization

## Usage

1. **Login**: Access the system through the login page
2. **Dashboard**: View overview statistics and quick actions
3. **Navigation**: Use the navigation bar to access different modules
4. **Logout**: Click logout in the user dropdown menu

## Development

To add new features:

1. Create new views in `youthcamp/views.py`
2. Add URL patterns in `youthcamp/urls.py`
3. Create templates in the `templates/` directory
4. Update models in `youthcamp/models.py` if needed

## Deployment Notes

- Change `SECRET_KEY` in `settings.py` for production
- Set `DEBUG = False` in production
- Configure appropriate database settings
- Set up proper static file serving
- Configure allowed hosts

## Support

Developed by: STEVEN KIM S. IB-IB
