from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user
from datetime import date
import csv, io
from extensions import db
from models import Habit, CheckIn

habits_bp = Blueprint('habits', __name__)

ICONS = ['⚡','📚','💧','🏃','🧘','🍎','💪','🎨','🎵','🌿','☀️','🛌','✍️','🧹','🚴']
COLORS = ['blue','purple','teal','coral','amber','green','pink']


@habits_bp.route('/habits/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        icon  = request.form.get('icon', '⚡')
        color = request.form.get('color', 'blue')
        if not name:
            flash('Habit name is required.', 'error')
            return render_template('habit_form.html', icons=ICONS, colors=COLORS, habit=None)
        habit = Habit(user_id=current_user.id, name=name, icon=icon, color=color)
        db.session.add(habit)
        db.session.commit()
        flash(f'Habit "{name}" added!', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('habit_form.html', icons=ICONS, colors=COLORS, habit=None)


@habits_bp.route('/habits/<int:habit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        icon  = request.form.get('icon', habit.icon)
        color = request.form.get('color', habit.color)
        if not name:
            flash('Habit name is required.', 'error')
            return render_template('habit_form.html', icons=ICONS, colors=COLORS, habit=habit)
        habit.name  = name
        habit.icon  = icon
        habit.color = color
        db.session.commit()
        flash('Habit updated.', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('habit_form.html', icons=ICONS, colors=COLORS, habit=habit)


@habits_bp.route('/habits/<int:habit_id>/delete', methods=['POST'])
@login_required
def delete(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    habit.is_active = False
    db.session.commit()
    flash(f'Habit "{habit.name}" removed.', 'success')
    return redirect(url_for('dashboard.index'))


@habits_bp.route('/habits/<int:habit_id>/checkin', methods=['POST'])
@login_required
def checkin(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    if habit.checked_today():
        return jsonify({'status': 'already', 'message': 'Already done today!',
                        'streak': habit.current_streak()})
    c = CheckIn(habit_id=habit_id, user_id=current_user.id, checked_date=date.today())
    db.session.add(c)
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'Checked in!',
                    'streak': habit.current_streak(),
                    'longest': habit.longest_streak()})


@habits_bp.route('/habits/<int:habit_id>/detail')
@login_required
def detail(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    return render_template('habit_detail.html',
                           habit=habit,
                           heatmap=habit.heatmap_data(),
                           weekly=habit.weekly_data())


@habits_bp.route('/export')
@login_required
def export_csv():
    habits = [h for h in current_user.habits if h.is_active]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Habit', 'Icon', 'Date Checked In', 'Current Streak', 'Longest Streak'])
    for h in habits:
        for c in sorted(h.checkins, key=lambda x: x.checked_date):
            writer.writerow([h.name, h.icon, c.checked_date.isoformat(),
                             h.current_streak(), h.longest_streak()])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=habits_export.csv'})
