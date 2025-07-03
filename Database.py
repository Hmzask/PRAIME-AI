# ---------------------------------------------IMPORTS------------------------------------------------------
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#---------------------------------------------INITTIALISATION---------------------------------------------

app = Flask(__name__) 

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://myapp_user:root@localhost/prime_base'
app.config['SQLALCHEMY_BINDS'] = {'sqlite_db':'sqlite:///demo.db'}

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#---------------------------------------------DATABASE SCHEMA---------------------------------------------

class User_cred(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    username = db.Column(db.String(100))
    email =   db.Column(db.String(100))
    password = db.Column(db.String(100),unique=True)

class Cars(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    Brand = db.Column(db.String(100))
    Model = db.Column(db.String(100))
    price =   db.Column(db.String(100))
    year = db.Column(db.Integer,unique=True)

def addtocars():
    entries = [
        ('Bugatti','Centodiecci','$90,000,00',2024),
        ('BMW','m5','$150,000',2023),
        ('Pagani','Zonda','$250,000',2018),
        ('Koeiniggseg','regera','$50,000,00',1991)

    ]
    for Brand,Model,price,year in entries:
         aleady_there = Cars.query.filter_by(Brand=Brand,Model=Model,price=price,year=year).first()
         if not aleady_there:
             adding = Cars(Brand=Brand,Model=Model,price=price,year=year)
             db.session.add(adding)
             db.session.commit()

