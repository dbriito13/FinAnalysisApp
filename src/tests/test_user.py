from models.user import User
import unittest


class TestUser(unittest.TestCase):
    def test_normal_user(self):
        normal_user = User('danielbrito', 'password')
        self.assertEqual(normal_user.username, 'danielbrito')
        self.assertEqual(normal_user.password, 'password')


if __name__ == '__main__':
    unittest.main()