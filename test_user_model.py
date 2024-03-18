"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email = 'camdent@test.com',
            username = 'camdentadhg', 
            password = 'HASHED_PASSWORD'
        )
        u2 = User(
            email = 'dianabright@test.com', 
            username = 'dianabright',
            password = 'HASHED_PASSWORD'
        )
        u3 = User(
            email = 'amandamacomber@test.com',
            username = 'amandamacomber', 
            password = 'HASHED_PASSWORD'
        )
        db.session.add_all([u1, u2, u3])
        db.session.commit()

        u1.followers.append(u2)
        u2.followers.append(u1)
        db.session.add_all([u1, u2])
        db.session.commit()

        self.client = app.test_client()
    
    def tearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.likes), 0)

    def test_repr(self):
        """Does repr return the correct format?"""

        u = User(
            email = "test@test.com",
            username = "testuser",
            password = "HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(f'<User {u.id}: testuser, test@test.com>', str(u))

    def test_is_followed_by_true(self):
        """Does is_followed_by correctly identify when the relationship exists?"""

        camden = db.session.query(User).filter(User.username == 'camdentadhg').first()
        diana = db.session.query(User).filter(User.username == 'dianabright').first()

        self.assertTrue(camden.is_followed_by(diana))

    def test_is_followed_by_false(self):
        """Does is_followed_by correctly identify when a relationship does not exist?"""
        
        camden = db.session.query(User).filter(User.username == 'camdentadhg').first()
        amanda = db.session.query(User).filter(User.username == 'amandamacomber').first()

        self.assertFalse(camden.is_followed_by(amanda))

    def test_is_following_true(self):
        """Does is_following correctly identify when a relationship exists?"""

        camden = db.session.query(User).filter(User.username == 'camdentadhg').first()
        diana = db.session.query(User).filter(User.username == 'dianabright').first()

        self.assertTrue(camden.is_following(diana))

    def test_is_following_false(self):
        """Does is_following correctly identify when a relationship does not exist?"""

        camden = db.session.query(User).filter(User.username == 'camdentadhg').first()
        amanda = db.session.query(User).filter(User.username == 'amandamacomber').first()

        self.assertFalse(camden.is_following(amanda))

    def test_signup_correct(self):
        """Does signup correctly create a user when the appropriate data is given?"""

        u = User.signup(username='testing', email='test@test.com', password='testing', image_url=None, header_image_url=None, bio=None, location=None)
        db.session.commit()

        self.assertIsInstance(u, User)
        self.assertNotEqual(7, len(u.password))
        self.assertEqual(u.username, 'testing')
        self.assertEqual(u.image_url, "/static/images/default-pic.png")
        self.assertEqual(u.header_image_url,"/static/images/warbler-hero.jpg")

    def test_signup_duplicate_username(self):
        """Does signup fail to return a user when a duplicate username is entered?"""
        
        with self.assertRaises(Exception) as context:
            u = User.signup(username='camdentadhg', email='camdentadhg@test.com', password='testing', image_url=None, header_image_url=None, bio=None, location=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception))

    def test_signup_duplicate_email(self):
        """Does signup fail to return a user when a duplicate email is entered?"""

        with self.assertRaises(Exception) as context:
            u = User.signup(username='camdentadhg2', email='camdent@test.com', password='testing',image_url=None, header_image_url=None, bio=None, location=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception)) 

    def test_signup_blank_username(self):
        """Does signup fail to return a user when no username is entered?"""

        with self.assertRaises(Exception) as context:
            u = User.signup(username=None, email='camdent@test.com', password='testing',image_url=None, header_image_url=None, bio=None, location=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception)) 

    def test_signup_blank_password(self):
        """Does signup fail to return a user when no password is entered?"""

        with self.assertRaises(Exception) as context:
            u = User.signup(username='camdentadhg2', email='camdent@test.com', password=None,image_url=None, header_image_url=None, bio=None, location=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception)) 

    def test_signup_blank_email(self):
        """Does signup fail to return a user when no email is entered?"""

        with self.assertRaises(Exception) as context:
            u = User.signup(username='camdentadhg2', email=None, password='testing',image_url=None, header_image_url=None, bio=None, location=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception)) 

    def test_authenticate_true(self):
        """Does authenticate return a user when a correct username and password are entered?"""

        u = User.signup(username='camdentadhg2', email='camdent@gmail.com', password='testing',image_url=None, header_image_url=None, bio=None, location=None)
        db.session.commit()

        test_user = User.authenticate(username='camdentadhg2', password='testing')

        self.assertIsInstance(test_user, User)
        self.assertEqual(test_user.username, 'camdentadhg2')


    def test_authenticate_false(self):
        """Does authenticate not return a user and return False when an incorrect username and password are entered?"""

        u = User.signup(username='camdentadhg2', email='camdent@gmail.com', password='testing',image_url=None, header_image_url=None, bio=None, location=None)
        db.session.commit()

        test_user = User.authenticate(username='camdentadhg2', password='password')

        self.assertNotIsInstance(test_user, User)
        self.assertFalse(test_user)