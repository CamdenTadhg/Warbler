"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None,
                                    header_image_url=None,
                                    bio=None, 
                                    location=None)
        self.testuser2 = User.signup(username="testuser2", 
                                     email="test2@test.com", 
                                     password="testuser", 
                                     image_url=None,
                                     header_image_url=None,
                                     bio=None,
                                     location=None)

        db.session.commit()

        msg1 = Message(text="testing 1", user_id = self.testuser.id)
        msg2 = Message(text="testing 2", user_id = self.testuser2.id)
        db.session.add_all([msg1, msg2])
        db.session.commit()
    
    def tearDown(self):
        """clean up any fouled transactions"""

        db.session.rollback()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of our test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'http://localhost/users/{self.testuser.id}')

            msg = db.session.query(Message).filter(Message.text == "Hello").first()
            self.assertEqual(msg.text, "Hello")
    
    def test_add_message_redirect(self):
        """Does site redirect appropriately after a message is added?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser', html)

    def test_add_message_loggedout(self):
        """Does site recognize when no one is logged in?"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')


    def test_add_message_loggedout_redirect(self):
        """Does site redirect appropriately when no one is logged in?"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up now", html)
            self.assertIn('Access unauthorized', html)


    def test_add_message_form_display(self):
        """Does site display add message form?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/messages/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add my message!', html)

    def test_view_message(self):
        """Does site display another user's message appropriately?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            msg = db.session.query(Message).filter(Message.text == "testing 2").first()
            resp = c.get(f'/messages/{msg.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testing 2', html)
            self.assertIn('fa-thumbs-up', html)
            self.assertNotIn('Delete', html)
             
    def test_view_message_loggedout(self):
        """Does site respond appropriately when a logged out user tries to view a message?"""
        with self.client as c:

            msg = db.session.query(Message).filter(Message.text == "testing 2").first()
            resp = c.get(f'/messages/{msg.id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')

    def test_view_message_loggedout_redirect(self):
        """Does site redirect appropriately when a logged out user tries to view a message?"""
        with self.client as c:

            msg = db.session.query(Message).filter(Message.text == "testing 2").first()
            resp = c.get(f'/messages/{msg.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up now", html)
            self.assertIn('Access unauthorized', html)

    def test_view_own_message(self):
        """Does site display a user's own messages correctly without a like button?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            msg = db.session.query(Message).filter(Message.text == "testing 1").first()
            resp = c.get(f'/messages/{msg.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testing 1', html)
            self.assertNotIn('fa-thumbs-up', html)
            self.assertIn('Delete', html)

    def test_delete_message(self):
        """Does the site delete messages correctly?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = db.session.query(Message).filter(Message.text == "testing 1").first()
            resp = c.post(f'/messages/{msg.id}/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'http://localhost/users/{self.testuser.id}')


    def test_delete_message_redirect(self):
        """Does the site redirect correctly when a message is deleted?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = db.session.query(Message).filter(Message.text == "testing 1").first()
            resp = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser', html)
            self.assertNotIn('testing 1', html)

    def test_delete_message_wrong_user(self):
        """Does the site respond correctly when a user tries to delete another user's message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = db.session.query(Message).filter(Message.text == "testing 2").first()
            resp = c.post(f'/messages/{msg.id}/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'http://localhost/users/{self.testuser.id}')
    
    def test_delete_message_wrong_user_redirect(self):
        """Does the site redirect correctly when a user tries to delete another user's message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = db.session.query(Message).filter(Message.text == "testing 2").first()
            resp = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser', html)

    def test_delete_message_loggedout(self):
        """Does site respond appropriately when a logged out user tries to delete a message?"""
        with self.client as c:

            msg = db.session.query(Message).filter(Message.text == "testing 2").first()
            resp = c.post(f'/messages/{msg.id}/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')

    def test_delete_message_loggedout_redirect(self):
        """Does site redirect appropriately when a logged out user tries to delete a message?"""
        with self.client as c:

            msg = db.session.query(Message).filter(Message.text == "testing 2").first()
            resp = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up now", html)
            self.assertIn('Access unauthorized', html)