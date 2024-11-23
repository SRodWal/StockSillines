import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import yfinance as yf
import tkinter as tk

# Custom Modules
def Selector(lst):
    def on_select():
        nonlocal selected_items, risk_aversion
        selected_items = [lst[i] for i in lb.curselection()]
        risk_aversion = slider.get() / 100  # Convert to a value between 0 and 1
        root.destroy()
    
    selected_items = []
    risk_aversion = 0.5  # Default value
    
    root = tk.Tk()
    root.title("Multi-Select List")
    root.geometry("400x400")

    lb = tk.Listbox(root, selectmode=tk.MULTIPLE)
    for item in lst:
        lb.insert(tk.END, item)
    lb.pack(padx=10, pady=10)

    slider_label = tk.Label(root, text="Risk Aversion (0: Max Returns, 100: Min Risk):")
    slider_label.pack(pady=10)

    slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
    slider.pack(pady=10)

    select_button = tk.Button(root, text="Select", command=on_select)
    select_button.pack(pady=10)

    root.mainloop()
    
    return selected_items, risk_aversion

# Read data from Excel
f_dir = r"D:/Professional_WorkTools/Github/StockSillines/Open Positions.xlsx"
portfolio_df = pd.read_excel(f_dir)
portfolio_df = portfolio_df[["Chapter", "Ticker", "Volume", "Price", "Expected Return QoQ%", "Volatility", "Value"]]
Selected_Chapters, risk_aversion = Selector(list(set(portfolio_df.Chapter)))
df = portfolio_df.loc[portfolio_df.Chapter.isin(Selected_Chapters)].drop("Chapter", axis=1)


# Extract necessary data
tickers = df['Ticker'].values
expected_returns = df['Expected Return QoQ%'].values
volatilities = df['Volatility'].values
weights = df['Value'].values / df['Value'].sum()  # Normalize initial weights

# Measure correlation
start = '2023-01-01'
end = '2024-12-31'

def CorMatrix(df, start_date, end_date):
    tickers = list(df["Ticker"])
    info = yf.download(tickers, start=start_date, end=end_date)['Close']
    # Calculate daily returns
    returns = info.pct_change().dropna()
    # Calculate the correlation matrix
    correlation_matrix = returns.corr()
    return correlation_matrix

correlation_matrix = CorMatrix(df, start, end)

# Covariance matrix
cov_matrix = np.outer(volatilities, volatilities) * correlation_matrix

# Objective Function to minimize: Risk-Adjusted Portfolio Variance
def objective_function(weights, cov_matrix, expected_returns, risk_aversion):
    # Minimize (risk_aversion * variance - (1 - risk_aversion) * returns)
    portfolio_variance = weights.T @ cov_matrix @ weights
    portfolio_return = np.sum(weights * expected_returns)
    return risk_aversion * portfolio_variance - (1 - risk_aversion) * portfolio_return

# Constraints: sum(weights) = 1
constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

# Boundaries: weights should be between 0 and 1
bounds = tuple((0, 1) for asset in range(len(tickers)))

# Compute the efficient frontier
risk_aversions = np.linspace(0, 1, 200)  # 50 points from 0 to 1
frontier_returns = []
frontier_volatilities = []

for risk_aversion in risk_aversions:
    opt_results = minimize(objective_function, weights, args=(cov_matrix, expected_returns, risk_aversion), method='SLSQP', bounds=bounds, constraints=constraints)
    optimal_weights = opt_results.x
    portfolio_return = np.sum(optimal_weights * expected_returns)
    portfolio_volatility = np.sqrt(optimal_weights.T @ cov_matrix @ optimal_weights)
    frontier_returns.append(portfolio_return)
    frontier_volatilities.append(portfolio_volatility)

# Plot the efficient frontier
plt.figure(figsize=(10, 6))
plt.plot(frontier_volatilities, frontier_returns, label='Efficient Frontier')
plt.scatter(volatilities, expected_returns, c='red', marker='o', label='Individual Assets')

for i, txt in enumerate(tickers):
    plt.annotate(txt, (volatilities[i], expected_returns[i]))

plt.title('Efficient Frontier')
plt.xlabel('Volatility (Risk)')
plt.ylabel('Expected Return')
plt.legend()
plt.grid(True)
plt.show()
