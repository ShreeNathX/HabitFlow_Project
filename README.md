# HabitFlow - Habit Streak Tracker

A Flask web app to track daily habits, build streaks, and visualize consistency.

## Setup & Run

```bash
# 1. Install dependencies
pip install flask flask-login flask-sqlalchemy bcrypt

# 2. Run the app
python app.py

# 3. Open in browser
http://localhost:5000
```

## Features
- Register / Login (bcrypt passwords)
- Add, edit, delete habits with icons and color themes
- One-click daily check-in (AJAX, no page reload)
- Streak counter (current + longest)
- 35-day heat-map calendar
- Weekly bar chart (Chart.js)
- CSV export of all check-in data

## Project Structure
```
habit_tracker/
├── app.py              # Flask app factory
├── models.py           # SQLAlchemy models (User, Habit, CheckIn)
├── routes/
│   ├── auth.py         # Register, Login, Logout
│   ├── dashboard.py    # Main dashboard view
│   └── habits.py       # CRUD + check-in + export
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── habit_detail.html
│   └── habit_form.html
└── static/
    ├── css/style.css
    └── js/main.js, detail.js
```

## Tech Stack
- Backend: Python 3 + Flask
- Database: SQLite + SQLAlchemy
- Auth: Flask-Login + bcrypt
- Charts: Chart.js 4
- Frontend: HTML5 + CSS3 + Vanilla JS

## Test Login
Username: testuser | Password: test123
