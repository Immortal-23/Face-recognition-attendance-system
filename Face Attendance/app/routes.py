from flask import render_template, request, jsonify, redirect, url_for, Response, flash, send_file, session
from datetime import datetime, timedelta
import cv2
import base64
import json
import numpy as np
import io
import csv
import os
from PIL import Image
from functools import wraps
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import (
    get_user_by_username,
    get_all_students,
    update_user,
    delete_user,
    record_attendance,
    get_attendance_history,
    get_attendance_stats,
    get_recent_activities,
    supabase  # Import the Supabase client
)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app):
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            try:
                # Sign in with Supabase Auth
                auth_response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                if auth_response.user:
                    # Get user details from our users table
                    user = get_user_by_username(auth_response.user.email)
                    
                    if user:
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        session['role'] = user['role']
                        logger.info(f"User logged in - Role: {user['role']}")
                        flash('Login successful!', 'success')
                        return redirect(url_for('dashboard'))
                    else:
                        flash('User profile not found!', 'danger')
                        return redirect(url_for('login'))
                else:
                    flash('Invalid email or password!', 'danger')
                    return redirect(url_for('login'))
            except Exception as e:
                logging.error(f"Login error: {str(e)}")
                flash('Login failed. Please try again.', 'danger')
                return redirect(url_for('login'))
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        try:
            # Add more detailed logging
            logger.info(f"User accessing dashboard - Username: {session.get('username')}, Role: {session.get('role')}")
            stats = get_attendance_stats()
            logger.info(f"Dashboard stats retrieved: {stats}")
            
            # Add session debug info
            session_info = {
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'role': session.get('role')
            }
            logger.info(f"Session info: {session_info}")
            
            return render_template('dashboard.html', stats=stats, session_info=session_info)
        except Exception as e:
            logger.error(f"Error in dashboard route: {str(e)}")
            flash('Error loading dashboard statistics.', 'error')
            return render_template('dashboard.html', stats={
                'total_students': 0,
                'present_students': 0,
                'absent_students': 0,
                'student_attendance_rate': 0
            })

    @app.route('/take-attendance')
    @login_required
    def take_attendance():
        try:
            student = get_user_by_username(session['username'])
            return render_template('take_attendance.html', student=student)
        except Exception as e:
            logger.error(f"Error in take_attendance route: {str(e)}")
            flash('Error loading attendance page.', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/record-attendance', methods=['POST'])
    @login_required
    def record_attendance_route():
        try:
            student_id = session['user_id']
            status = request.form.get('status', 'present')
            
            attendance = record_attendance(student_id, status)
            if attendance:
                flash('Attendance recorded successfully!', 'success')
            else:
                flash('Failed to record attendance.', 'error')
            
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Error recording attendance: {str(e)}")
            flash('Error recording attendance.', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/manage-users')
    @login_required
    @admin_required
    def manage_users():
        try:
            students = get_all_students()
            return render_template('manage_users.html', students=students)
        except Exception as e:
            logger.error(f"Error in manage_users route: {str(e)}")
            flash('Error loading user management page.', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/reports')
    @login_required
    def reports():
        try:
            student_id = None if session['role'] == 'admin' else session['user_id']
            attendance_records = get_attendance_history(student_id)
            return render_template('attendance_history.html', records=attendance_records)
        except Exception as e:
            logger.error(f"Error in reports route: {str(e)}")
            flash('Error loading attendance records.', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/api/recent-activities')
    @login_required
    def recent_activities():
        try:
            activities = get_recent_activities()
            return jsonify(activities)
        except Exception as e:
            logger.error(f"Error fetching recent activities: {str(e)}")
            return jsonify([])

    return app 