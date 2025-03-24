from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    login.init_app(app)
    mail.init_app(app)
    
    from financetracker.main import main_bp
    app.register_blueprint(main_bp)
    
    from .auth import auth_bp
    app.register_blueprint(auth_bp)
    
    return app

from . import models