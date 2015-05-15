from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from conf import *
import random
import time
import string

db = SQLAlchemy()
		
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(USERNAME_MAXLEN))
    password_hash = db.Column(db.String(PASSWORD_HASH_MAXLEN))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
	
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_user_by_name(name):
        return User.query.filter(User.username == name).first()
        
    @staticmethod
    def is_user_exists(name):
        return len(User.query.filter(User.username == name).all()) != 0

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
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod    
    def paginate_clients(page, per_page):
		if not page: page = DEFAULT_START_PAGE
		if not per_page: per_page = DEFAULT_PER_PAGE
		if per_page > MAX_PER_PAGE: per_page = MAX_PER_PAGE
		return ClientModel.query.paginate(page, per_page, True).items
    
    @staticmethod
    def get_client_by_id(client_id):
        return ClientModel.query.get(client_id)

    def __repr__(self):
        return ('name: ' + self.name + ', state: ' + self.state)
        
    def dict(self):
		return {'id': self.id, 'name':self.name,'surname':self.surname, 'balance':self.balance, 'state':self.state}
		
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer)
    token = db.Column(db.String(TOKEN_LEN))
    
    def __init__(self):
        self.start = int(round(time.time()))
        self.token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
        db.session.add(self)
        db.session.commit()

    def dict(self):
        return {'token': self.token}

    @staticmethod
    def check_token(token):
        token = Token.query.filter(Token.token == token).first()
        if (token):
            if (time.time() - token.start) < TOKEN_TTL:
                return (True, 'Success')
            else: return (False, 'Token expired')
        else: return (False, 'Unauthorized')
        
class Company(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userslist = db.Column(db.String)
	
	def __init__(self, userslist):
		self.userslist = userslist
		db.session.add(self)
		db.session.commit()
		
	def dict(self):
		return {'id': self.id, 'userslist': self.userslist}
	
	@staticmethod
	def get_all():
		comp_list = Company.query.all()
		returnarr = []
		for comp in comp_list:
			returnarr.append({comp.id: comp.userslist})
		return returnarr
	
		
class Temp_ulist(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userslist = db.Column(db.String)
	sid = db.Column(db.String(TOKEN_LEN))
	
	@staticmethod
	def find_by_sid(sid):
		return Temp_ulist.query.filter(Temp_ulist.sid == sid).first()
	
	def __init__(self, sid, name):
		self.userslist = name
		self.sid = sid
		db.session.add(self)
		db.session.commit()
	
	def append(self, string):
		self.userslist += ', ' + string
		db.session.add(self)
		db.session.commit()
		
	def string(self):
		return userslist
		
	def delete(self):
		db.session.delete(self)
		db.session.commit()
		
class SequenceID(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sequenceid = db.Column(db.String(TOKEN_LEN))

	def __init__(self):
		self.sequenceid = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	@staticmethod
	def find_sequence(sequenceid):
		return SequenceID.query.filter(SequenceID.sequenceid == sequenceid).first()
