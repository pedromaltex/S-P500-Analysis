import requests

import pandas as pd

from flask import redirect, render_template, session
from functools import wraps
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import datetime

import requests
from datetime import datetime, timezone

from yahooquery import Screener

# Defina sua chave API do Finnhub
API_KEY = "cv3qp99r01ql2eusvo70cv3qp99r01ql2eusvo7g" 

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def lookup(symbol):
    """Look up quote for symbol using yfinance."""

    # Validar o símbolo de entrada
    if not isinstance(symbol, str) or len(symbol) == 0:
        print("Erro: O símbolo deve ser uma string não vazia.")
        return None

    try:
        # Buscar dados de ações usando yfinance
        ticker = yf.Ticker(symbol.upper())
        stock_info = ticker.info

        # Tentar diferentes campos para obter o preço
        if 'regularMarketPrice' in stock_info:
            price = stock_info['regularMarketPrice']
        elif 'last_price' in stock_info:
            price = stock_info['last_price']
        elif 'previousClose' in stock_info:
            price = stock_info['previousClose']
        else:
            print(f"Erro: Não foi possível encontrar o preço de {symbol}.")
            return None

        # Verificar se a empresa foi encontrada
        if 'longName' in stock_info:
            return {
                "name": stock_info["longName"],
                "price": price,
                "symbol": symbol.upper()
            }
        else:
            print(f"Erro: Não foi possível encontrar o nome da empresa para {symbol}.")
            return None

    except ValueError as e:
        print(f"Erro de análise de dados: {e}")
    except KeyError as e:
        print(f"Erro de chave: Dados esperados ausentes para {symbol}.")
    except Exception as e:
        print(f"Erro: Problema ao buscar dados para {symbol}. {e}")

    return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def get_data(symbol, period='1y', interval='1d'):

    if symbol == "PORTFOLIO":
        #TODO Colocar aqui o gráfico da evolução da carteira ao longo do tempo
        return None
    data = yf.download(tickers=symbol, period=period, interval=interval)

    data.reset_index(inplace=True)

    #Caso o DataFrame tenha um MultiIndex, remover os níveis extras
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)  # Remove o primeiro nível do índice

    if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
        data = data[["Datetime", "Open", "Close"]]

        # Convertendo datas para string no formato ISO para facilitar a serialização
        data['Datetime'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Convertendo para listas compatíveis com JSON
        labels = data['Datetime'].tolist()

        #values = data['Close'].tolist() é a versão simplificada, mas como só queria 2 casas decimais, tive de por esta versão manhosa em baixo
        values = [round(v, 2) for v in data['Close'].tolist()]

    elif interval in ['1d', '5d', '1wk', '1mo', '3mo']:
        data = data[["Date", "Open", "Close"]]

        # Convertendo datas para string no formato ISO para facilitar a serialização
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')

        # Convertendo para listas compatíveis com JSON
        labels = data['Date'].tolist()

        #values = data['Close'].tolist() é a versão simplificada, mas como só queria 2 casas decimais, tive de por esta versão manhosa em baixo
        values = [round(v, 2) for v in data['Close'].tolist()]
    else:
        raise ValueError("Meteste um valor errado no interval, estes são os válidos: \
                         1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
    return labels, values

def get_data_percent(symbol, period='1y', interval='1d'):
    labels, values = get_data(symbol, period, interval)  # Obtém os valores absolutos
    
    # Calcular a variação percentual
    percent_changes = [0]  # O primeiro valor é sempre 0, pois não há variação anterior
    
    for i in range(1, len(values)):
        percent_change = ((values[i] - values[i - 1]) / values[i - 1]) * 100
        percent_changes.append(round(percent_change, 2))  # Arredondar para 2 casas decimais
    
    return labels, percent_changes

def get_news(symbol, max_news=100):
    """Obtém notícias financeiras para um símbolo específico usando Finnhub"""
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2024-01-01&to={datetime.today().strftime("%Y-%m-%d")}&token={API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"[ERROR] Falha ao buscar notícias do Finnhub para {symbol}")
            return []

        data = response.json()

        news_list = []
        for article in data[:max_news]:  # Pega até 'max_news' notícias
            date_parsed = datetime.fromtimestamp(article["datetime"], tz=timezone.utc) if "datetime" in article else None

            news_list.append({
                "title": article.get("headline", "Sem título"),
                "link": article.get("url", "#"),
                "content": article.get("summary", "Sem descrição disponível"),
                "date": date_parsed,
                "publisher": article.get("source", "Desconhecido"),
                "image": article.get("image", None)  # Obtém a imagem da notícia
            })

        return news_list

    except Exception as e:
        print(f"[ERROR] Erro ao buscar notícias para {symbol}: {str(e)}")
        return []

def correlation(target_ticker, market_ticker, years_ago): # Tem bug caso o ano atual seja bissexto e o há years_ago não seja
    # Baixar os dados históricos
    day, month, year = datetime.now().day, datetime.now().month, datetime.now().year

    # Baixar os dados históricos para os dois períodos
    data1 = yf.download(target_ticker, start=f"{year-years_ago}-{month}-{day}", end=f"{year}-{month}-{day}")["Close"]
    data2 = yf.download(market_ticker, start=f"{year-years_ago}-{month}-{day}", end=f"{year}-{month}-{day}")["Close"]

    # Criar um DataFrame único com os dados
    data = pd.concat([data1, data2], axis=1)

    # Calcular retornos diários
    returns = data.pct_change().dropna()

    # Calcular a correlação
    correlation = returns.corr().iloc[0, 1]
    correlation = round(correlation, 4)

    return correlation

def get_companiesbysector(sector): # Obtém 100 maiores empresas do determinado setor
    sector_indices = [
    'ms_basic_materials',
    'ms_communication_services',
    'ms_consumer_cyclical',
    'ms_consumer_defensive',
    'ms_energy',
    'ms_financial_services',
    'ms_healthcare',
    'ms_industrials',
    'ms_real_estate',
    'ms_technology',
    'ms_utilities',
    'most_visited_basic_materials',
    'most_visited_communication_services',
    'most_visited_consumer_cyclical',
    'most_visited_consumer_defensive',
    'most_visited_energy',
    'most_visited_financial_services',
    'most_visited_healthcare',
    'most_visited_industrials',
    'most_visited_real_estate',
    'most_visited_technology',
    'most_visited_utilities'
]

        
    # Obtém as empresas do setor escolhido
    screener = Screener()
    data = screener.get_screeners(sector, count=100)  # Pode ajustar 'count'

    #print(data[sector]['quotes'][0]['symbol'])

    # Extraindo os símbolos das empresas
    sector_tickers = [stock['symbol'] for stock in data[f'ms_{sector}']['quotes']]
    return sector_tickers

# Ter o intervalo de tempo a retirar tendo em conta periodo total a consideral
def get_interval(period):
    grupos = [('1d','1m'), ('1wk','1h'), ('1mo','1h'), ('YTD','1h'), ('1y','1d'), ('5y','1wk'), ('20y','1mo'), ('99y','3mo')]
    for i in range(len(grupos)):
        if period == grupos[i][0]:
            return grupos[i][1]
    raise ValueError('Colocou valor errado em get_interval')

# Comparar duas empresas em termos de alteração de percentagem num tempo específico.
def compare2(stock1, stock2, period): #TODO#
    data1 = get_data_percent(stock1, period, get_interval(period))
    data2 = get_data_percent(stock2, period, get_interval(period))
    return {"label1": data1[0],
            "label2": data2[0],
            "value1": data1[1],
            "value2": data2[1]}


import yfinance as yf
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone
from yahooquery import Screener


def dowl_data_return_dataset(target_data, market_data, start, end):
    # Baixar os dados históricos para os dois períodos
    data1 = yf.download(target_data, start=start, end=end)["Close"]
    data2 = yf.download(market_data, start=start, end=end)["Close"]

    # Criar um DataFrame único com os dados
    data = pd.concat([data1, data2], axis=1)

    return data

def calc_returns_daily(dataset):
    # Calcular retornos diários
    returns = dataset.pct_change().dropna()
    return returns

def calc_corr(dataset_returns):
    # Calcular a correlação
    correlation = dataset_returns.corr().iloc[0, 1]
    return correlation

################## tentar implementar correlacao setores
import seaborn as sns


sector_mapping = {
                    'Basic Materials': 'ms_basic_materials',
                    'Communication Services': 'ms_communication_services',
                    'Consumer Cyclical': 'ms_consumer_cyclical',
                    'Consumer Defensive': 'ms_consumer_defensive',
                    'Energy': 'ms_energy',
                    'Financial Services': 'ms_financial_services',
                    'Healthcare': 'ms_healthcare',
                    'Industrials': 'ms_industrials',
                    'Real Estate': 'ms_real_estate',
                    'Technology': 'ms_technology',
                    'Utilities': 'ms_utilities'
                }
            
# Return list of tickers of each company
def get_companiesbysector(sector):  # Obtém 100 maiores empresas do determinado setor
    if sector not in list(sector_mapping.keys()):
        raise ValueError(f"Setor inválido: {sector}. Escolha um dos seguintes: {list(sector_mapping.keys())}")

    screener_id = sector_mapping[sector]
    screener = Screener()
    data = screener.get_screeners(screener_id, count=100)

    # Verifica se os dados retornaram corretamente
    if screener_id not in data or 'quotes' not in data[screener_id]:
        raise ValueError(f"Não foi possível obter dados para o setor: {sector}")

    # Extraindo os símbolos das empresas
    sector_tickers = [stock['symbol'] for stock in data[screener_id]['quotes']]
    return sector_tickers

# Função heatmap
def heatmap(dataset1, dataset2):

    # Preencher dados ausentes com o último valor disponível
    dataset1 = dataset1.fillna(1)
    dataset2 = dataset2.fillna(1)

    # Calcular as percentagens diárias
    returns1 = dataset1.pct_change().dropna()
    returns2 = dataset2.pct_change().dropna()

    correlation_by_company = {}
    for company1 in returns1.columns:
        correlation_by_company[f'{company1}'] = {}
        for company2 in returns2.columns:
            merged_df = pd.concat([returns1[company1], returns2[company2]], axis=1)
            correlation_by_company[f'{company1}'][f'{company2}'] = merged_df[company1].corr(merged_df[company2])

    # Converter o dicionário de correlações em um DataFrame
    correlation_df = pd.DataFrame.from_dict(correlation_by_company, orient='index')

    # Gerar o heatmap
    plt.figure(figsize=(40, 40))
    sns.heatmap(correlation_df, annot=False, cmap='coolwarm', center=0, linewidths=0.5, cbar=True)

    # Personalizar o gráfico
    plt.title(f'Correlação Anual: Empresas do Setor {list(sector_mapping.keys())[0]} vs. {list(sector_mapping.keys())[1]}') # ALTERAR ISTO NOS INDICES TODO
    plt.xlabel('Ano')
    plt.ylabel('Empresas')

    #plt.savefig(f"{sector_mapping.keys()[i]}_{sector_mapping.keys()[j]}.png", dpi=300, bbox_inches='tight')

    # Exibir o gráfico
    plt.show()


# Return the dataset of each ticker in a list
def download_data(tickers, start, end):
    return yf.download(tickers, start=start, end=end)['Close']




'''
for i in range(len(sector_mapping.keys())):
    # Obtendo tickers dos setores desejados
    dataset1 = datasetpro[i]
    for j in range(len(sector_mapping.keys())):
        if i != j:
            dataset2 = datasetpro[j]
            mae(dataset1, dataset2)
'''
