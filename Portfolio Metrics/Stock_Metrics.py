# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 00:14:21 2024

@author: serw1
"""

import pandas as pd
import yfinance as yf
from collections import Counter

# Define the stock ticker
ticker = "DUK"  # replace with your chosen stock symbol


def stock_metrics(ticker):
    # Fetch financial data
    stock = yf.Ticker(ticker)
    financials = stock.financials.T
    cashflow = stock.cashflow.T
    stock = yf.Ticker(ticker)
    # Get the name of the stock
    stock_name = stock.info['longName']
    
    
    """
    def get_financials(key):
       return financials.get(key, 0)
    
    # Extract necessary parameters
    df = pd.DataFrame({
        "Revenue": [get_financials("Total Revenue")],
        "Cost of Sales": [get_financials("Cost Of Revenue")],
        "SD&A": [get_financials("Selling General And Administration")],
        "Operating Expenses": [get_financials("Operating Expense")],
        "Total Expenses": [get_financials("Total Expenses")],
        "R&D": [get_financials("Research And Development")],
        "Net Income": [get_financials("Net Income")],
        "FCF": cashflow["Free Cash Flow"]
    })
    
    # Function to convert values and determine unit
    def convert_value(value):
        if value >= 1e9:
            return value / 1e9, "B USD"
        elif value >= 1e6:
            return value / 1e6, "M USD"
        elif value >= 1e3:
            return value / 1e3, "K USD"
        else:
            return value, "USD"
    
    # Apply conversion to the dataframe and collect units
    df_converted = pd.DataFrame()
    units = pd.DataFrame(index=df.index, columns=df.columns)
    for column in df.columns:
        converted_values = df[column].apply(convert_value)
        df_converted[column] = [val[0] for val in converted_values]
        units[column] = [val[1] for val in converted_values]
    
    # Find the most common unit for the entire table
    most_common_unit = Counter(units.values.flatten()).most_common(1)[0][0]
    
    # Convert all values to the most common unit
    def unify_units(value, unit, target_unit):
        conversion_factors = {
            "USD": 1,
            "K USD": 1e3,
            "M USD": 1e6,
            "B USD": 1e9
        }
        return value * conversion_factors[unit] / conversion_factors[target_unit]
    
    df_unified = pd.DataFrame()
    for column in df_converted.columns:
        df_unified[column] = [
            unify_units(val, unit, most_common_unit) for val, unit in zip(df_converted[column], units[column])
        ]
    
    # Apply formatting to the dataframe
    df_unified_formatted = df_unified.applymap(lambda x: f"${x:.2f} {most_common_unit}")
    
    # Add TTM
    #df["TTM Revenue"] = financials["Total Revenue"].sum()
    #df["TTM Cost of Sales"] = financials["Cost Of Revenue"].sum()
    #df["TTM SD&A"] = financials["Selling General Administrative"].sum()
    #df["TTM Operating Expenses"] = financials["Total Operating Expenses"].sum()
    #df["TTM Net Income"] = financials["Net Income"].sum()
    #df["TTM FCF"] = cashflow["Free Cash Flow"].sum()
    """
    # Fetch stock metrics
    info = stock.info

# Function to safely get the metric
    def get_metric(key):
       return info.get(key, 0)

    # Fetch stock metrics, filling in blanks if not found
    metrics_df = pd.DataFrame({
    "P/E": [get_metric("trailingPE")],
    "EPS": [get_metric("trailingEps")],
    "Debt-to-Equity": [get_metric("debtToEquity")],
    "Dividend": [get_metric("dividendRate")],
    "Total Volume": [get_metric("volume")],
    "Avg Volume": [get_metric("averageVolume")]
    })
    
    metrics_df["P/E"] = metrics_df["P/E"].map('{:.2f}'.format)
    metrics_df["EPS"] = metrics_df["EPS"].map('{:.2f}'.format)
    metrics_df["Debt-to-Equity"] = metrics_df["Debt-to-Equity"].map('{:.2f}'.format)
    metrics_df["Dividend"] = metrics_df["Dividend"].map('{:.2f}'.format)
    metrics_df["Total Volume"] = metrics_df["Total Volume"].map('{:.0f}'.format)
    metrics_df["Avg Volume"] = metrics_df["Avg Volume"].map('{:.0f}'.format)
    
    
   
   
    # Export to CSV
    financial_path = "Resources/Financials_"+ticker+".csv"
    metric_path = "Resources/Metrics_"+ticker+".csv"
    #df.to_csv("financial_path)
    metrics_df.to_csv(metric_path,index=False)
    
    return financial_path, metric_path, stock_name

