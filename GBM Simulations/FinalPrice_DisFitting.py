import yfinance as yf
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.io as pio
from concurrent.futures import ThreadPoolExecutor

# Define functions
def GetParam(dtype, returns):
    return getattr(stats, dtype).fit(returns)

def DistFun(dtype, x, returns, params_cache):
    if dtype not in params_cache:
        params_cache[dtype] = GetParam(dtype, returns)
    fit = getattr(stats, dtype).pdf
    return fit(x, *params_cache[dtype])

def Ptest(dtype, returns, params_cache):
    if dtype not in params_cache:
        params_cache[dtype] = GetParam(dtype, returns)
    ks, pvalue = stats.kstest(returns, dtype, args=params_cache[dtype])
    return ks, pvalue

def GetStatistics(dtype, returns, params_cache):
    if dtype not in params_cache:
        params_cache[dtype] = GetParam(dtype, returns)
    fit_data = getattr(stats, dtype).rvs(*params_cache[dtype], size=1000)
    mean = np.mean(fit_data)
    median = np.median(fit_data)
    std = np.std(fit_data)
    skewness = stats.skew(fit_data)
    kurtosis = stats.kurtosis(fit_data)
    var_95 = np.percentile(fit_data, 5)
    var_75 = np.percentile(fit_data,25)
    var_25 = np.percentile(fit_data,75)
    cvar_95 = fit_data[fit_data <= var_95].mean()
    iqr = np.percentile(fit_data, 75) - np.percentile(fit_data, 25)
    return mean, median,var_95,var_75,var_25, std, skewness, kurtosis, cvar_95, iqr

# Distribution Functions to compare
dist_name = [
    'lognorm', 'norm', 'gamma', 'weibull_min', 'weibull_max', 'genpareto', 'cauchy', 
    'beta', 't', 'expon', 'gumbel_r', 'gumbel_l', 'logistic', 'pareto', 'nct', 'johnsonsu'
]


Ndist = 3  # Number of top most probable distributions.

# Calculate statistics for the Gaussian distribution
def Dist_Fitting(df_simulations, Ndist,Name):
    final_prices = df_simulations.iloc[:, -1]
    close_price = df_simulations.iloc[0, 0]
    mean = final_prices.mean()
    std = final_prices.std()
    
    # Create x values
    x = np.linspace(min(final_prices), max(final_prices), 100)
    
    # Perform distribution tests and get top N distributions
    results = []
    params_cache = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(Ptest, dtype, final_prices, params_cache): dtype for dtype in dist_name}
        for future in futures:
            dtype = futures[future]
            try:
                ks, pvalue = future.result()
                results.append([dtype, ks, pvalue])
            except Exception as e:
                print(f"Error processing distribution {dtype}: {e}")
    
    df_results = pd.DataFrame(results, columns=["Distribution", "KS Statistic", "P Value"])
    df_sorted = df_results.sort_values(by="P Value", ascending=False).head(Ndist)
    df_sorted = pd.concat([df_sorted,df_results.loc[df_results.Distribution.isin(["cauchy","gaussian","weibull_min","f"])]],ignore_index=True)
    
    
    # Plot using Plotly
    fig = go.Figure()
    
    
    
    # Plot Histogram
    fig = ff.create_distplot([final_prices], ["Final Price"], bin_size=0.025 * close_price, show_rug=False, show_hist=True)
    #Find max density for to define y-axis
    max_density = max([trace['y'].max() for trace in fig.data if trace['type'] == 'scatter'])
    y_max = 1.2 * max_density
    
    # Plot top N distributions with statistics
    table_header = dict(values=['<b>Distribution</b>', '<b>P Value</b>', '<b>Mean</b>', '<b>Median</b>', '<b>VaR 95%</b>', '<b>VaR 75%</b>', '<b>VaR 25%</b>', '<b>Std Dev</b>', '<b>Skewness</b>', '<b>Kurtosis</b>', '<b>CVaR 95%</b>', '<b>IQR</b>'],
                        fill_color='paleturquoise',
                        align='left')
    
    table_cells = {'values': [[], [], [], [], [], [], [], [], [], [], [], []],
                   'fill_color': 'lavender',
                   'align': 'left'}
    
    for _, row in df_sorted.iterrows():
        dtype = row["Distribution"]
        pvalue = row["P Value"]
        stats_result = GetStatistics(dtype, final_prices, params_cache)
        fig.add_trace(go.Scatter(x=x, y=DistFun(dtype, x, final_prices, params_cache), mode='lines', name=f'{dtype} PDF P: {pvalue:.2%}'))
        
        # Add statistics to table
        table_cells['values'][0].append(dtype)
        table_cells['values'][1].append(f'{pvalue:.2%}')
        for i, value in enumerate(stats_result):
            table_cells['values'][i+2].append(f'{value:.2f}')
    
    # Add the table to the figure
    table = go.Table(header=table_header, cells=table_cells, domain=dict(x=[0, 1], y=[0, 0.28]))
    
    fig.add_trace(table)
    
    fig.update_layout(
        title='Distribution of Final Prices '+Name,
        xaxis_title='Final Price ($)',
        xaxis=dict(showgrid=True, tickformat='$#,##0.00'),
        yaxis_title='Density',
        yaxis = dict(range = [-1*y_max/2.2, 1.2*y_max], tickformat = "0.00%"),
        barmode='overlay',
        autosize=False,
        width=1200,
        height=800  # Increased height to accommodate the table
    )
    
    #fig.update_traces(opacity=0.75)
    fig.write_html("final_prices_histogram.html")
    fig.show()
    return fig

# Example usage
# Assuming df_simulations is already defined
#Name = "Altria - MO"
#Dist_Fitting(df_simulations, Ndist, Name)
