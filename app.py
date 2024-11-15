import sys
import yfinance as yf
import pandas as pd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                           QComboBox, QPushButton, QListWidget, QLabel, 
                           QDateEdit, QTableWidget, QTableWidgetItem, QHBoxLayout)
from datetime import datetime, timedelta

class StockDataUI(QMainWindow):
    def __init__(self, optimize_portfolio_func):
        super().__init__()
        self.optimize_portfolio_func = optimize_portfolio_func  # Store the optimization function
        self.setWindowTitle("Portfolio Optimizer")
        self.setGeometry(100, 100, 1000, 800)
        
        # Store all tickers
        self.all_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM",
            "V", "WMT", "PG", "JNJ", "XOM", "BAC", "DIS", "NFLX", "CSCO",
            "INTC", "PFE", "KO", "PEP", "CMCSA", "VZ", "CVX", "ABT"
        ]
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left and right layouts for better organization
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        # Create widgets
        self.setup_left_panel(left_layout)
        self.setup_right_panel(right_layout)
        
        # Initialize combo box
        self.ticker_filter.addItems(sorted(self.all_tickers))

    def setup_left_panel(self, layout):
        # Ticker search/filter combobox
        self.ticker_filter = QComboBox()
        self.ticker_filter.setEditable(True)
        self.ticker_filter.setInsertPolicy(QComboBox.NoInsert)
        # self.ticker_filter.lineEdit().textChanged.connect(self.filter_tickers)
        layout.addWidget(QLabel("Search Tickers:"))
        layout.addWidget(self.ticker_filter)
        
        # Selected tickers list
        self.selected_tickers = QListWidget()
        layout.addWidget(QLabel("Selected Tickers:"))
        layout.addWidget(self.selected_tickers)
        
        # Date range selection
        date_layout = QVBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setDate(datetime.now().date() - timedelta(days=365))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(QLabel("Start Date:"))
        date_layout.addWidget(self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(datetime.now().date())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(QLabel("End Date:"))
        date_layout.addWidget(self.end_date)
        
        layout.addLayout(date_layout)
        
        # Buttons
        self.add_button = QPushButton("Add Ticker")
        self.add_button.clicked.connect(self.add_ticker)
        layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_ticker)
        layout.addWidget(self.remove_button)
        
        self.optimize_button = QPushButton("Optimize Portfolio")
        self.optimize_button.clicked.connect(self.optimize_portfolio)
        layout.addWidget(self.optimize_button)
        
        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def setup_right_panel(self, layout):
        # Results section title
        layout.addWidget(QLabel("Optimization Results"))
        
        # Create table for weights
        self.weights_table = QTableWidget()
        self.weights_table.setColumnCount(2)
        self.weights_table.setHorizontalHeaderLabels(['Ticker', 'Weight'])
        layout.addWidget(self.weights_table)
        
        # Portfolio metrics section
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(['Metric', 'Value'])
        layout.addWidget(QLabel("Portfolio Metrics"))
        layout.addWidget(self.metrics_table)

    def filter_tickers(self, text):
        self.ticker_filter.addItem(text)

    def add_ticker(self):
        current_ticker = self.ticker_filter.currentText().upper()
        if current_ticker and current_ticker not in self.get_selected_tickers():
            self.selected_tickers.addItem(current_ticker)

    def remove_ticker(self):
        for item in self.selected_tickers.selectedItems():
            self.selected_tickers.takeItem(self.selected_tickers.row(item))

    def get_selected_tickers(self):
        return [self.selected_tickers.item(i).text() 
                for i in range(self.selected_tickers.count())]

    def update_weights_table(self, weights_dict):
        self.weights_table.setRowCount(len(weights_dict))
        for i, (ticker, weight) in enumerate(weights_dict.items()):
            # Ticker
            ticker_item = QTableWidgetItem(ticker)
            self.weights_table.setItem(i, 0, ticker_item)
            
            # Weight (formatted as percentage)
            weight_item = QTableWidgetItem(f"{weight:.2%}")
            self.weights_table.setItem(i, 1, weight_item)
        
        self.weights_table.resizeColumnsToContents()

    def update_metrics_table(self, metrics_dict):
        self.metrics_table.setRowCount(len(metrics_dict))
        for i, (metric, value) in enumerate(metrics_dict.items()):
            # Metric name
            metric_item = QTableWidgetItem(metric)
            self.metrics_table.setItem(i, 0, metric_item)
            
            # Metric value (formatted based on type)
            if isinstance(value, float):
                value_str = f"{value:.4f}"
            else:
                value_str = str(value)
            value_item = QTableWidgetItem(value_str)
            self.metrics_table.setItem(i, 1, value_item)
        
        self.metrics_table.resizeColumnsToContents()

    def optimize_portfolio(self):
        selected_tickers = self.get_selected_tickers()
        if len(selected_tickers) < 2:
            self.status_label.setText("Please select at least 2 tickers")
            return
        
        try:
            self.status_label.setText("Fetching data and optimizing...")
            QApplication.processEvents()  # Update UI
            
            # Fetch the data
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            data = yf.download(
                selected_tickers,
                start=start_date,
                end=end_date
            )
            
            # Extract closing prices
            if len(selected_tickers) == 1:
                prices_df = data['Close'].to_frame()
            else:
                prices_df = data['Close']
            
            print('runs to here')
            # Run optimization
            optimization_results = self.optimize_portfolio_func(prices_df)
            print(optimization_results)
            
            # Update the UI with results
            self.update_weights_table(optimization_results['weights'])
            if 'metrics' in optimization_results:
                self.update_metrics_table(optimization_results['metrics'])
            
            self.status_label.setText("Portfolio optimization completed successfully")
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

def main(optimize_portfolio_func):
    app = QApplication(sys.argv)
    window = StockDataUI(optimize_portfolio_func)
    window.show()
    sys.exit(app.exec_())