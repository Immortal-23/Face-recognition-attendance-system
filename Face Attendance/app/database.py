from supabase import create_client
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    logger.error("Supabase URL or key is missing in environment variables")
    logger.error(f"SUPABASE_URL: {supabase_url}")
    logger.error(f"SUPABASE_KEY: {supabase_key and 'Set' or 'Not Set'}")
    raise Exception("Supabase configuration is missing. Please check your .env file.")

logger.info(f"Initializing Supabase client with URL: {supabase_url}")
try:
    supabase = create_client(supabase_url, supabase_key)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise

def get_user_by_username(username_or_email):
    try:
        # Try to find user by email first
        response = supabase.table('users').select('*').eq('email', username_or_email).execute()
        users = response.data
        
        if not users:
            # If not found by email, try username
            response = supabase.table('users').select('*').eq('username', username_or_email).execute()
            users = response.data
            
        return users[0] if users else None
    except Exception as e:
        logger.error(f"Error getting user by username/email: {str(e)}")
        return None

def create_user(username, email, password, role='student'):
    try:
        # Check if username or email already exists
        existing_user = get_user_by_username(username)
        if existing_user:
            raise Exception("Username already exists")
            
        existing_email = get_user_by_username(email)
        if existing_email:
            raise Exception("Email already exists")
            
        # First, create the auth user
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "email_confirm": True  # Auto-confirm email for testing
        })
        
        if not auth_response.user:
            raise Exception("Failed to create auth user")
            
        # Then create the user profile in the users table
        user_data = {
            "id": auth_response.user.id,
            "username": username,
            "email": email,
            "role": role,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table('users').insert(user_data).execute()
        
        if not response.data:
            # If profile creation fails, clean up the auth user
            supabase.auth.admin.delete_user(auth_response.user.id)
            raise Exception("Failed to create user profile")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return None

def get_all_students():
    try:
        response = supabase.table('users').select('*').eq('role', 'student').execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting all students: {str(e)}")
        return []

def update_user(user_id, data):
    try:
        response = supabase.table('users').update(data).eq('id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return None

def delete_user(user_id):
    try:
        # Delete from users table
        response = supabase.table('users').delete().eq('id', user_id).execute()
        
        # Delete from auth.users (if needed)
        supabase.auth.admin.delete_user(user_id)
        
        return True
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return False

def record_attendance(student_id, status='present'):
    try:
        attendance_data = {
            "student_id": student_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = supabase.table('attendance').insert(attendance_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error recording attendance: {str(e)}")
        return None

def get_attendance_history(student_id=None):
    try:
        query = supabase.table('attendance').select(
            'attendance.id, attendance.status, attendance.timestamp, users.username'
        ).join('users', 'attendance.student_id=users.id')
        
        if student_id:
            query = query.eq('student_id', student_id)
            
        response = query.order('timestamp', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting attendance history: {str(e)}")
        return []

def get_attendance_stats():
    try:
        logger.info("Starting to fetch attendance stats...")
        logger.info(f"Supabase URL: {supabase_url}")
        
        # Test Supabase connection
        try:
            # Get total number of users and their roles
            users_response = supabase.table('users').select('*').execute()
            logger.info(f"Raw users response: {users_response}")
            
            if hasattr(users_response, 'error') and users_response.error:
                logger.error(f"Supabase error: {users_response.error}")
                raise Exception(f"Supabase error: {users_response.error}")
                
            users = users_response.data if users_response.data else []
            logger.info(f"Retrieved users data: {users}")
            
            if not users:
                logger.warning("No users found in the database")
            
            total_users = len(users)
            total_students = sum(1 for user in users if user.get('role') == 'student')
            total_admins = sum(1 for user in users if user.get('role') == 'admin')
            logger.info(f"Counted users - Total: {total_users}, Students: {total_students}, Admins: {total_admins}")

            # Get present users for today
            today = datetime.utcnow().date().isoformat()
            logger.info(f"Fetching attendance for date: {today}")
            
            present_response = supabase.table('attendance').select(
                'attendance.id, attendance.student_id'
            ).eq('status', 'present').gte('timestamp', today).execute()
            
            logger.info(f"Raw attendance response: {present_response}")
            
            if hasattr(present_response, 'error') and present_response.error:
                logger.error(f"Supabase error: {present_response.error}")
                raise Exception(f"Supabase error: {present_response.error}")
            
            present_records = present_response.data if present_response.data else []
            logger.info(f"Retrieved attendance records: {present_records}")
            
            present_student_ids = set(record.get('student_id') for record in present_records if record.get('student_id'))
            logger.info(f"Present student IDs: {present_student_ids}")
            
            # Count present students
            present_students = sum(1 for user in users 
                                 if user.get('role') == 'student' and user.get('id') in present_student_ids)
            logger.info(f"Counted {present_students} present students today")

            # Calculate attendance rates
            student_attendance_rate = (present_students / total_students * 100) if total_students > 0 else 0
            logger.info(f"Calculated attendance rate: {student_attendance_rate}%")

            stats = {
                'total_users': total_users,
                'total_students': total_students,
                'total_admins': total_admins,
                'present_students': present_students,
                'absent_students': total_students - present_students,
                'student_attendance_rate': round(student_attendance_rate, 2)
            }
            logger.info(f"Final stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error in Supabase query: {str(e)}")
            logger.exception("Full traceback:")
            raise  # Re-raise to be caught by outer try-except
            
    except Exception as e:
        logger.error(f"Error getting attendance stats: {str(e)}")
        logger.exception("Full traceback:")
        
        # Check Supabase connection
        if not supabase_url or not supabase_key:
            logger.error("Supabase URL or key is missing")
        
        return {
            'total_users': 0,
            'total_students': 0,
            'total_admins': 0,
            'present_students': 0,
            'absent_students': 0,
            'student_attendance_rate': 0
        }

def get_recent_activities():
    try:
        response = supabase.table('attendance').select(
            'attendance.status, attendance.timestamp, users.username'
        ).join('users', 'attendance.student_id=users.id').order('timestamp', desc=True).limit(5).execute()
        
        return [{
            'name': activity['username'],
            'timestamp': activity['timestamp'],
            'status': activity['status']
        } for activity in response.data]
    except Exception as e:
        logger.error(f"Error getting recent activities: {str(e)}")
        return [] 