#!/home/q/web/rest/venv/bin/python


from flask import Flask, jsonify
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.mongoalchemy import MongoAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
import os, string, random, time
from functools import wraps
from passlib.apps import custom_app_context as pwd_context

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('pwd', type=str)
parser.add_argument('surname', type=str)
parser.add_argument('state', type=str)
parser.add_argument('change-balance', type=int)
parser.add_argument('session', type=str)
parser.add_argument('balance', type=int)

def get_client(client_id):
	if ClientModel.query.get(client_id) is None:
		abort(404, message="Client {} doesn't exist".format(client_id))
	return ClientModel.query.get(client_id)		
		
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100))
	password_hash = db.Column(db.String(100))

	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

	def dict(self):
		return {'username': self.username}

class Sess(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	start = db.Column(db.Integer)
	session = db.Column(db.String(30))
	
	def dict(self):
		return {'session': self.session}
		
def login_required(session):
	session = Sess.query.filter(Sess.session == session).first()
	if (session):
		if (time.time() - session.start) < 60:
			return True
		abort (400, message = 'Session expired')
	abort (403)

class ClientModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    state = db.Column(db.String(10))
    balance = db.Column(db.Integer)
    
    def __init__(self, name, surname, state, balance):
        self.name = name
        self.surname = name
        self.state = state
        self.balance = balance

    def __repr__(self):
        return ('name: ' + self.name + ', state: ' + self.state)
        
    def dict(self):
		return {'id': self.id, 'name':self.name,'surname':self.surname, 'balance':self.balance, 'state':self.state}

class Client(Resource):
	def get(self, client_id):
		return get_client(client_id).dict()

	def delete(self, client_id):
		args = parser.parse_args()
		if (login_required(args['session'])):
			db.session.delete(get_client(client_id))
			db.session.commit()
			return '', 204
		return 403

	def put(self, client_id):
		args = parser.parse_args()
		if (login_required(args['session'])):
			abort_if_client_doesnt_exist(client_id)
			args = parser.parse_args()
			client = ClientModel.query.get(client_id)
			client.state = args['state']
			return client.dict()
		return 403

class ClientsList(Resource):
	def get(self):
		method_decorators=[login_required]
		args = parser.parse_args()
		print login_required(args['session'])
		if (login_required(args['session'])):
			clientList = []
			page = 1
			ipp = 10
			paginate = ClientModel.query.paginate(page, ipp)
			for client in ClientModel.query.all():
				clientList.append(client.dict())
			return {"clients": clientList}
		else:
			abort (403)
        
	def post(self):
		args = parser.parse_args()
		if (login_required(args['session'])):
			client = ClientModel(name=args["name"], state=args["state"], surname=args["surname"], balance=args['balance'])
			db.session.add(client)
			db.session.commit()
			return client.dict(), 201
		abort(403)
		
class Login(Resource):
	def get(self):
		args = parser.parse_args()
		name = args['name']
		pwd = args['pwd']
		user = User.query.filter(User.username == name).first()
		if (user):
			if (user.verify_password(pwd)):
				start = int(round(time.time()))
				session = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
				s = Sess(start = start, session = session)
				db.session.add(s)
				db.session.commit()
				return s.dict()
			else:
				abort (400, message = 'wrong password')
		else:
			abort (400, message = 'user doesn\'t exists')
			
	def post(self):
		args = parser.parse_args()
		username = args['name']
		pwd = args['pwd']
		if (len(User.query.filter(User.username == args['name']).all()) == 0):
			user = User(username = username)
			user.hash_password(pwd)
			db.session.add(user)
			db.session.commit()
			return user.dict(), 201
		else:
			abort (400, message = 'user ' + username + ' already registered')

api.add_resource(ClientsList, '/clients')
api.add_resource(Client, '/clients/<int:client_id>')
api.add_resource(Login, '/login')

if __name__ == '__main__':
	app.run(debug=True)
