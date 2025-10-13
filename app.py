from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from routes import main_bp, auth_bp, clinic_bp, mother_bp
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    # ✅ FIX: Point Flask-Login to the correct login route
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(clinic_bp, url_prefix="/clinic")
    app.register_blueprint(mother_bp, url_prefix="/mother")

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
# Note: Debug mode should be turned off in production