from flask import Flask, jsonify
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.mongoalchemy import MongoAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
import os, string, random, time
from functools import wraps
from passlib.apps import custom_app_context as pwd_context
from config import *
from models import db, User, ClientModel, Token

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db.init_app(app)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('pwd', type=str)
parser.add_argument('surname', type=str)
parser.add_argument('state', type=str)
parser.add_argument('change-balance', type=int)
parser.add_argument('token', type=str)
parser.add_argument('balance', type=int)
parser.add_argument('page', type=int)
parser.add_argument('per-page', type=int)

def get_client(client_id):
    if ClientModel.query.get(client_id) is None:
        abort(404, message="Client {} doesn't exist".format(client_id))
    return ClientModel.query.get(client_id)

def login_required(token):
	token = Token.query.filter(Token.token == token).first()
	if (token):
		if (time.time() - token.start) < TOKEN_TTL:
			return True
		abort (400, message = 'Token expired')
	abort (403)

class Client(Resource):
	def get(self, client_id):
		return get_client(client_id).dict()

	def delete(self, client_id):
		args = parser.parse_args()
		if (login_required(args['token'])):
			try:
				db.session.delete(get_client(client_id))
				db.session.commit()
			except:
				abort (500)
			return '', 204
		return 403

	def put(self, client_id):
		args = parser.parse_args()
		if (login_required(args['token'])):
			abort_if_client_doesnt_exist(client_id)
			client = ClientModel.query.get(client_id)
			client.state = args['state']
			return client.dict()
		return 403

class ClientsList(Resource):
	def get(self):
		args = parser.parse_args()
		if (login_required(args['token'])):
			clientList = []
			page = args['page']
			per_page = args['per-page']
			if not page:
				page = DEFAULT_START_PAGE
			if not per_page:
				per_page = DEFAULT_PER_PAGE
			for client in ClientModel.query.paginate(page, per_page, True).items:
				clientList.append(client.dict())
			return {"clients": clientList}
		else:
			abort (403)
        
	def post(self):
		args = parser.parse_args()
		if (login_required(args['token'])):
			client = ClientModel(name=args["name"], state=args["state"], surname=args["surname"], balance=args['balance'])
			client.add()
			return client.dict(), 201
		abort(403)
		
class Login(Resource):
	def get(self):
		args = parser.parse_args()
		name = args['name']
		pwd = args['pwd']
		user = User.query.filter(User.username == name).first()
		if (user):
			if (pwd):
				if (user.verify_password(pwd)):
					start = int(round(time.time()))
					token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
					s = Token(start = start, token = token)
					token.add()
					return s.dict()
				else:
					abort (400, message = 'wrong password')
			else:
				abort (400, message = 'pwd can\'t be empty')
		else:
			abort (400, message = 'user doesn\'t exists')
			
	def post(self):
		args = parser.parse_args()
		username = args['name']
		pwd = args['pwd']
		if (len(User.query.filter(User.username == args['name']).all()) == 0):
			user = User(username = username)
			user.hash_password(pwd)
			user.add()
			return user.dict(), 201
		else:
			abort (400, message = 'user ' + username + ' already registered')

api.add_resource(ClientsList, '/clients')
api.add_resource(Client, '/clients/<int:client_id>')
api.add_resource(Login, '/login')
