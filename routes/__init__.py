# routes/__init__.py

from .main_routes import main_bp
from .auth_routes import auth_bp
from .clinic_routes import clinic_bp
from .mother_routes import mother_bp
from .admin_routes import admin_bp
from .admin_auth_routes import admin_auth_bp

__all__ = ["main_bp", "auth_bp", "clinic_bp", "mother_bp", "admin_bp", "admin_auth_bp"]
