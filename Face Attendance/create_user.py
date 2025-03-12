import os
import sys
import re
import json
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')  # Use service role key for admin operations

if not supabase_url or not supabase_key:
    print("Error: Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in your .env file")
    sys.exit(1)

print(f"Using Supabase URL: {supabase_url}")
print(f"Service key starts with: {supabase_key[:10]}...")

supabase = create_client(supabase_url, supabase_key)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    return len(password) >= 6

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def create_user(username, email, password, role='student'):
    try:
        if not is_valid_email(email):
            print("Error: Invalid email format")
            return None
            
        if not is_valid_password(password):
            print("Error: Password must be at least 6 characters long")
            return None
            
        # First, create the auth user
        print(f"Creating auth user with email: {email}")
        auth_data = {
            "email": email,
            "password": password,
            "email_confirm": True
        }
        print(f"Auth request data: {json.dumps(auth_data, indent=2)}")
        
        auth_user = supabase.auth.admin.create_user(auth_data)
        print(f"Auth response: {json.dumps(auth_user.model_dump(), cls=DateTimeEncoder, indent=2)}")
        
        if not auth_user.user:
            print("Error: Failed to create auth user")
            return None
            
        print("Auth user created successfully")
        print(f"User ID: {auth_user.user.id}")
        
        # Then create the user profile
        user_data = {
            "id": auth_user.user.id,
            "username": username,
            "email": email,
            "role": role,
            "created_at": datetime.utcnow().isoformat()
        }
        
        print(f"\nCreating user profile with data: {json.dumps(user_data, indent=2)}")
        response = supabase.table('users').insert(user_data).execute()
        print(f"Database response: {json.dumps(response.model_dump(), cls=DateTimeEncoder, indent=2)}")
        
        if response.data:
            print(f"Successfully created {role}: {username}")
            return response.data[0]
        else:
            print("Error: Failed to create user profile")
            return None
            
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        if hasattr(e, 'message'):
            print(f"Error message: {e.message}")
        return None

def main():
    print("\nCreate new user/admin in Supabase")
    print("--------------------------------")
    
    while True:
        username = input("\nEnter username (3-30 characters): ").strip()
        if 3 <= len(username) <= 30:
            break
        print("Username must be between 3 and 30 characters")
    
    while True:
        email = input("Enter email: ").strip()
        if is_valid_email(email):
            break
        print("Please enter a valid email address")
    
    while True:
        password = input("Enter password (min 6 characters): ").strip()
        if is_valid_password(password):
            break
        print("Password must be at least 6 characters long")
    
    while True:
        role = input("Enter role (student/admin): ").strip().lower()
        if role in ['student', 'admin']:
            break
        print("Role must be either 'student' or 'admin'")
    
    print("\nCreating user with the following details:")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Role: {role}")
    
    confirm = input("\nConfirm creation? (y/n): ").strip().lower()
    if confirm != 'y':
        print("User creation cancelled")
        return
        
    user = create_user(username, email, password, role)
    
    if user:
        print("\nUser created successfully!")
        print("User details:")
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Role: {user['role']}")
        print("\nEmail is auto-confirmed for testing. User can log in immediately.")
    else:
        print("\nFailed to create user")

if __name__ == "__main__":
    main() 