# Personal Budget System

A Django-based web application designed to help users track expenses, set budgets, and manage their personal finances effectively.

## Project Overview

The Personal Budget System allows users to:
- Create and manage budget cycles
- Track expenses by category
- Monitor daily spending limits
- Maintain a user profile with avatar support
- View spending history and analytics

## Project Structure

```
Personal-Budget-System-main/
├── budgetapp/                      # Django project root directory
│   ├── budgetapp/                  # Project settings and configuration
│   │   ├── settings.py            # Django settings (database, apps, middleware)
│   │   ├── urls.py                # Main URL routing configuration
│   │   ├── wsgi.py                # WSGI application entry point
│   │   └── asgi.py                # ASGI application entry point
│   ├── users/                      # Main Django app for budget and user management
│   │   ├── models.py              # Database models (Expense, BudgetCycle, Profile)
│   │   ├── views.py               # View logic for handling requests
│   │   ├── urls.py                # App-specific URL routes
│   │   ├── forms.py               # Django forms for user input
│   │   ├── admin.py               # Django admin configuration
│   │   ├── apps.py                # App configuration
│   │   ├── tests.py               # Unit tests
│   │   └── templates/             # HTML templates for views
│   ├── static/                     # Static files (CSS, JavaScript, images)
│   ├── media/                      # User-uploaded files (profile pictures)
│   ├── manage.py                  # Django CLI utility for administrative tasks
│   └── db.sqlite3                 # SQLite database
├── .gitignore                      # Git ignore configuration
└── README.md                       # This file
```

## Key Components

### Models (budgetapp/users/models.py)

**1. Expense**
- Tracks individual expense transactions
- Fields: user, category, amount, date, expense_date
- Categories: Food, Transport, Study, Shopping, Bills, Other

**2. BudgetCycle**
- Manages budget periods with spending limits
- Fields: user, total_amount, start_date, end_date, daily_limit

**3. Profile**
- Extends user profile with avatar support
- Fields: user, image (profile picture)

## Technologies Used

### Backend
- **Django 3.2** - Web framework for building the application
- **Python 3** - Programming language
- **SQLite** - Lightweight database for data storage

### Frontend
- **HTML** - Markup language for web pages
- **CSS** - Styling and layout
- **Bootstrap 4** - CSS framework for responsive design via `crispy-bootstrap4`

### Libraries & Packages
- **Django Crispy Forms** - Enhanced form rendering with Bootstrap styling
- **Crispy Bootstrap 4** - Bootstrap 4 template pack for crispy forms
- **Pillow** - Image processing for profile picture uploads
