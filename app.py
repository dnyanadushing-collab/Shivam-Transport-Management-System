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

app.register_blueprint(auth)
print("APP STARTED SUCCESSFULLY")

if __name__ == "__main__":
    app.run(debug=True)