# Investment Portfolio Manager

#### Video Demo: <URL HERE>

## Description:
The **Investment Portfolio Manager** is a web application that allows users to manage their stock investments efficiently. This platform provides real-time stock data, portfolio tracking, and transaction history while integrating advanced features such as stock predictions and interactive charts. The project was developed as part of CS50’s final project, showcasing proficiency in web development, finance APIs, and database management.

## Features:
- **User Authentication**: Users can register, log in, and securely manage their investment portfolio.
- **Portfolio Management**: Users can buy and sell stocks, view their current holdings, and track gains/losses.
- **Stock Lookup**: Real-time stock data retrieval using Yahoo Finance API.
- **Transaction History**: A detailed log of all buy/sell transactions.
- **Interactive Charts**: Users can visualize stock performance over different timeframes.
- **Deposit Funds**: Users can add virtual money to their portfolio.
- **Market News (Upcoming)**: A dedicated page to display financial news (not implemented yet).
- **Stock Price Prediction (Upcoming)**: Integration with a machine learning model to predict stock trends (not implemented yet).

## File Structure:
- `app.py`: The core Flask application handling routes, authentication, and database interactions.
- `helpers.py`: Contains utility functions like `lookup()` for retrieving stock data and `usd()` for formatting currency.
- `finance.db`: SQLite database storing user information, portfolio details, and transaction history.
- `templates/`: Contains HTML templates for the web interface, including:
  - `index.html`: Main dashboard displaying portfolio and stock charts.
  - `quote.html`: Page to search for stock prices.
  - `buy.html`: Page for purchasing stocks.
  - `sell.html`: Page for selling stocks.
  - `history.html`: Displays transaction history.
  - `register.html`: User registration page.
  - `login.html`: User login page.
  - `deposit.html`: Allows users to add funds.
- `static/`: Contains CSS, JavaScript, and image assets.

## Design Choices:
- **Flask Framework**: Chosen for its simplicity and efficiency in handling web applications.
- **SQLite Database**: Used for ease of deployment and integration with Flask.
- **Yahoo Finance API**: Provides real-time stock data.
- **Session-Based Authentication**: Ensures user security and persistence across sessions.
- **JSON for Data Storage**: Used in session management and API responses.

## Challenges and Future Improvements:
1. **Graph Issues**: The main graph on the homepage is not displaying S&P 500 data correctly. Further debugging is needed.
2. **Stock Prediction Feature**: Integration with a machine learning model is pending.
3. **Market News Section**: Yet to be implemented.
4. **Performance Optimization**: Currently, some database queries can be optimized for faster performance.

This project demonstrates key concepts in web development, financial APIs, and database management, making it a valuable tool for users interested in tracking and managing their investments. Future enhancements will include AI-based stock predictions and integration with live news feeds to provide a comprehensive investment management platform.

