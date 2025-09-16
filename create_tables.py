from app import app
from models.db import db

# The models need to be imported so that SQLAlchemy knows about them
from models.model import User, Message

with app.app_context():
    db.create_all()

print("Database tables created successfully.")