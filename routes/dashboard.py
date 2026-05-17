from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    habits = [h for h in current_user.habits if h.is_active]
    total = len(habits)
    done_today = sum(1 for h in habits if h.checked_today())
    best_streak = max((h.current_streak() for h in habits), default=0)
    return render_template('dashboard.html',
                           habits=habits,
                           total=total,
                           done_today=done_today,
                           best_streak=best_streak,
                           today=date.today().strftime('%A, %d %B %Y'))
