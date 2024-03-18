"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase
from app import do_login, do_logout, add_user_to_g
from flask import g, session

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

class UserViewTestCase(TestCase):
    """Test views for users."""

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
        self.testuser2 = User.signup(username='testuser2', 
                                     email='test2@test.com', 
                                     password='testuser',
                                     image_url=None,
                                     header_image_url=None,
                                     bio=None,
                                     location=None)
        db.session.commit()
        
        self.msg1 = Message(text="testing 1", user_id = self.testuser.id)
        self.msg2 = Message(text="testing 2", user_id = self.testuser2.id)
        db.session.add_all([self.msg1, self.msg2])
        db.session.commit()

        self.testuser.following.append(self.testuser2)
        db.session.add(self.testuser)
        db.session.commit()

    
    def tearDown(self):
        """clean up any fouled transactions"""

        db.session.rollback()
    
    def test_homepage_loggedout(self):
        """Does anonymous homepage display correctly?"""
        with self.client as c:
            resp = c.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign up now', html)

    def test_homepage_loggedin(self):
        """Does logged in home page display correctly?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # testing presence of own message
            self.assertIn('testing 1', html)
            # testing presence of followed user's message
            self.assertIn('testing 2', html)

    # def test_do_login(self):
    #     """Does do_login function work?"""
    #     with app.test_request_context():
    #         with self.client as c:
    #             with c.session_transaction() as session:
    #                 do_login(self.testuser)

    #             self.assertEqual(session[CURR_USER_KEY], self.testuser.id)

    # def test_do_logout(self):
    #     """Does do_logout fuction work?"""
    #     with app.test_request_context():
    #         with self.client as c:
    #             with c.session_transaction() as session:
    #                 session[CURR_USER_KEY] = self.testuser.id
    #                 do_logout()

    #             self.assertFalse(session.get(CURR_USER_KEY))

    # def test_add_user_to_g(self):
    #     """Does add_user_to_g function work?"""
    #     with app.test_request_context():
    #         with self.client as c:
    #             with c.session_transaction() as session:
    #                 session[CURR_USER_KEY] = self.testuser.id
    #             add_user_to_g()

    #             self.assertEqual(g.user, self.testuser)

    def test_signup_get(self):
        """If there is no valid form submission, does the site display the signup form?"""
        with self.client as c:
            resp = c.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Join Warbler today.', html)


    # def test_signup_correct(self):
    #     """Can a user sign up for Warbler?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             resp = c.post('/signup', data={'username':'testuser3', 'password':'testuser', 'password2':'testuser', 'email': 'test3@test.com', 'image_url':None, 'header_image_url': None, 'bio': None, 'location': None})
    #             new_user = db.session.query(User).filter(User.username == 'testuser3').first()

    #             self.assertEqual(resp.status_code, 302)
    #             self.assertEqual(resp.location, 'http://localhost/')
    #             self.assertEqual(session[CURR_USER_KEY], new_user.id)
    #             self.assertIsInstance(new_user, User)
    #             self.assertEqual(new_user.email, 'test3@test.com')

    def test_signup_correct_redirect(self):
        """Does the site redirect correctly after a sign up?"""
        with self.client as c:
            resp = c.post('/signup', data={'username':'testuser3', 'password':'testuser', 'password2':'testuser', 'email': 'test3@test.com', 'image_url':None, 'header_image_url': None, 'bio': None, 'location': None}, follow_redirects=True)
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser3', html)

    # def test_signup_password_no_match(self):
    #     """Does the site detect non-matching passwords?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             resp = c.post('/signup', data={'username':'testuser3', 'password':'testuser', 'password2':'testuseruser', 'email': 'test3@test.com', 'image_url':None, 'header_image_url': None, 'bio': None, 'location': None})
    #             html=resp.get_data(as_text=True)

    #             self.assertEqual(resp.status_code, 200)
    #             self.assertIn('Passwords do not match.', html)
    #             self.assertFalse(session.get(CURR_USER_KEY))

    # def test_signup_username_taken(self):
    #     """Does the site detect when a username is already in use?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             resp = c.post('/signup', data={'username':'testuser', 'password':'testuser', 'password2':'testuser', 'email': 'test3@test.com', 'image_url':None, 'header_image_url': None, 'bio': None, 'location': None})
    #             html=resp.get_data(as_text=True)

    #             self.assertEqual(resp.status_code, 200)
    #             self.assertIn('Username already taken', html)
    #             self.assertFalse(session.get(CURR_USER_KEY))

    # def test_signup_email_taken(self):
    #     """Does the site detect when an email is already in use?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             resp = c.post('/signup', data={'username':'testuser3', 'password':'testuser', 'password2':'testuser', 'email': 'test2@test.com', 'image_url':None, 'header_image_url': None, 'bio': None, 'location': None})
    #             html=resp.get_data(as_text=True)

    #             self.assertEqual(resp.status_code, 200)
    #             self.assertIn('Email already taken', html)
    #             self.assertFalse(session.get(CURR_USER_KEY))
     
    # def test_signup_loggedin_get(self):
    #     """Does the site refuse to show the sign up form if a user is already logged in?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #             resp = c.get('/signup')

    #             self.assertEqual(resp.status_code, 302)
    #             self.assertEqual(resp.location, 'http://localhost/')

    # def test_signup_loggedin_redirect_get(self):
    #     """Does the site redirect correctly when a logged in user tries to access the signup form?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #             resp = c.get('/signup', follow_redirects=True)
    #             html = resp.get_data(as_text=True)

    #             self.assertEqual(resp.status_code, 200)
    #             self.assertIn('You are already logged in', html)

    def test_signup_loggedin(self):
        """Does the site refuse a signup post if a user is already logged in?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.post('/signup', data={'username':'testuser3', 'password':'testuser', 'password2':'testuser', 'email': 'test3@test.com', 'image_url':None, 'header_image_url': None, 'bio': None, 'location': None})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')

    def test_signup_loggedin_redirect(self):
        """Does the site redirect correctly if a logged in user tries to send a signup form?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.post('/signup', data={'username':'testuser3', 'password':'testuser', 'password2':'testuser', 'email': 'test3@test.com', 'image_url':None, 'header_image_url': None, 'bio': None, 'location': None}, follow_redirects=True)
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are already logged in', html)

    def test_login_get(self):
        """Does the site display the login form when no valid form data is submitted?"""
        with self.client as c:
            resp = c.get('/login')
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome back', html)

    # def test_login_correct(self):
    #     """Does the site correctly authenticate a valid user?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             resp = c.post('/login', data={'username': 'testuser', 'password': 'testuser'})

    #             self.assertEqual(resp.status_code, 302)
    #             self.assertEqual(resp.location, 'http://localhost/')
    #             self.assertEqual(session[CURR_USER_KEY], self.testuser.id)

    # def test_login_correct_redirect(self):
    #     """Does the site correctly redirect once a valid user is authenticated?"""
    #     with self.client as c:
    #         resp = c.post('/login', data={'username': 'testuser', 'password': 'testuser'}, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Hello, testuser', html)
    #         with c.session_transaction() as session:
    #             self.assertEqual(session[CURR_USER_KEY], self.testuser.id)
    #         self.assertEqual(g.user, self.testuser)

    def test_login_loggedin_get(self):
        """Does the site refuse to display the login form if a user is logged in?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.get('/login')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')

    def test_login_loggedin_redirect_get(self):
        """Does the site redirect correctly if a logged in user tries to access the login form?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.get('/login', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are already logged in', html)

    def test_login_loggedin(self):
        """Does the site refuse to process a login form if a user is already logged in?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.post('/login', data={'username': 'testuser2', 'password': 'testuser'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')
            self.assertEqual(session[CURR_USER_KEY], self.testuser.id)

    def test_login_loggedin_redirect(self):
        """Does the site redirect correctly if a logged in user tries to submit a login form?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.post('/login', data={'username': 'testuser2', 'password': 'testuser'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are already logged in', html)
            self.assertEqual(session[CURR_USER_KEY], self.testuser.id)

    def test_logout_loggedout(self):
        """Does the site reject a logout request if the user is already logged out?"""
        with self.client as c:
            resp = c.post('/logout')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/login')

    def test_logout_loggedout_redirect(self):
        """Does the site redirect correctly when a logged out user tries to log out?"""
        with self.client as c:
            resp = c.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome back.', html)

    # def test_logout_success(self):
    #     """Can a user log out?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post('/logout')

    #         self.assertEqual(resp.status_code, 302)
    #         self.assertEqual(resp.location, 'http://localhost/login')
    #         self.assertFalse(session.get(CURR_USER_KEY))

    # def test_logout_success_redirect(self):
    #     """Does the site redirect correctly when a user logs out?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post('/logout', follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Welcome back.', html)
            # self.assertIn('You have logged', html)
    #         self.assertFalse(session.get(CURR_USER_KEY))
    
    def test_list_users_loggedout(self):
        """Does the site deny access to the user list to an anonymous user?"""
        with self.client as c:
            resp = c.get('/users')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')

    def test_list_users_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the user list?"""
        with self.client as c:
            resp = c.get('/users', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_list_users(self):
        """Can the user view a list of current users?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser2', html)
    
    def test_list_users_search(self):
        """Can the user search for another user?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            new_user = User.signup(username='janedoe', email='janedoe@test.com', password='password', image_url=None, header_image_url=None, bio=None, location=None)
            db.session.add(new_user)
            db.session.commit()
            resp=c.get('/users?q=jane')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@janedoe', html)
            self.assertNotIn('@testuser2', html)          


    def test_users_show_loggedout(self):
        """Does the site deny access to a user record to an anonymous user"""
        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')
        
    def test_users_show_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access a user record?"""
        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    # def test_users_show(self):
    #     """Can the user see another user's record?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.get(f'/users/{self.testuser2.id}')
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('@testuser2', html)
    #         self.assertIn('testing 2', html)

    def test_users_show_not_found(self):
        """Does the user see a 404 page if the user is not found for a profile page?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.get('/users/3000')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('blue jay', html)

    def test_show_following_loggedout(self):
        """Does the site deny access to a user's following list to an anonymous user?"""
        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}/following')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')

    def test_show_folowing_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access a user's following list?"""
        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    # def test_show_following(self):
    #     """Can the user see another user's following list?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser2.id
    #         resp = c.get(f'/users/{self.testuser.id}/following')
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('@testuser2', html)
    #         self.assertIn('Unfollow', html)
    #         self.assertNotIn('Follow', html)

    def test_show_following_not_found(self):
        """Does the user see a 404 page if the user is not found for a following page?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.get('/users/3000/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('blue jay', html)

    def test_users_followers_loggedout(self):
        """Does the site deny access to a user's followers list to an anonymous user?"""
        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}/followers')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')

    def test_users_followers_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access a user's followers list?"""
        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)
            
    # def test_users_followers(self):
    #     """Can the user see another user's followers list?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.get(f'/users/{self.testuser2.id}/followers')
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('@testuser', html)
    #         self.assertIn('Follow', html)

    def test_users_folowers_not_found(self):
        """Does the user see a 404 page if the user is not found for a followers page?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.get('/users/3000/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('blue jay', html)

    def test_users_likes_loggedout(self):
        """Does the site deny access to a user's likes list to an anonymous user?"""
        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}/likes')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')
            
    def test_users_likes_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access a user's likes list?"""
        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}/likes', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)
            
    # def test_users_likes(self):
    #     """Can the user see another user's likes page?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         self.testuser2.likes.append(self.msg1)
    #         resp = c.get(f'users/{self.testuser2.id}/likes')
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('testing 1', html)

    def test_users_likes_not_found(self):
        """Does the user see a 404 page if the user is not found for a likes page?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.get('/users/3000/likes')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('blue jay', html)

    def test_add_follow_loggedout(self):
        """Does the site stop an anonymous user from adding a follow?"""
        with self.client as c:
            resp = c.post(f'/users/follow/{self.testuser2.id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')
            
    def test_add_follow_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to add a follow?"""
        with self.client as c:
            resp = c.post(f'/users/follow/{self.testuser2.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)
            
    # def test_add_follow(self):
    #     """Can the user follow another user?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser2.id

    #         resp = c.post(f'/users/follow/{self.testuser.id}')

    #         self.assertEqual(resp.status_code, 302)
    #         self.assertEqual(resp.location, f'/users/{self.testuser2.id}/following')
    #         self.assertIn(self.testuser2.following, self.testuser)

    # def test_add_follow_redirect(self):
    #     """Does the site redirect correctly after a new user follow has been added?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser2.id

    #         resp = c.post(f'/users/follow/{self.testuser.id}', follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('@testuser', html)
    #         self.assertIn(self.testuser2.following, self.testuser)

    def test_stop_following_loggedout(self):
        """Does the site stop an anonymous user from removing a follow?"""
        with self.client as c:
            self.testuser.following.append(self.testuser2)
            db.session.commit()
            resp = c.post(f'/users/stop-following/{self.testuser2.id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')
            
    def test_stop_following_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to remove a follow?"""
        with self.client as c:
            self.testuser.following.append(self.testuser2)
            db.session.commit()
            resp = c.post(f'/users/stop-following/{self.testuser2.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)
            
    # def test_stop_following(self):
    #     """Can the user stop following another user?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
            

    #         resp = c.post(f'/users/stop-following/{self.testuser2.id}')

    #         self.assertEqual(resp.status_code, 302)
    #         self.assertEqual(resp.location, f'/users/{self.testuser.id}/following')
    #         self.assertNotIn(self.testuser2.following, self.testuser)

    # def test_stop_following_redirect(self): 
    #     """Does the site redirect correctly after a user follow has been remove?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id

    #         resp = c.post(f'/users/follow/{self.testuser2.id}', follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertNotIn('@testuser2', html)
    #         self.assertNotIn(self.testuser2.following, self.testuser)

    # def test_profile_loggedout_get(self):
    #     """Does the site stop an anonymous user from accessing an edit profile form?"""
    #     with self.client as c:
    #         resp = c.get('/users/profile')

    #         self.assertEqual(resp.status_code, 302)
    #         self.assertEqual(resp.location, 'http://localhost/')
            
    # def test_profile_loggedout_redirect_get(self):
    #     """Does the site redirect correctly when an anonymous user tries to access an edit profile form?"""
    #     with self.client as c:
    #         resp = c.get('/users/profile', follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Access unauthorized', html)
    
    # def test_profile_loggedout_post(self):
    #     """Does the site stop an anonymous user from editing a profile?"""
    #     with self.client as c:
    #         resp = c.post('/users/profile', data={'username': 'testuser', 'email': 'testuser@test.com', 'password': 'testuser', 'image_url': None, 'header_image_url': None, 'bio': None, 'location': 'New York City'})

    #         self.assertEqual(resp.status_code, 302)
    #         self.assertEqual(resp.location, 'http://localhost/')
            
    # def test_profile_loggedout_redirect_post(self):
    #     """Does the site redirect correctly when an anonymous user tries to edi a user profile?"""
    #     with self.client as c:
    #         resp = c.post('/users/profile', data={'username': 'testuser', 'email': 'testuser@test.com', 'password': 'testuser', 'image_url': None, 'header_image_url': None, 'bio': None, 'location': 'New York City'}, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Access unauthorized', html)
                
    # def test_profile_get(self):
    #     """Does the site display the edit profile for if no form data is submitted?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.get('/users/profile')
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('testuser', html)
    #         self.assertIn('test@test.com', html)


    # def test_profile_success(self):
    #     """Can a user edit their profile?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post('/users/profile', data={'username': 'testuser', 'password': 'testuser', 'email': 'test@test.com', 'image_url': None, 'header_image_url': None, 'bio': None, 'location': 'New York City'})

    #         self.assertEqual(resp.status_code, 302)
    #         self.assertEqual(resp.location, f'/users/{self.testuser.id}') 
    #         self.assertEqual(self.testuser.location, 'New York City')

    # def test_profile_success_redirect(self):
    #     """Does the site redirect correctly when a user edits their profile?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post('/users/profile', data={'username': 'testuser', 'password': 'testuser', 'email': 'test@test.com', 'image_url': None, 'header_image_url': None, 'bio': None, 'location': 'New York City'}, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('New York City', html)

    # def test_profile_authenticate_fail(self):
    #     """Does the site respond correctly when the user puts in the wrong password?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post('/users/profile', data={'username': 'testuser', 'password': 'testuseruser', 'email': 'test@test.com', 'image_url': None, 'header_image_url': None, 'bio': None, 'location': 'New York City'}, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Invalid password', html)
            
    # def test_profile_duplicate_username(self):
    #     """Does the site respond correctly when the user puts in a duplicate username?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post('/users/profile', data={'username': 'testuser2', 'password': 'testuser', 'email': 'test@test.com', 'image_url': None, 'header_image_url': None, 'bio': None, 'location': None}, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Username already taken', html)

    # def test_profile_duplicate_email(self):
    #     """Does the site respond correctly when the user puts in a duplicate email?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post('/users/profile', data={'username': 'testuser', 'password': 'testuser', 'email': 'test2@test.com', 'image_url': None, 'header_image_url': None, 'bio': None, 'location': None}, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Email already taken', html)

    def test_add_remove_likes_loggedout(self):
        """Does the site stop an anonymous user from adding or removing a like?"""
        with self.client as c:
            db.session.add(self.testuser)
            db.session.commit()
            resp = c.post(f'/users/add_like/{self.msg2.id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')
            
    def test_add_remove_likes_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to add or remove a like?"""
        with self.client as c:
            self.testuser.likes.append(self.msg2)
            db.session.add(self.testuser)
            db.session.commit()
            resp = c.post(f'/users/add_like/{self.msg2.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)
            
    # def test_add_remove_likes_add(self):
    #     """Can a user like a message?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post(f'/users/add_like/{self.msg2.id}')
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('testing 2', html)
    #         self.assertIn('btn-primary', html)

    # def test_add_remove_likes_remove(self):
    #     """Can a user unlike a message?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         self.testuser.likes.append(self.msg2)
    #         db.session.add(self.testuser)
    #         db.session.commit()
    #         resp = c.post(f'/users/add_like/{self.msg2.id}')
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertNotIn('testing 2', html)

    def test_delete_user_loggedout(self):
        """Does the site stop an anonymous user from deleting a user?"""
        with self.client as c:
            resp = c.post('/users/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')
            
    def test_delete_user_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to delete a user?"""
        with self.client as c:
            resp = c.post('/users/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)
            
    # def test_delete_user(self):
    #     """Can a user delete their account?"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post('/users/delete')

    #         self.assertEqual(resp.status_code, 302)
    #         self.assertEqual(resp.location, 'http://localhost/signup')
    #         self.assertFalse(session.get(CURR_USER_KEY))

    # def test_delete_user_redirect(self):
    #     """Does the site redirect correctly when a user deletes their account"""
    #     with self.client as c:
    #         with c.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post('/users/delete', follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Join Warbler today', html)
    #         self.assertEqual(g.user, None)