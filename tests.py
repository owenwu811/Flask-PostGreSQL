from flask import json
from app import app, db, User
import unittest 

#unittest.TestCase is a class
class TestUsers(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = '...'
        self.app = app.test_client()
        self.context = app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        for user in User.query.all():
            db.session.delete(user)
        db.session.commit()
        db.drop_all()
        self.context.pop()
    #creates record in the database
    def test_create_user(self):
        # Send a POST request to create a user
        response = self.app.post('/users', data=json.dumps({'name': 'John', 'email': 'john@example.com'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.query.count(), 1) #problem
    #first creates a user before executing a put request
    def test_update_user(self):
        # Create a user
        user = User(name='John', email='john@example.com')
        db.session.add(user)
        db.session.commit()

        # Send a PUT request to update the user
        response = self.app.put(f'/users/{user.id}', data=json.dumps({'name': 'Jane'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Check that the user was updated
        updated_user = User.query.get(user.id)
        self.assertEqual(updated_user.name, 'Jane')

    def test_delete_user(self):
        # Create a user
        user = User(name='John', email='john@example.com')
        db.session.add(user)
        db.session.commit()

        # Send a GET request to get the user's ID
        response = self.app.get(f'/users/{user.id}')
        self.assertEqual(response.status_code, 200) #problem

        # Send a DELETE request to delete the user
        response = self.app.delete(f'/users/{user.id}')
        self.assertEqual(response.status_code, 200)

        # Check that the user was deleted
        deleted_user = User.query.get(user.id)
        self.assertIsNone(deleted_user)

if __name__ == '__main__':
    unittest.main()
    
#To execute the unitest, run = python -m unittest discover -s tests - in the VSCode terminal
#documentation here: https://docs.python.org/3/library/unittest.html
