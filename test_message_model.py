"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from datetime import date

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

class MessageModelTestCase(TestCase):
    """Tests for the message model"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        test_user = User(email='janedoe@gmail.com', username='janedoe', password='password')
        db.session.add(test_user)
        db.session.commit()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""
        test_user = db.session.query(User).filter(User.username=='janedoe').first()

        m = Message(
            text="this is a test message",
            user_id = test_user.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.user.username, 'janedoe')
        self.assertEqual(m.text, 'this is a test message')
        self.assertIn(str(date.today()), str(m.timestamp))
