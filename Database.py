# ---------------------------------------------IMPORTS------------------------------------------------------
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#---------------------------------------------INITIALIZATION---------------------------------------------

app = Flask(__name__) 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://myapp_user:root@localhost:5432/prime_base"
app.config['SQLALCHEMY_BINDS'] = {'sqlite_db': 'sqlite:///demo.db'}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#---------------------------------------------DATABASE SCHEMA---------------------------------------------

class User_cred(db.Model):
    __tablename__ = 'user_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=True)  # Nullable for OAuth users
    auth_provider = db.Column(db.String(20), default='form')  # 'form' or 'google'
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'username': self.username,
            'email': self.email,
            'auth_provider': self.auth_provider,
            'is_active': self.is_active
        }

with app.app_context():
        db.create_all()
        

