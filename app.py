from flask import Flask, request, render_template
#from flask-restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_swagger import swagger
from flasgger import Swagger
import requests

app = Flask(__name__)

# Initialize Flask-SQLAlchemy - set the database connection string and initialize a db object instance
app.config['SQLALCHEMY_DATABASE_URI'] = '...'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db, migrate, ma = SQLAlchemy(app), Migrate(app, db), Marshmallow(app)

# Define your models here
class User(db.Model):
    #database has a table called users with columns id, name, and email
    __tablename__ = 'users'
    id, name, email = db.Column(db.Integer, primary_key=True), db.Column(db.String(50)), db.Column(db.String(120))
    def __repr__(self): #string representation of instance 
        return '<User %r>' % self.name

# how to convert object into json and vice versa. dump method lets you convert your object into json and vice versa using the load method. 
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

#Setting up flask restful api with two classes 
# handler to post data aka add users to the database 
class Users(Resource): # Users handles post 
    def post(self):
        # Get data from request
        data = request.get_json()
        # Validate input data 
        if 'name' not in data or 'email' not in data:
            return {'message': 'Invalid input data'}, 400
        # Add user to the database if atleast one of the fields is in the request payload
        user = User(name=data['name'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

api.add_resource(Users, '/users')

# handler for put request
class UserResource(Resource): # handles put + delete to update / delete a user frm the database based on the provided user id 
    def put(self, user_id):
        # Get the user from the database
        user = User.query.get(user_id)
        # error handling
        if not user: #user not found in database
            return {'message': f'User with ID {user_id} not found'}, 404

        # Get data from request
        data = request.get_json()
        # Update user data
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        db.session.commit()

        # Return updated user data
        user_schema = UserSchema()
        user_json = user_schema.dump(user)
        return {'message': 'User updated successfully', 'user': user_json}, 200

    def delete(self, user_id):
        # Get the user from the database
        user = User.query.get(user_id)
        if not user:
            return {'message': f'User with ID {user_id} not found'}, 404

        # Delete the user from the database
        db.session.delete(user)
        db.session.commit()

        return {'message': f'User with ID {user_id} deleted successfully'}, 200


api.add_resource(UserResource, '/users/<int:user_id>')
class Onboard(Resource): #onboarding process to handle creating a new user in Terraform Enterprise and storing that user in the database
    def post(self):
        # Get data from request
        data = request.get_json()
        # Validate input data
        if 'name' not in data or 'email' not in data or 'team' not in data:
            return {'message': 'Invalid input data'}, 400
        # Create user in Terraform Enterprise
        url = '...'
        headers = {'Authorization': '...'}
        payload = {
            'data': {
                'type': 'users',
                'attributes': {
                    'name': data['name'],
                    'email': data['email'],
                    'team': data['team']
                }
            }
        }
        print('Payload:', payload)
        response = requests.post(url, headers=headers, json=payload)
        print('Response:', response.json())
        # Check if user creation was successful
        if response.status_code != 201:
            return {'message': 'Failed to create user in Terraform Enterprise'}, 500
        # Add user to the database
        user = User(name=data['name'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

api.add_resource(Onboard, '/onboard') 

@app.route('/users') #route to fetch all users from database and render data using users.html template 
def get_users():
    users, user_schema, users_json = User.query.all(), UserSchema(many=True), user_schema.dump(users)
    return render_template('users.html', users=users_json, column_name='nickname') 
    
@app.route('/swagger')
def api_spec():
    """Returns the Swagger API specification."""
    with open("specification.yaml", 'r') as f:
        spec = f.read()
    return Response(spec, mimetype="text/plain")


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/specification.yaml",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
    "yaml": "specification.yaml"
}

swagger = Swagger(app, config=swagger_config)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #running flask app on 5000 with debug mode enabled 
    # Next, we need to perform database migrations. Database migrations can be thought of like version control systems when you want to rollback a change to the database schema. For example, if you update the class in line 20 to add a new model, you want the PostGreSql database to reflect these changes, so you would perform a database migration.
    #Instructions to perform DataBase Migrations:
    # 1. pip install flask-migrate or pip3 install flask-migrate
    # 2. set FLASK_APP=app.py or export FLASK_APP=app.py
    # 3. add to the top: from flask_migrate import Migrate

    # ...

    # migrate = Migrate(app, db)
    # 4. flask db init
    # 5. flask db migrate -m "initial migration"
    # 6. flask db upgrade
    # Step six applies any pending migrations to your database - postgresql in this case, so the migration will be executed within a DDL transaction
  
