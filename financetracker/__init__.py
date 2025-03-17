from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='no-secret-now'
    )
    
    from financetracker.main import main_bp
    app.register_blueprint(main_bp)
    
    return app