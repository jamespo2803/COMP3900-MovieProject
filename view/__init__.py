from flask import Flask
from flask_login import LoginManager


login_manager = LoginManager()

def createApp():
    app = Flask(__name__)

    login_manager.init_app(app)

    # Application Configuration
    app.config.from_object('config.Config')

    with app.app_context():
        from view import routes
        from view import auth

        # Register blueprints
        app.register_blueprint(routes.routes_bp)
        app.register_blueprint(auth.auth_bp)

    return app