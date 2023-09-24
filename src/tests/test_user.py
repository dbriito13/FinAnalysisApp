from models.user import User


def test_normal_user():
    normal_user = User('danielbrito', 'password')
    assert normal_user.username == 'danielbrito'
    assert normal_user.password == 'password'
