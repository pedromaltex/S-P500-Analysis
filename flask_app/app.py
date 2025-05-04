import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask import jsonify
from datetime import datetime, timezone
import yfinance as yf
import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt


from helpers import apology, login_required, lookup, usd, get_data, get_news, correlation, get_interval, get_data_percent, compare2, dowl_data_return_dataset, calc_returns_daily, calc_corr, get_companiesbysector, heatmap, download_data

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Sets the time of the events
current_time = datetime.now()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Deixar predefinido o gráfico de 1 ano
    selected_options = ['1y']
    stock_total = 0

    period = ['1d', '1wk', '1mo', 'YTD', '1y', '5y', '20y']
    interval = ['1m', '1h', '1h', '1h', '1d', '1wk', '1mo']

    # Processar a seleção do período quando o formulário é submetido
    if request.method == "POST":
        selected_options = request.form.getlist('selecao')

        for i in range(len(period)):
            if selected_options[0] == period[i]:
                data = get_data("^GSPC", period[i], interval[i])  # Sempre usar ^GSPC no index

        session['index_labels'] = data[0]
        session['index_values'] = data[1]
        session['index_selected_options'] = selected_options

        return redirect("/")

    # Obter dados do portfólio do utilizador
    portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?", session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']

    # Garantir que as variáveis têm os tipos corretos para cálculos no Jinja
    for stock in portfolio:
        stock["total"] = int(stock["shares"]) * float(stock["price"])
        stock_total += stock["total"]

    # Obter os dados do S&P 500 (por enquanto)
    data = get_data("^GSPC", period[4], interval[4])  # TODO: Substituir ^GSPC por PORTFOLIO quando a função estiver completa
    labels, values = data

    # Buscar os dados da sessão para GET requests
    labels = session.get('index_labels', [])
    values = session.get('index_values', [])
    selected_options = session.get('index_selected_options', [])

    #########################################################################################################################
    # TODO: O gráfico da página principal não está a ser do S&P 500 e sim do quoted, e não sei porque isto está a acontecer #
    #########################################################################################################################

    return render_template(
        "index.html",
        portfolio=portfolio,
        cash=float(cash),
        stock_total=float(stock_total),
        portfolio_json=json.dumps(portfolio),
        labels=labels,
        values=values,
        period=period,
        interval=interval,
        selected_options=selected_options
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
