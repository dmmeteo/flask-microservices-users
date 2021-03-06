import time
import json

from project import db
from project.tests.base import BaseTestCase
from project.api.models import User
from project.tests.utils import add_user


class TestAuthBlueprint(BaseTestCase):

    def test_user_registration(self):
        """Ensure user can registration"""
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps(
                    {
                        "username": "justatest",
                        "email": "test@test.com",
                        "password": "test",
                    }
                ),
                content_type="application/json",
            )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertTrue(data["message"] == "Successfully registered.")
        self.assertTrue(data["auth_token"])
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 201)

    def test_user_registration_duplicate_email(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps(
                    {"username": "boba", "email": "test@test.com", "password": "test"}
                ),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Sorry. That user already exists.", data["message"])
            self.assertIn("error", data["status"])

    def test_user_registration_duplicate_username(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps(
                    {"username": "test", "email": "test@test2.com", "password": "test"}
                ),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Sorry. That user already exists.", data["message"])
            self.assertIn("error", data["status"])

    def test_user_registration_invalid_json(self):
        with self.client:
            response = self.client.post(
                "/auth/register", data=json.dumps({}), content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("error", data["status"])

    def test_user_registration_invalid_json_keys_no_username(self):
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("error", data["status"])

    def test_user_registration_invalid_json_keys_no_email(self):
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({"username": "justatest", "password": "test"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("error", data["status"])

    def test_user_registration_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({"username": "justatest", "email": "test@test.com"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("error", data["status"])

    def test_registered_user_login(self):
        with self.client:
            user = add_user("justatest", "test@test.com", "test")
            response = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully logged in.")
            self.assertTrue(data["auth_token"])
            self.assertTrue(response.content_type == "application/json")

    def test_not_registered_user_login(self):
        with self.client:
            response = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertTrue(data["status"] == "error")
            self.assertTrue(data["message"] == "User does not exist.")
            self.assertTrue(response.content_type == "application/json")

    def test_valid_logout(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            # user login
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            # valid token logout
            response = self.client.get(
                "/auth/logout",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully logged out.")
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout_expired_token(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            # invalid token logout
            time.sleep(4)
            response = self.client.get(
                "/auth/logout",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "error")
            self.assertTrue(
                data["message"] == "Signature expired. Please log in again."
            )
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout(self):
        with self.client:
            response = self.client.get(
                "/auth/logout", headers={"Authorization": "Bearer invalid"}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "error")
            self.assertTrue(data["message"] == "Invalid token. Please log in again.")
            self.assertEqual(response.status_code, 401)

    def test_user_status(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            response = self.client.get(
                "/auth/status",
                headers={
                    "Authorization": "Bearer "
                    + json.loads(resp_login.data.decode())["auth_token"]
                },
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["data"] is not None)
            self.assertTrue(data["data"]["username"] == "test")
            self.assertTrue(data["data"]["email"] == "test@test.com")
            self.assertTrue(data["data"]["active"] is True)
            self.assertTrue(data["data"]["created_at"])

    def test_invalid_status(self):
        response = self.client.get(
            "/auth/status", headers={"Authorization": "Bearer invalid"}
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertTrue(data["status"])
        self.assertTrue(data["message"] == "Invalid token. Please log in again.")

    def test_invalid_logout_inactive(self):
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
            response = self.client.get(
                "/auth/logout",
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
