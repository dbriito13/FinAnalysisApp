#!/usr/bin/env python3

import sys

from flask import Flask, request, render_template, redirect
from routes.get_ticker_info import TickerFetcher

app = Flask(__name__)


@app.route("/")
def main():
    return '''
     <form action="/ticker" method="GET">
         <input name="ticker">
         <input type="submit" value="Submit!">
     </form>
     '''


@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return "You entered: " + input_text


@app.route("/ticker", methods=["GET"])
def ticker():
    ticker = request.args.get('ticker')
    tickerFetcher = TickerFetcher(ticker)
    prev_close, daily_change, eps_ttm, pe_ratio = tickerFetcher.get_ticker_info(ticker)
    print(f"{prev_close}|{daily_change}|{eps_ttm}|{pe_ratio}|", file=sys.stderr)
    return render_template('ticker.html', ticker='AAPL')


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/ticker')
    return render_template('login.html', error=error)
