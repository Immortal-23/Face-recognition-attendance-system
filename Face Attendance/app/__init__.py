from flask import Flask
from flask_session import Session

def create_app():
    app = Flask(__name__)
    
    # Configure Flask-Session
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    
    # Set secret key
    from .config import SECRET_KEY
    app.secret_key = SECRET_KEY
    
    # Initialize routes
    with app.app_context():
        from .routes import init_routes
        init_routes(app)
    
    return app 