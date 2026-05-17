from extensions import db
from flask_login import UserMixin
from datetime import date, timedelta


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at    = db.Column(db.DateTime, default=db.func.now())
    habits        = db.relationship('Habit', backref='owner', lazy=True,
                                    cascade='all, delete-orphan')


class Habit(db.Model):
    __tablename__ = 'habits'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name       = db.Column(db.String(120), nullable=False)
    icon       = db.Column(db.String(10), default='⚡')
    color      = db.Column(db.String(20), default='blue')
    created_at = db.Column(db.Date, default=date.today)
    is_active  = db.Column(db.Boolean, default=True)
    checkins   = db.relationship('CheckIn', backref='habit', lazy=True,
                                  cascade='all, delete-orphan')

    def checked_today(self):
        return CheckIn.query.filter_by(
            habit_id=self.id, checked_date=date.today()
        ).first() is not None

    def current_streak(self):
        checked = sorted(
            {c.checked_date for c in self.checkins}, reverse=True
        )
        if not checked:
            return 0
        streak, cursor = 0, date.today()
        for d in checked:
            if d == cursor or d == cursor - timedelta(days=1):
                streak += 1
                cursor = d
            else:
                break
        return streak

    def longest_streak(self):
        checked = sorted({c.checked_date for c in self.checkins})
        if not checked:
            return 0
        best, run = 1, 1
        for i in range(1, len(checked)):
            if checked[i] - checked[i-1] == timedelta(days=1):
                run += 1
                best = max(best, run)
            else:
                run = 1
        return best

    def heatmap_data(self):
        today = date.today()
        days = {(today - timedelta(days=i)).isoformat(): 0 for i in range(34, -1, -1)}
        for c in self.checkins:
            key = c.checked_date.isoformat()
            if key in days:
                days[key] = 1
        return days

    def weekly_data(self):
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        checked = {c.checked_date for c in self.checkins}
        return [(1 if monday + timedelta(days=i) in checked else 0) for i in range(7)]


class CheckIn(db.Model):
    __tablename__ = 'checkins'
    __table_args__ = (
        db.UniqueConstraint('habit_id', 'checked_date', name='uq_habit_date'),
    )
    id           = db.Column(db.Integer, primary_key=True)
    habit_id     = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checked_date = db.Column(db.Date, nullable=False, default=date.today)