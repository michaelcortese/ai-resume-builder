from flask import Flask
from flask_cors import CORS
import logging
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app 