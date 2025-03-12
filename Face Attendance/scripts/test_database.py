import os
import sys
import uuid
from datetime import datetime
import logging

# Add the parent directory to the Python path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import supabase, logger

def test_database_connection():
    try:
        # Test users table
        logger.info("Testing users table...")
        
        # Generate test data
        test_student = {
            'id': str(uuid.uuid4()),
            'username': f'test_student_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'role': 'student',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Insert test student
        logger.info(f"Inserting test student: {test_student}")
        response = supabase.table('users').insert(test_student).execute()
        
        if response.data:
            logger.info(f"Successfully inserted test student: {response.data}")
            
            # Test attendance table
            logger.info("Testing attendance table...")
            
            attendance_record = {
                'student_id': test_student['id'],
                'status': 'present',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Inserting test attendance record: {attendance_record}")
            response = supabase.table('attendance').insert(attendance_record).execute()
            
            if response.data:
                logger.info(f"Successfully inserted test attendance record: {response.data}")
            else:
                logger.error("Failed to insert test attendance record")
        else:
            logger.error("Failed to insert test student")
            
        # Query all students
        logger.info("Querying all students...")
        response = supabase.table('users').select('*').eq('role', 'student').execute()
        logger.info(f"Found {len(response.data)} students: {response.data}")
        
        # Query today's attendance
        logger.info("Querying today's attendance...")
        today = datetime.utcnow().date().isoformat()
        response = supabase.table('attendance').select('*').gte('timestamp', today).execute()
        logger.info(f"Found {len(response.data)} attendance records for today: {response.data}")
        
    except Exception as e:
        logger.error(f"Error testing database: {str(e)}")
        logger.exception("Full traceback:")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_database_connection() 