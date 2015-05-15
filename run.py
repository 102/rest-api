from app import app
from app import db
db.init_app(app)

if __name__ == '__main__':
	with app.app_context():
		#db.drop_all()
		db.create_all()
	app.run(debug=True)
