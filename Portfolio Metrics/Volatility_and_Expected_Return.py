# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 22:22:12 2024

@author: serw1
"""

import pandas as pd
import numpy as np
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tabulate import tabulate
from scipy.signal import find_peaks, peak_widths
import warnings
import os

# Ignore all warnings
warnings.filterwarnings("ignore")
# Current date and time




ticker = "MC.PA"
current_date = datetime.now()
end_date =  "2024-06-17"
end_dateplot = current_date + timedelta(days=365)
start_plotdate = current_date - timedelta(days=365)
T = 1 # Horizon Years
#start_date = current_date - timedelta(days=365)
start_date = "2023-01-01"
simulations = 10000 # Number of simulations
adjusted_return = 1
position_price = (165.93)
open_position_view = True
PP = 1 # Percentile graphs

def price_walk(ticker,start_date,end_date,adjusted_return,simulations,T):
    #Needed Output, price_paths_df, annual_volatility, name
    
    # Fetch historical data for a stock/ticker, e.g., Apple (AAPL)
    info = yf.Ticker(ticker).info
    name = name = info["longName"]
    stock_data = yf.download(ticker, start=start_date, end=end_date,progress=False)
    stock_data['Daily Return'] = stock_data['Adj Close'].pct_change()
    # Standard deviation of daily returns, mu
    volatility = stock_data['Daily Return'].std()
    # Annualize the volatility (assuming 252 trading days in a year), sigma
    annual_volatility = volatility * np.sqrt(252)
    #print(f"Annualized Volatility: {annual_volatility}")
    
    # Parameters
    S0 = stock_data['Adj Close'][-1]  # Last closing price
    #T = simulations  # Time horizon in years
    dt = 1/252  # Daily steps
    N = int(T / dt)  # Number of steps
    mu = stock_data['Daily Return'].mean() * 252 * adjusted_return  # Annualized mean return
    sigma = annual_volatility*adjusted_return  # Annualized volatility
    # Generate random daily returns
    daily_returns = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.randn(N))
    # Initialize an array to store the price paths
    price_paths = np.zeros((N, simulations))
    for i in range(simulations):
        # Generate random daily returns
        daily_returns = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.randn(N))
    
        # Simulate stock price path
        price_paths[0, i] = S0
        for t in range(1, N):
            price_paths[t, i] = price_paths[t-1, i] * daily_returns[t-1]
            
    # Convert the price paths to a DataFrame with adjusted date time for easier plotting
    start = max(stock_data.index) #simulation date
    price_paths_df = pd.DataFrame(price_paths)
    date_range = pd.date_range(start=start, periods=N, freq='B')  # 'B' frequency
    # Set the date range as the index
    price_paths_df.index = date_range

    return price_paths_df,annual_volatility,name

def weightprice_walk(ticker,start_date,end_date,adjusted_return,simulations,T):
    #Needed Output, price_paths_df, annual_volatility, name
    
    # Fetch historical data for a stock/ticker, e.g., Apple (AAPL)
    info = yf.Ticker(ticker).info
    name = name = info["longName"]
    stock_data = yf.download(ticker, start=start_date, end=end_date,progress=False)
    stock_data['Daily Return'] = stock_data['Adj Close'].pct_change()
    stock_data["Weighted Return"] = stock_data['Daily Return']*stock_data["Volume"]
    stock_data["Sqrt Weighted Return"] = (stock_data['Daily Return']**2)*stock_data["Volume"]
    # Calculate the sum of weighted returns and total volume for each day
    weighted_sum = stock_data['Weighted Return'].sum()
    sqrt_weighted_sum = stock_data['Sqrt Weighted Return'].sum()
    total_volume = stock_data['Volume'].sum()
    avg_volume = total_volume / len(stock_data)
    # Calculate the volume-weighted average return
    avg_Wdaily = weighted_sum / total_volume
    # Calculate the standard deviation of the volume-weighted daily returns
    weighted_volatility = stock_data['Weighted Return'].std()
    # Annualize the weighted volatility (assuming 252 trading days in a year)
    annual_volatility = np.sqrt(sqrt_weighted_sum / total_volume * 252)
    #print(f"Annual Weighted Volatility: {annual_volatility}")
    
    # Parameters
    S0 = stock_data['Adj Close'][-1]  # Last closing price
    #T = simulations  # Time horizon in years
    dt = 1/252  # Daily steps
    N = int(T / dt)  # Number of steps
    mu = weighted_sum / total_volume * 252 * adjusted_return  # Annualized mean return
    sigma = (annual_volatility)*adjusted_return  # Annualized volatility
    # Generate random daily returns
    daily_returns = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.randn(N))
    # Initialize an array to store the price paths
    price_paths = np.zeros((N, simulations))
    for i in range(simulations):
        # Generate random daily returns
        daily_returns = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.randn(N))
    
        # Simulate stock price path
        price_paths[0, i] = S0
        for t in range(1, N):
            price_paths[t, i] = price_paths[t-1, i] * daily_returns[t-1]
            
    # Convert the price paths to a DataFrame with adjusted date time for easier plotting
    start = max(stock_data.index) #simulation date
    price_paths_df = pd.DataFrame(price_paths)
    date_range = pd.date_range(start=start, periods=N, freq='B')  # 'B' frequency
    # Set the date range as the index
    price_paths_df.index = date_range

    return price_paths_df,annual_volatility,name

def Weekly_Volatility(ticker,start_date,end_date):
    # Fetch historical data for a stock (e.g., Apple)
    stock_data = yf.download(ticker, start=start_date, end=end_date, interval = "1wk")
    # Resample to weekly data and calculate weekly returns
    stock_data['Weekly Return'] = stock_data['Adj Close'].pct_change()
    # Calculate weekly volatility (standard deviation of weekly returns)
    stock_data['Weekly Volatility'] = stock_data['Weekly Return'].rolling(window=5).std() * np.sqrt(5)

    # Calculate mean and median weekly returns
    stock_data['Mean Weekly Return'] = stock_data['Weekly Return'].rolling(window=5).mean() * 5
    stock_data['Median Weekly Return'] = stock_data['Weekly Return'].rolling(window=5).median() * 5

    # Plot the weekly volatility, mean return, and median return
    plt.figure(figsize=(10, 6),dpi=300)
    plt.plot(stock_data.index, stock_data['Weekly Volatility'], label='Weekly Volatility')
    plt.plot(stock_data.index, stock_data['Mean Weekly Return'], label='Mean Weekly Return')
    plt.plot(stock_data.index, stock_data['Median Weekly Return'], label='Median Weekly Return')

    plt.title('Weekly Volatility, Mean Return, and Median Return of AAPL')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.show()
    

def GBM_Simulation(ticker,start_date,end_date,start_plotdate,end_dateplot,simulations,adjusted_return,position_price,T,open_position_view,PP):
    
    if not os.path.exists("Resources"):
        os.makedirs("Resources")
    
    if open_position_view == "Both":
        price_paths_df,annual_volatility,name = price_walk(ticker,start_date,end_date,adjusted_return,simulations,T)
        wprice_paths_df,annual_Wvolatility,_ = weightprice_walk(ticker, start_date, end_date, adjusted_return, simulations, T)
        price_paths_df2,annual_volatility,_= price_walk(ticker,start_date,end_dateplot,adjusted_return,simulations,T)
        wprice_paths_df2,annual_Wvolatility2,_ = weightprice_walk(ticker, start_date, end_dateplot, adjusted_return, simulations, T)
    elif open_position_view == True:
        price_paths_df,annual_volatility,name = price_walk(ticker,start_date,end_date,adjusted_return,simulations,T)
        wprice_paths_df,annual_Wvolatility2,_ = weightprice_walk(ticker, start_date, end_date, adjusted_return, simulations, T)
        price_paths_df2 = price_paths_df
    else:
        price_paths_df,annual_volatility,name = price_walk(ticker,start_date,end_dateplot,adjusted_return,simulations,T)
        wprice_paths_df,annual_Wvolatility2,_ = weightprice_walk(ticker, start_date, end_date, adjusted_return, simulations, T)
        price_paths_df2 = price_paths_df    
    
    
    # Plot multiple percentiles
    percentiles = [5,50,95]
    colors = ["red","yellow","green"]
    plt.figure(figsize=(10, 6),dpi=150)
    #Plot Historical Prices
    final_price = price_paths_df.loc[max(price_paths_df.index)]
    
    for p,color in zip(percentiles,colors):
        #percentil_path = price_paths_df.quantile(p/100, axis=1)
        #plt.plot(percentil_path, label=str(p)+'th Percentile', color = color)
        
        # Find and plot path examples
        quantile_price= final_price.quantile(p/100)
        final_price = final_price.sort_values(ascending = False)
        price_location = final_price[final_price < quantile_price].index
        for path in price_location[0:PP]:
            plt.plot(price_paths_df[path], color = color, linestyle=":",alpha = np.sqrt(PP)/PP)
        
    for quintile in [5,20,40,47.5]:
        percentile_path1 = price_paths_df.quantile(quintile/100, axis = 1)
        percentile_path2 = price_paths_df.quantile((100-quintile)/100, axis = 1)
        plt.fill_between(percentile_path1.index, percentile_path1,percentile_path2, alpha = 0.2, color = "gray", label = str(quintile)+"th Percentil")

    
    
    
    #Plot open position price
    plt.axhline(y=position_price, color = "y",linestyle="--", label = "Open Position")
    
    #GBM Price walk
    daily_mean_prices = price_paths_df.median(axis=1) # Daily Average Simulated price
    plt.plot(daily_mean_prices, label = "Median Simulated Price", color = "Green",linestyle = "--")
    
    daily_mean_prices = wprice_paths_df.median(axis=1) # Daily Average Simulated price
    plt.plot(daily_mean_prices, color = "Green",linestyle = ":", label = str((100*annual_Wvolatility2).round(2))+"% VWAP")
    #final_price2 = wprice_paths_df.loc[max(wprice_paths_df.index)]
    
    

     
    if (open_position_view=="Both"):
        daily_mean_prices = price_paths_df2.mean(axis=1) # Daily Average Simulated price
        plt.plot(daily_mean_prices, color = "Green",linestyle = "--")
        #final_price = price_paths_df2.loc[max(price_paths_df2.index)]
        
        for quintile in [5,20,40,45]:
            percentile_path1 = price_paths_df2.quantile(quintile/100, axis = 1)
            percentile_path2 = price_paths_df2.quantile((100-quintile)/100, axis = 1)
            plt.fill_between(percentile_path1.index, percentile_path1,percentile_path2, alpha = 0.1, color = "gray")
        
        daily_mean_prices = wprice_paths_df2.mean(axis=1) # Daily Average Simulated price
        plt.plot(daily_mean_prices, color = "c",linestyle = ":", label = str((100*annual_Wvolatility).round(2))+"% VWAP")
        #final_price2 = wprice_paths_df.loc[max(wprice_paths_df.index)]    
        
        #for quintile in [5,20,40,47.5]:
        #    percentile_path01 = wprice_paths_df.quantile(quintile/100, axis = 1)
        #    percentile_path02 = price_paths_df.quantile((100-quintile)/100, axis = 1)
        #    plt.fill_between(percentile_path01.index, percentile_path01,percentile_path02, alpha = 0.05, color = "c")
        
        #for quintile in [5,20,40,47.5]:
        #    percentile_path1 = price_paths_df.quantile(quintile/100, axis = 1)
        #    percentile_path2 = price_paths_df.quantile((100-quintile)/100, axis = 1)
        #    plt.fill_between(percentile_path1.index, percentile_path1,percentile_path2, alpha = 0.2, color = "gray", label = str(quintile)+"th Percentil")
        
        #for p,color in zip(percentiles,colors):
        #    percentil_path = price_paths_df2.quantile(p/100, axis=1)
        #    plt.plot(percentil_path, color = color)
            
            
            
            #quantile_price= final_price.quantile(p/100)
            #price_location = max(final_price[final_price < quantile_price])
            #path = final_price[final_price == price_location].index
            #plt.plot(price_paths_df[path], color = color, linestyle=":")
    
    #Plot historical prices    
    plot_stock_data = yf.download(ticker, start=start_plotdate, end=end_dateplot,progress=False)
    plt.plot(plot_stock_data["Adj Close"], label = "Adjusted Close Price") # Plot Historical price
    close_price = plot_stock_data["Adj Close"].loc[max(plot_stock_data.index)]
    
    plt.title(name+' GBM Price Evolution - Annualized Volatility: '+str((100*annual_volatility).round(2))+"%")
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.legend(loc = "upper left")   
    projection_path = "Resources/"+name+"_projection_T="+str(T)+".png"
    plt.savefig(projection_path)
    plt.show()
    plt.close()
    
    # Plot the distribution of final prices
    final_price = price_paths_df2.loc[max(price_paths_df2.index)]
    plt.figure(figsize=(10, 6),dpi=150)
    plt.hist(final_price, bins=100, edgecolor='black')
    plt.axvline(x=position_price, color='yellow', linestyle='--', linewidth=2, label=str(round(position_price,2))+" - Open Posotion")
    plt.axvline(x=final_price.mean(), color='b', linestyle='--', linewidth=2, label=str(round(final_price.mean(),2))+" - Mean Price")
    plt.axvline(x=final_price.median(), color='c', linestyle='--', linewidth=2, label=str(round(final_price.median(),2))+" - Median Price")
    plt.axvline(x=close_price, color='r', linestyle='--', linewidth=2, label=str(round(close_price,2))+" - Close Price")
    plt.title('Distribution of Simulated Final Stock Prices')
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    plt.legend()
    distribution_path = "Resources/"+name+"_distribution_T="+str(T)+".png"
    plt.savefig(distribution_path)
    plt.show()
    
    #Weekly_Volatility(ticker, start_date, end_date)
    
    #Expected Returns
    percentiles = [5,25,45,50,65,75,95]
    print(name+"; Open position: "+str(position_price)+" with "+str(int(T*365))+" Days Maturity")
    data = {
            "Price Description":[str(p)+"th percentile" for p in percentiles],
            "Forward Price":[final_price.quantile(p/100).round(2) for p in percentiles]
            }
    df_profit = pd.DataFrame(data)
    df_profit["Profit Margin (%)"] = 100*(df_profit["Forward Price"]-position_price)/df_profit["Forward Price"]
    df_profit["Profit Margin (%)"] = df_profit["Profit Margin (%)"].round(2)
    
    #Obtain HWHM prices
    print(tabulate(df_profit, headers='keys', tablefmt='pretty'))
    maturity_path = "Resources/"+name+"_maturity_T="+str(T)+".csv"
    df_profit.to_csv(maturity_path, index = False)
    
    
    
 
    """
    # Melt the DataFrame to long format for seaborn
    price_paths_long = price_paths_df.reset_index().melt(id_vars='index', var_name='Simulation', value_name='Price')
    price_paths_long.rename(columns={'index': 'Date'}, inplace=True)
    
    # Plot the distribution of stock prices over time
    plt.figure(figsize=(12, 8))
    sns.kdeplot(data=price_paths_long, x='Date', y='Price', fill=True, cmap='viridis')
    sns.lineplot(data = stock_data, x = "Date", y="Adj Close")
    plt.title('Density Plot of Simulated Stock Price Distributions Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()
    """
    
    return projection_path, distribution_path, maturity_path


#tickers = ["AMAT","GOOGL",'QCOM',"NVDA","TSM","KMB","AAPL","MSFT","MO","MA","NEE","PEP","V"]
#open_prices = [244.47,190.71,188.12,131.38,189.11,147.67,225.34,432.57,51.24,455.40,77.53,165.93,260.8]

#for ticker,position_price in zip(["AAPL"],[225.34222]):
#    GBM_Simulation(ticker,start_date,"2024-07-3",start_plotdate,end_dateplot,100000,adjusted_return,(225.34222)/1,60/365,False,0)




