from flask import Flask
from flask_migrate import Migrate
from app import create_app
from models import db, Tip, User, Appointment

# Create app using the factory
app = create_app()

# Initialize Flask-Migrate **after the app is created**
migrate = Migrate(app, db)

# Optional: make app available for CLI
if __name__ == "__main__":
    app.run(debug=True)
