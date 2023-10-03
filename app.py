#!/usr/bin/env python3

import sys

from flask import request, Flask, flash, session, render_template, redirect
import get_ticker_info
import ticker_graphs
from flask_login import login_user, UserMixin, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os 
from healthcheck import HealthCheck
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import re
import click
from flask.cli import with_appcontext


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=5, max=50)])
    password = PasswordField(validators=[InputRequired(),
                                         Length(min=5, max=50)])
    submit = SubmitField('Login')

    def validate_username(self, username):
        '''
        Validate that the username exists
        '''
        user = User.query.filter(User.username == username.data).first()
        if user is None:
            raise ValidationError("Username does not exist!")


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=5, max=50)])
    password = PasswordField(validators=[InputRequired(),
                                         Length(min=5, max=50)])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        '''
        Validate that the username does not already exist
        '''
        user = User.query.filter(User.username == username.data).first()
        if user is not None:
            raise ValidationError("Username already in use!")

    def validate_password(self, password):
        '''
        Simple password validation
        '''
        has_number = bool(re.search(r'\d', password.data))
        has_uppercase = bool(re.search(r'\w*[A-Z]\w*', password.data))
        if not has_number or not has_uppercase:
            raise ValidationError("Password must contain a number"
                                  " and uppercase letter")


if os.environ.get('DATABASE_URL') is not None:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///Users.sqlite3'

if os.environ.get('SECRET_KEY') is not None:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
else:
    SECRET_KEY = 'ldfjsolasfuasdfjsodfusoij4w09r8pswojufsldkfjdf9'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.app_context().push()


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()


app.cli.add_command(create_tables)


db = SQLAlchemy()
db.init_app(app)
bcrypt = Bcrypt(app)
health = HealthCheck()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    searches = db.Column(db.String, nullable=True)


@app.route("/")
def main():
    # If logged in, then AAPL, if not then login
    return '''
     <form action="/ticker" method="GET">
         <input name="ticker">
         <input type="submit" value="Submit!">
     </form>
     '''


@app.route("/ticker", methods=["GET"])
def ticker():
    ticker = request.args.get('ticker')
    tickerFetcher = get_ticker_info.TickerFetcher(ticker)
    (prev_close, daily_chg,
     prev_vol, daily_chg_vol, prices) = tickerFetcher.get_ticker_info(ticker)
    tickerGraphs = ticker_graphs.TickerGraphs(prices, ticker)
    plot_prices, plot_vol = tickerGraphs.generate_plots()
    searches = []
    logged_in = False
    if current_user.is_authenticated:
        searches = session["searches"]
        logged_in = True
    return render_template('ticker.html',
                           ticker=ticker,
                           data=plot_prices,
                           aux=plot_vol,
                           prev_vol=prev_vol,
                           prev_close=prev_close,
                           daily_chg=daily_chg,
                           daily_chg_vol=daily_chg_vol,
                           searches=searches,
                           logged_in=logged_in)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/ticker?ticker=AAPL")
    session.pop('_flashes', None)
    form = LoginForm(meta={'csrf': False})
    if form.validate_on_submit():
        # Find user with the specified 
        user = User.query.filter(User.username == form.username.data) \
                         .first()
        if user is not None:
            if bcrypt.check_password_hash(user.password,
                                          form.password.data):
                flash('You were successfully logged in')
                login_user(user)
                session["username"] = form.username.data
                if user.searches != "" and user.searches is not None:
                    session["searches"] = user.searches.split(",")
                else:
                    session["searches"] = []
                return redirect("/ticker?ticker=AAPL")
        else:
            flash('Wrong login credentials')
    if request.method == 'POST':
        flash('Wrong login credentials')
    return render_template('login.html', login_form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/ticker?ticker=AAPL")
    session.pop('_flashes', None)
    form = RegisterForm(meta={'csrf': False})
    if form.validate_on_submit():
        # Create User model and upload to 
        user = User(username=form.username.data,
                               password=bcrypt.generate_password_hash(form.password.data),
                               searches="")
        db.session.add(user)
        db.session.commit()
        return redirect("/ticker?ticker=AAPL")
    else:
        if request.method == 'POST':
            flash('Something went wrong, check the input.')
    return render_template('register.html', form=form)


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    session.pop('_flashes', None)
    if session["username"]:
        user = User.query.filter(User.username == session["username"]) \
            .first()
        session["searches"] = user.searches.split(",")
        print(session["searches"], flush=True, file=sys.stderr)
        return render_template('profile.html',
                               username=session["username"],
                               searches=session["searches"])

    return redirect("/login")


@app.route('/save_search', methods=['GET'])
@login_required
def save_search():
    session.pop('_flashes', None)
    ticker = request.args.get('ticker')
    if ticker:
        if ticker not in session["searches"]:
            session["searches"].append(ticker)
            session.modified = True
            print(session["searches"], flush=True, file=sys.stderr)
            # Save searches to User model
            user = User.query.filter(User.username == session["username"]) \
                             .first()
            user.searches = ",".join(session["searches"])
            db.session.commit()
            print(session["searches"], flush=True, file=sys.stderr)
            return "OK"
    else:
        return "ERR"


@app.route('/remove_search', methods=['GET'])
@login_required
def remove_search():
    session.pop('_flashes', None)
    ticker = request.args.get('ticker')
    if ticker:
        session["searches"].remove(ticker)
        session.modified = True
        user = User.query.filter(User.username == session["username"]) \
                   .first()
        user.searches = ",".join(session["searches"])
        db.session.commit()
        return "OK"
    else:
        return "ERR"


@app.route('/remove_all_searches', methods=['GET'])
@login_required
def remove_all_searches():
    session.pop('_flashes', None)
    session["searches"] = []
    session.modified = True
    user = User.query.filter(User.username == session["username"]).first()
    user.searches = ""
    db.session.commit()
    return redirect('/profile')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect('/login')


def app_reachable():
    tester = app.test_client()
    response = tester.get("/register")
    if response.status_code == 200:
        return True, "App is Reachable"
    return False, "App is not Reachable"


def login_reachable():
    # Creating test user in db
    User.query.filter(User.username == "testuser").delete()
    user = User(username="testuser",
                password=bcrypt.generate_password_hash("testPassword1"),
                searches="")
    db.session.add(user)
    db.session.commit()
    # Test login redirects
    tester = app.test_client()
    response_1 = tester.post("/login",
                             data={
                                "username": "testuser",
                                "password": "testPassword1"
                             })
    response_2 = tester.get('/logout')
    User.query.filter(User.username == "testuser").delete()
    db.session.commit()
    if response_1.status_code == 302 \
            and response_2.status_code == 302:
        return True, "Login Works"
    return False, "Login Not Working"


health.add_check(app_reachable)
health.add_check(login_reachable)

app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
