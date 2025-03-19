# GoTable - Restaurant Table Booking System

A Django-based restaurant table booking system that allows users to search for restaurants, view available tables, make bookings, and manage reservations.

## Features

- User Authentication (Customer and Restaurant Admin roles)
- Restaurant Management
- Table Management
- Booking System
- Custom Admin Panel
- RESTful API with JWT Authentication
- CORS Support
- Media File Handling

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gotable
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- POST `/api/register/` - Register a new user
- POST `/api/token/` - Obtain JWT token
- POST `/api/token/refresh/` - Refresh JWT token

### Restaurants
- GET `/api/restaurants/` - List all restaurants
- POST `/api/restaurants/` - Create a new restaurant (Restaurant Admin only)
- GET `/api/restaurants/{id}/` - Get restaurant details
- PUT `/api/restaurants/{id}/` - Update restaurant (Restaurant Admin only)
- DELETE `/api/restaurants/{id}/` - Delete restaurant (Restaurant Admin only)

### Tables
- GET `/api/tables/` - List all tables
- POST `/api/tables/` - Create a new table (Restaurant Admin only)
- GET `/api/tables/{id}/` - Get table details
- PUT `/api/tables/{id}/` - Update table (Restaurant Admin only)
- DELETE `/api/tables/{id}/` - Delete table (Restaurant Admin only)

### Bookings
- GET `/api/bookings/` - List user's bookings
- POST `/api/bookings/` - Create a new booking
- GET `/api/bookings/{id}/` - Get booking details
- PUT `/api/bookings/{id}/` - Update booking
- DELETE `/api/bookings/{id}/` - Cancel booking
- POST `/api/bookings/{id}/confirm/` - Confirm booking (Restaurant Admin only)
- POST `/api/bookings/{id}/cancel/` - Cancel booking

## Admin Panel

Access the admin panel at `/admin/` with your superuser credentials. The admin panel provides:

- User Management
- Restaurant Management
- Table Management
- Booking Management
- Custom Dashboard

## Development

### Project Structure
```
gotable/
├── gotable/          # Project settings
├── myapp/           # Main application
│   ├── models.py    # Database models
│   ├── views.py     # API views
│   ├── urls.py      # URL routing
│   ├── serializers.py # API serializers
│   └── admin.py     # Admin interface
├── static/          # Static files
├── media/           # User-uploaded files
├── templates/       # HTML templates
└── manage.py        # Django management script
```

### Running Tests
```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 