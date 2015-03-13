from flask import Flask, jsonify
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.mongoalchemy import MongoAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('surname', type=str)
parser.add_argument('state', type=str)
parser.add_argument('change-balance', type=int)

def get_client(client_id):
	if ClientModel.query.get(client_id) is None:
		abort(404, message="Client {} doesn't exist".format(client_id))
	return ClientModel.query.get(client_id)

class ClientModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    state = db.Column(db.String(10))
    balance = db.Column(db.Integer)
    
    def __init__(self, name, surname, state):
        self.name = name
        self.surname = name
        self.state = state
        #self.balance = balance

    def __repr__(self):
        return ('name: ' + self.name + ', state: ' + self.state)
        
    def dict(self):
		return {'id': self.id, 'name':self.name,'surname':self.surname, 'balance':self.balance, 'state':self.state}

class Client(Resource):
	def get(self, client_id):
		return get_client(client_id).dict()

	def delete(self, client_id):
		db.session.delete(get_client(client_id))
		db.session.commit()
		return '', 204

	def put(self, client_id):
		abort_if_client_doesnt_exist(client_id)
		args = parser.parse_args()
		client = ClientModel.query.get(client_id)
		client.state = args['state']
		return client.dict()

class ClientsList(Resource):
	def get(self):
		clientList = []
		page = 1
		ipp = 10
		paginate = ClientModel.query.paginate(page, ipp)
		for client in ClientModel.query.all():
			clientList.append(client.dict())
		return {"clients": clientList}
        
	def post(self):
		args = parser.parse_args()
		client = ClientModel(name=args["name"], state=args["state"], surname=args["surname"])
		db.session.add(client)
		db.session.commit()
		return client.dict(), 201

api.add_resource(ClientsList, '/clients')
api.add_resource(Client, '/clients/<int:client_id>')


if __name__ == '__main__':
	app.run(debug=True)
