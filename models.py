from flask.ext.sqlalchemy import SQLAlchemy
from config import *

db = SQLAlchemy()
		
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100))
	password_hash = db.Column(db.String(100))

	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)
	
	def add(self):
		db.session.add(self)
		db.session.commit()

	def dict(self):
		return {'username': self.username}

class ClientModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(FIRSTNAME_MAXLEN))
    surname = db.Column(db.String(SURNAME_MAXLEN))
    state = db.Column(db.String(STATE_MAXLEN))
    balance = db.Column(db.Integer)
    
    def __init__(self, name, surname, state, balance):
        self.name = name
        self.surname = name
        self.state = state
        self.balance = balance
        
    def add(self):
        db.session.add(client)
        db.session.commit()

    def __repr__(self):
        return ('name: ' + self.name + ', state: ' + self.state)
        
    def dict(self):
		return {'id': self.id, 'name':self.name,'surname':self.surname, 'balance':self.balance, 'state':self.state}
		
class Token(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	start = db.Column(db.Integer)
	token = db.Column(db.String(TOKEN_LEN))
	
	def add(self):
		db.session.add(s)
		db.session.commit()
	
	def dict(self):
		return {'token': self.token}
