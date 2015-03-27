from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from conf import *
import random, time, string

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
