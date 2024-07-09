from flask import Flask
from app.config import Config
from app.extensions import db, migrate
from flask import render_template
from datetime import timedelta

def create_app(config_class=Config):
    app = Flask(__name__)
    app.secret_key = '20120598'
    app.permanent_session_lifetime = timedelta(minutes=30)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    app.register_error_handler(404, (lambda e: render_template('404.html')))

    return app
