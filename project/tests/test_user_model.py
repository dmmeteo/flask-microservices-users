from sqlalchemy.exc import IntegrityError

from project import db
from project.tests.base import BaseTestCase
from project.api.models import User
from project.tests.utils import add_user


class TestUserModel(BaseTestCase):
    """Ensure that user is add to database"""
    def test_add_user(self):
        user = User(
            username='justatest',
            email='test@test.com'
        )
        db.session.add(user)
        db.session.commit()
        self.assertTrue(user.id)
        self.assertTrue(user.active)
        self.assertTrue(user.created_at)
        self.assertEqual(user.username, 'justatest')
        self.assertEqual(user.email, 'test@test.com')

    """Ensure that when you add new user it must be unique username"""
    def test_add_user_duplicate_username(self):
        user = User(
            username='justatest',
            email='test@test.com'
        )
        db.session.add(user)
        db.session.commit()
        duplicate_user = User(
            username='justatest',
            email='test@test2.com'
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    """Ensure that when you add new user it must be unique email"""
    def test_add_user_duplicate_email(self):
        user = User(
            username='justatest',
            email='test@test.com'
        )
        db.session.add(user)
        db.session.commit()
        duplicate_user = User(
            username='justatest2',
            email='test@test.com'
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    """Ensure that passwoerds are random"""
    def test_passwords_are_random(self):
        user_one = add_user('justatest', 'test@test.com', 'test')
        user_two = add_user('justatest2', 'test2@test.com', 'test')
        self.assertNotEqual(user_one.passwoerd, user_two.passwoerd)







