import app
import unittest


class TestEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        app.app.config['TESTING'] = True
        app.app.config['WTF_CSRF_METHODS'] = []
        self.tester = app.app.test_client(self)

    def test_home(self):
        
        response = self.tester.get("/")
        self.assertEqual(response.status_code, 200)

    def test_register_reachable(self):
        
        response = self.tester.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_login_reachable(self):
        response = self.tester.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        # Creating test user in database.db
        try:
            app.User.query.filter(app.User.username == "testuser").delete()
        finally:
            user = app.User(username="testuser",
                        password=app.bcrypt.generate_password_hash("testPassword1"),
                        searches="")
            app.db.session.add(user)
            app.db.session.commit()
            # Test login redirects
            
            response = self.tester.post("/login",
                                    data={
                                        "username": "testuser",
                                        "password": "testPassword1"
                                    })
            self.assertEqual(response.status_code, 302)
            response = self.tester.get('/logout')
            self.assertEqual(response.status_code, 302)
