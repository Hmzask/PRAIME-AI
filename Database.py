# ---------------------------------------------IMPORTS------------------------------------------------------
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    

# class User_prompt(db.Model):
#     __tablename__ = 'user_prompts'

#     prompt_id = db.Column(db.Integer, primary_key=True)
#     id = db.Column(db.Integer, db.ForeignKey('user_credentials.d'),nullable=False)
#     prompt = db.Column(db.Text, nullable=False)
#     response = db.Column(db.Text, nullable=True)

    
    def to_dict(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'username': self.username,
            'email': self.email,
            'auth_provider': self.auth_provider,
            'google_id':self.google_id,
            'is_active': self.is_active,
        }


        

