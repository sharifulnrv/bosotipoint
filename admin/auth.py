"""Admin authentication routes."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models import User
from . import admin_bp


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        flash('ভুল ইউজারনেম বা পাসওয়ার্ড।', 'error')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))
