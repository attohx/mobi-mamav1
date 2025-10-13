# routes/__init__.py

from .main_routes import main_bp
from .auth_routes import auth_bp
from .clinic_routes import clinic_bp
from .mother_routes import mother_bp

__all__ = ["main_bp", "auth_bp", "clinic_bp", "mother_bp"]
