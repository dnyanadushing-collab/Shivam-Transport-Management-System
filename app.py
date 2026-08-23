from flask import Flask
from config import Config
from extensions import db

from routes import auth
from models import User, Customer, Trip

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

    # Create default admin user if not already exists
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password="admin123"
        )
        db.session.add(admin)
        db.session.commit()
        print("DEFAULT ADMIN CREATED")

app.register_blueprint(auth)

print("APP STARTED SUCCESSFULLY")

if __name__ == "__main__":
    app.run(debug=True)