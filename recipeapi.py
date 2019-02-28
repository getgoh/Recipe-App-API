from flask import Flask, request, json
from flask_restful import reqparse, Resource, Api
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

from flask_json import FlaskJSON, JsonError, json_response, as_json


mysql = MySQL()
app = Flask(__name__)
api = Api(app)
# json = FlaskJSON(app)
FlaskJSON(app)


# parser = reqparse.RequestParser()
# parser.add_argument('user')

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'recipedb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


# Recipe class. Aim is to implement CRUD
class Recipe(Resource):
	# post: (C)reate
	def post(self):
		# read data from post
		data = request.get_json(force=True)

		# print data to console (debugging)
		print("data: " + str(data));

		# for d in data:
		# 	print(d)

		_name = data['Name']
		_desc = data['Description']
		_preptime = data['PrepTime']
		_cooktime = data['CookingTime']
		_directions = data['Directions']

		# connect to database
		conn = mysql.connect()
		# acquire cursor
		cursor = conn.cursor()

		print("Name: " + _name)
		print("desc: " + _desc)
		# integers need to be parsed to string before printing
		print("preptime: " + str(_preptime)) 
		print("cooktime: " + str(_cooktime))

		# Stored procedure: store the recipe
		cursor.callproc('sp_createRecipe', (_name, _desc, _preptime, _cooktime))
		# get returned id of newly inserted row
		data = cursor.fetchall()

		if len(data) > 0:
			conn.commit()
			currRecipeID = data[0]
			# store each direction
			for d in range(len(_directions)):
				print("Dir #" + str(d) + ": " + _directions[d])
				cursor.callproc('sp_createDirection', (currRecipeID, str(_directions[d])))

		# commit transactions to database
		conn.commit()


		# TODO: return http response code(s)
		return json.dumps({'result':'done'})		


# TODO: Class for User
class Users(Resource):
	# post: (C)reate
	def post(self):
		data = request.get_json(force=True)

		_name = data['name']		

		
		conn = mysql.connect()
		cursor = conn.cursor()

		cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
		data = cursor.fetchall()

		if len(data) is 0:
			conn.commit()
			return json.dumps({'message':'User created successfully !'})
		else:
			return json.dumps({'error':str(data[0])})

		return 'test'
	# put: (U)pdate
	def put(self):
		data = request.get_json(force=True)

		_name = data['name']
		_email = data['email']
		_password = data['password']

		conn = mysql.connect()
		cursor = conn.cursor()

		# ALWAYS hash passwords
		_hashed_password = generate_password_hash(_password)
		cursor.callproc('sp_updateUser',(_name,_email,_hashed_password))
		data = cursor.fetchall()

		if len(data) is 0:
			conn.commit()
			return json.dumps({'message':'User updated successfully !'})
		else:
			return json.dumps({'error':str(data[0])})

# Test class
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


# Exposed endpoints (http://localhost:5000)
#api.add_resource(HelloWorld, '/')
api.add_resource(Recipe, '/')


if __name__ == '__main__':
	#setting the host like this allows it to be publicly accessed
    app.run(host="0.0.0.0",debug=True) 