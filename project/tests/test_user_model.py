from project import db
from project.tests.base import BaseTestCase
from project.api.models import User

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

