import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Flask configuration
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
SESSION_TYPE = 'filesystem' 