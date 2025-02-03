from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from datetime import timedelta
import os

# Initialize extensions
mail = Mail()
db = SQLAlchemy()

# Database file name
DB_NAME = 'database.sqlite3'

def create_database(app):
    """Create the database if it doesn't exist."""
    if not os.path.exists(DB_NAME):
        with app.app_context():
            db.create_all()
            print('Database Created')

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # App configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'hbnwdvbn ajnbsjn ahe')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Mail Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER', 'afindify@gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS', 'ifga hpug xgrr adbp')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER', 'afindify@gmail.com')

    # Session configuration for OTP
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
    app.config['SESSION_TYPE'] = 'filesystem'  # Optional: for more robust session handling

    # Initialize extensions
    mail.init_app(app)
    db.init_app(app)

    # Error handling
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        from .models import Customer  # Lazy import to avoid circular imports
        return Customer.query.get(int(id))

    # Register Blueprints
    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    # Create database if it doesn't exist
    create_database(app)

    return app