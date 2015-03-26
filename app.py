import os
from flask import Flask, jsonify
from flask.ext.restful import reqparse, abort, Api, Resource
from config import *
from models import *

app = Flask(__name__)


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
    if ClientModel.get_client_by_id(client_id) is None:
        abort(404, message="Client w/ id {} doesn't exist".format(client_id))
    return ClientModel.query.get(client_id)

def login_required(token):
	t = Token.check_token(token)
	if t[0]: return True
	else: abort (403, message = t[1])

class Client(Resource):
	def get(self, client_id):
		return get_client(client_id).dict()

	def delete(self, client_id):
		args = parser.parse_args()
		if (login_required(args['token'])):
			try:
				client = ClientModel.get_client_by_id(client_id)
				client.delete()
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
		abort (403)

class Login(Resource):
	def get(self):
		args = parser.parse_args()
		name = args['name']
		pwd = args['pwd']
		user = User.get_user_by_name(name)
		if (user):
			if (pwd):
				if (user.verify_password(pwd)):
					t = Token()
					return t.dict()
				else: abort (400, message = 'wrong password')
			else: abort (400, message = 'password can\'t be empty')
		else: abort (400, message = 'user doesn\'t exists')
			
	def post(self):
		args = parser.parse_args()
		username = args['name']
		pwd = args['pwd']
		if not User.is_user_exists(username):
			user = User(username = username)
			user.hash_password(pwd)
			user.add()
			return user.dict(), 201
		else:
			abort (400, message = 'user ' + username + ' already registered')

##########
##ROUTES##
##########
api.add_resource(ClientsList, '/clients')
api.add_resource(Client, '/clients/<int:client_id>')
api.add_resource(Login, '/login')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = COMMIT_ON_TEARDOWN
