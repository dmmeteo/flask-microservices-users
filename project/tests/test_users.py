import json
import datetime

from project import db
from project.tests.base import BaseTestCase
from project.api.models import User
from project.tests.utils import add_user


class TestUserServise(BaseTestCase):
    """Test for the Users Servise"""

    def test_users(self):
        """Ensure the /ping route bekaves correctly"""
        response = self.client.get("/ping")
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn("pong!", data["message"])
        self.assertIn("success", data["status"])

    def test_add_user(self):
        """Ensure a new user can be added to the database"""
        add_user("test", "test@test.com", "test")
        # update user
        user = User.query.filter_by(email="test@test.com").first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            response = self.client.post(
                "/users",
                data=json.dumps(
                    {
                        "username": "boba",
                        "email": "boba@realpython.com",
                        "password": "test",
                    }
                ),
                content_type="application/json",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn("boba@realpython.com was added!", data["message"])
            self.assertIn("success", data["status"])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        add_user("test", "test@test.com", "test")
        # update user
        user = User.query.filter_by(email="test@test.com").first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            response = self.client.post(
                "/users",
                data=json.dumps({}),
                content_type="application/json",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object does not have a username key"""
        add_user("test", "test@test.com", "test")
        # update user
        user = User.query.filter_by(email="test@test.com").first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            response = self.client.post(
                "/users",
                data=json.dumps({"email": "boba@realpython.com"}),
                content_type="application/json",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_duplicate_email(self):
        """Ensure error is thrown if the email already exists"""
        add_user("test", "test@test.com", "test")
        # update user
        user = User.query.filter_by(email="test@test.com").first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            self.client.post(
                "/users",
                data=json.dumps(
                    {
                        "username": "boba",
                        "email": "boba@realpython.com",
                        "password": "test",
                    }
                ),
                content_type="application/json",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            response = self.client.post(
                "/users",
                data=json.dumps({"username": "boba", "email": "boba@realpython.com"}),
                content_type="application/json",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Sorry. That email already exists.", data["message"])
            self.assertIn("fail", data["status"])

    def test_single_user(self):
        """Ensure get single user behaves correctly"""
        user = add_user("boba", "boba@realpython.com", "password")
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get(f"/users/{user.id}")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue("created_at" in data["data"])
            self.assertIn("boba", data["data"]["username"])
            self.assertIn("boba@realpython.com", data["data"]["email"])
            self.assertIn("success", data["status"])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided"""
        with self.client:
            response = self.client.get("/users/hui")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn("User does not exist", data["message"])
            self.assertIn("fail", data["status"])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist"""
        with self.client:
            response = self.client.get("/users/999")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn("User does not exist", data["message"])
            self.assertIn("fail", data["status"])

    def test_all_users(self):
        """Ensure get all users behaves correctly"""
        created = datetime.datetime.utcnow() + datetime.timedelta(-30)
        add_user("boba", "boba@realpython.com", "password", created)
        add_user("biba", "biba@realpython.com", "password")
        with self.client:
            response = self.client.get("/users")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data["data"]["users"]), 2)
            self.assertTrue("created_at" in data["data"]["users"][0])
            self.assertTrue("created_at" in data["data"]["users"][1])
            self.assertIn("boba", data["data"]["users"][1]["username"])
            self.assertIn("biba", data["data"]["users"][0]["username"])
            self.assertIn("boba@realpython.com", data["data"]["users"][1]["email"])
            self.assertIn("biba@realpython.com", data["data"]["users"][0]["email"])
            self.assertIn("success", data["status"])

    def test_add_user_invalid_json_keys_no_password(self):
        """Ensure error is thrown if the JSON object does not have a password key"""
        add_user("test", "test@test.com", "test")
        # update user
        user = User.query.filter_by(email="test@test.com").first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            response = self.client.post(
                "/users",
                data=json.dumps({"username": "boba", "email": "boba@realpython.com"}),
                content_type="application/json",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_inactive(self):
        add_user("test", "test@test.com", "test")
        # update user
        user = User.query.filter_by(email="test@test.com").first()
        user.active = False
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            response = self.client.post(
                "/users",
                data={
                    "username": "boba",
                    "email": "boba@realpython.com",
                    "password": "test",
                },
                content_type="application/json",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "error")
            self.assertTrue(
                data["message"] == "Something went wrong. Please contact us."
            )
            self.assertEqual(response.status_code, 401)

    def test_add_user_not_admin(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            # user login
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            response = self.client.post(
                "/users",
                data=json.dumps(
                    {
                        "username": "boba",
                        "email": "boba@realpython.com",
                        "password": "test",
                    }
                ),
                content_type="application/json",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "error")
            self.assertTrue(data["message"] == "You do not have permission to do that.")
            self.assertEqual(response.status_code, 401)
