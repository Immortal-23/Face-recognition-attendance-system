import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("Error: Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

def create_user(username, email, password, role='student'):
    try:
        # First, create the auth user
        print(f"Creating auth user with email: {email}")
        auth_user = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if not auth_user.user:
            print("Error: Failed to create auth user")
            return None
            
        print("Auth user created successfully")
        
        # Then create the user profile
        user_data = {
            "id": auth_user.user.id,
            "username": username,
            "email": email,
            "role": role,
            "created_at": datetime.utcnow().isoformat()
        }
        
        print(f"Creating user profile for {username} with role: {role}")
        response = supabase.table('users').insert(user_data).execute()
        
        if response.data:
            print(f"Successfully created {role}: {username}")
            return response.data[0]
        else:
            print("Error: Failed to create user profile")
            return None
            
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return None

def main():
    print("Create new user/admin in Supabase")
    print("--------------------------------")
    
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    role = input("Enter role (student/admin): ").strip().lower()
    
    if role not in ['student', 'admin']:
        print("Error: Role must be either 'student' or 'admin'")
        return
        
    if not all([username, email, password]):
        print("Error: All fields are required")
        return
        
    user = create_user(username, email, password, role)
    
    if user:
        print("\nUser created successfully!")
        print("User details:")
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Role: {user['role']}")
    else:
        print("\nFailed to create user")

if __name__ == "__main__":
    main() 