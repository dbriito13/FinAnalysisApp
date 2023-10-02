from app import app, db, bcrypt
from models.user import User
import unittest


class TestEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        app.config['TESTING'] = True
        app.config['WTF_CSRF_METHODS'] = []

    def test_home(self):
        tester = app.test_client(self)
        response = tester.get("/")
        self.assertEqual(response.status_code, 200)

    def test_register_reachable(self):
        tester = app.test_client(self)
        response = tester.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_login_reachable(self):
        tester = app.test_client(self)
        response = tester.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        # Creating test user in db
        User.query.filter(User.username == "testuser").delete()
        user = User(username="testuser",
                    password=bcrypt.generate_password_hash("testPassword1"),
                    searches="")
        db.session.add(user)
        db.session.commit()
        # Test login redirects
        tester = app.test_client(self)
        response = tester.post("/login",
                               data={
                                   "username": "testuser",
                                   "password": "testPassword1"
                               })
        self.assertEqual(response.status_code, 302)
        response = tester.get('/logout')
        self.assertEqual(response.status_code, 302)
        User.query.filter(User.username == "testuser").delete()
        db.session.commit()
