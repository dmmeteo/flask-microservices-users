import json

from project.tests.base import BaseTestCase


class TestUserServise(BaseTestCase):
    """Test for the Users Servise"""

    def test_users(self):
        """Ensure the /ping route bekaves correctly"""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to the database"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'boba',
                    'email': 'boba@realpython.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('boba@realpython.com was added!', data['message'])
            self.assertIn('success', data['status'])

