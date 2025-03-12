from app.database import supabase
from werkzeug.security import generate_password_hash

def init_db():
    try:
        # Create an admin user for testing
        admin_data = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': generate_password_hash('admin123'),
            'role': 'admin'
        }
        
        # Check if admin already exists
        existing_admin = supabase.table('users').select('*').eq('username', 'admin').execute()
        
        if not existing_admin.data:
            result = supabase.table('users').insert(admin_data).execute()
            if result.data:
                print("Admin user created successfully!")
                print("Username: admin")
                print("Password: admin123")
                print(f"Admin ID: {result.data[0]['id']}")
            else:
                print("Failed to create admin user")
        else:
            print("Admin user already exists!")
            print(f"Admin ID: {existing_admin.data[0]['id']}")
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

if __name__ == '__main__':
    init_db() 