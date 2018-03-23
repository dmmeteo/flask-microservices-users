from sqlalchemy.exc import IntegrityError

from project import db
from project.tests.base import BaseTestCase
from project.api.models import User
from project.tests.utils import add_user


class TestUserModel(BaseTestCase):

    def test_add_user(self):
        """Ensure that user is add to database"""
        user = add_user('justatest', 'test@test.com', 'test')
        self.assertTrue(user.id)
        self.assertEqual(user.username, 'justatest')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.password)
        self.assertTrue(user.active)
        self.assertTrue(user.created_at)
        self.assertTrue(user.admin == False)

    def test_add_user_duplicate_username(self):
        """Ensure that when you add new user it must be unique username"""
        add_user('justatest', 'test@test.com', 'test')
        duplicate_user = User(
            username='justatest',
            email='test@test2.com',
            password='test'
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_email(self):
        """Ensure that when you add new user it must be unique email"""
        add_user('justatest', 'test@test.com', 'test')
        duplicate_user = User(
            username='justatest2',
            email='test@test.com',
            password='test'
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_passwords_are_random(self):
        """Ensure that passwords are random"""
        user_one = add_user('justatest', 'test@test.com', 'test')
        user_two = add_user('justatest2', 'test2@test.com', 'test')
        self.assertNotEqual(user_one.password, user_two.password)

    def test_encode_auth_token(self):
        """Ensure that auth token is set and is bytes"""
        user = add_user('justatest', 'test@test.com', 'test')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertEqual(User.decode_auth_token(auth_token), user.id)




