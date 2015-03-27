import os
from flask import Flask, jsonify
from flask.ext.restful import reqparse, abort, Api, Resource
from conf import *
from models import *

app = Flask(__name__)
db.init_app(app)
api = Api(app)

parser = reqparse.RequestParser()
parser_args = {
	'name': str,
	'pwd': str,
	'surname': str,
	'state': str,
	'change-balance': int,
	'token': str,
	'balance': int,
	'page': int,
	'per-page': int
}
for (key, value) in parser_args.items():
	parser.add_argument(key, type=value)

def get_client(client_id):
	client = ClientModel.get_client_by_id(client_id)
	if client is None:
		abort(404, message="Client with id {} doesn't exist".format(client_id))
	return client

def authorize(token):
	t = Token.check_token(token)
	if t[0]: return True
	else: abort (403, message = t[1])

class Client(Resource):
	def get(self, client_id):
		return get_client(client_id).dict()

	def delete(self, client_id):
		args = parser.parse_args()
		if (authorize(args['token'])):
			try:
				client = ClientModel.get_client_by_id(client_id)
				client.delete()
			except:
				abort (500)
			return '', 204
		return 403

	def put(self, client_id):
		args = parser.parse_args()
		if (authorize(args['token'])):
			abort_if_client_doesnt_exist(client_id)
			client = ClientModel.query.get(client_id)
			client.state = args['state']
			return client.dict()
		return 403

class ClientsList(Resource):
	def get(self):
		args = parser.parse_args()
		if (authorize(args['token'])):
			clientList = []
			page = args['page']
			per_page = args['per-page']
			for client in ClientModel.paginate_clients(page, per_page):
				clientList.append(client.dict())
			return {"clients": clientList}
		else:
			abort (403)
        
	def post(self):
		args = parser.parse_args()
		if (authorize(args['token'])):
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

#ROUTES#
api.add_resource(ClientsList, '/clients')
api.add_resource(Client, '/clients/<int:client_id>')
api.add_resource(Login, '/login')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = COMMIT_ON_TEARDOWN
