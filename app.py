from flask import Flask, request, render_template
from flask_restful import Api, Resource
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'connection string here'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define your models here
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120))

    def __repr__(self):
        return '<User %r>' % self.name

api = Api(app)

class Onboard(Resource):
    def post(self):
        # Get data from request
        data = request.get_json()
        # Validate input data
        if 'name' not in data or 'email' not in data or 'team' not in data:
            return {'message': 'Invalid input data'}, 400
        # Create user in Terraform Enterprise
        url = 'yoururl'
        headers = {'Authorization': 'yourtoken'}
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
        return {'message': 'User created successfully'}, 201

api.add_resource(Onboard, '/onboard')

@app.route('/users')
def get_users():
    users = User.query.all()
    return render_template('users.html', users=users, column_name='nickname')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
