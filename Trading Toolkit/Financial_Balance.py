# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 19:55:44 2024

@author: serw1
"""

import yfinance as yf
import pandas as pd

# List of tickers
tickers = ['AAPL', 'MSFT', 'GOOGL']  # Add your tickers here

# Columns to collect
columns = ['Total Revenue', 'Cost Of Revenue', 'Selling General And Administration', 'Operating Expense', 
           'Total Expenses', 'Research And Development', 'Net Income', 'EBITDA', "Normalized EBITDA",'Free Cash Flow']

# Function to get financial data
def get_financial_data(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.T
    cashflow = stock.cashflow.T
    
    data = pd.DataFrame(index=financials.index)
    
    # Collecting financial data
    for col in columns:
        if col in financials.columns:
            data[col] = financials[col]
        elif col in cashflow.columns:
            data[col] = cashflow[col]
        else:
            data[col] = None  # Fill with None if column is not available
    
    return data

# Collect data for each ticker
all_data = {}
for ticker in tickers:
    all_data[ticker] = get_financial_data(ticker)

# Combine all data into a single DataFrame
combined_data = pd.concat(all_data, axis=1)

# Save to Excel
combined_data.to_excel('financial_statements.xlsx')

print("Financial data collected and saved to 'financial_statements.xlsx'")
