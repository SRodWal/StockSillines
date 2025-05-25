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
    return mean, median, std, skewness, kurtosis, var_95, var_75, var_25, cvar_95, iqr

def price_probability(df_simulations, price_target, tolerance):
    # Calculate probability within the specified range
    lower_bound = price_target - tolerance
    upper_bound = price_target + tolerance
    within_range = df_simulations.apply(lambda x: ((x >= lower_bound) & (x <= upper_bound)).mean(), axis=0)
    above_range = df_simulations.apply(lambda x: ((x >= price_target)).mean(), axis=0)
    below_range = df_simulations.apply(lambda x: ((x <= price_target)).mean(), axis=0)

    # Create a single DataFrame to join the three ranges
    probability_df = pd.DataFrame({
        'Within Range': within_range,
        'Above Target': above_range,
        'Below Target': below_range
    })

    return probability_df

# Distribution Functions to compare
dist_name = [
    'lognorm', 'norm', 'gamma', 'weibull_min', 'weibull_max', 'genpareto', 'cauchy', 
    'beta', 't', 'expon', 'gumbel_r', 'gumbel_l', 'logistic', 'pareto', 'nct', 'johnsonsu'
]

Ndist = 3  # Number of top most probable distributions.

def Dist_Fitting(df_simulations, Ndist, Name):
    final_prices = df_simulations.iloc[:, -1]
    close_price = df_simulations.iloc[0, 0]
    mean = final_prices.mean()
    std = final_prices.std()
    
    # Create x values
    x = np.linspace(min(final_prices), max(final_prices), 100)
    dx = (max(final_prices) - min(final_prices))/1000
    
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
    df_sorted = pd.concat([df_sorted, df_results.loc[df_results.Distribution.isin(["cauchy","gaussian","weibull_min","f"])]], ignore_index=True)
    
    # Plot using Plotly
    fig = go.Figure()
    
    # Plot Histogram
    fig = ff.create_distplot([final_prices], ["Final Price"], bin_size=0.01 * close_price, show_rug=False, show_hist=True)
    
    # Find max density for y-axis limit
    max_density = max([trace['y'].max() for trace in fig.data if trace['type'] == 'scatter'])
    y_max = 1.2 * max_density
    
    # Plot top N distributions with statistics
    table_header = dict(
        values=[
            '<b>Distribution</b>', '<b>P Value</b>', '<b>Mean</b>', '<b>Median</b>', 
            '<b>Std Dev</b>', '<b>Skewness</b>', '<b>Kurtosis</b>','<b>VaR 95%</b>', 
            '<b>VaR 75%</b>', '<b>VaR 25%</b>', '<b>CVaR 95%</b>', '<b>IQR</b>'
        ],
        fill_color='paleturquoise',
        align='left'
    )
    
    table_cells = {
        'values': [[], [], [], [], [], [], [], [], [], [], [], []],
        'fill_color': 'lavender',
        'align': 'left'
    }
    
    for _, row in df_sorted.iterrows():
        dtype = row["Distribution"]
        pvalue = row["P Value"]
        stats_result = GetStatistics(dtype, final_prices, params_cache)
        fig.add_trace(go.Scatter(
            x=x, y=DistFun(dtype, x, final_prices, params_cache),
            mode='lines', name=f'{dtype} PDF P: {pvalue:.2%}')
        )
        
        # Add statistics to table
        table_cells['values'][0].append(dtype)
        table_cells['values'][1].append(f'{pvalue:.2%}')
        for i, value in enumerate(stats_result):
            table_cells['values'][i+2].append(f'{value:.2f}')
    
    # Add the table to the figure
    table = go.Table(header=table_header, cells=table_cells, domain=dict(x=[0, 1], y=[0, 0.28]))
    fig.add_trace(table)
    
    fig.update_layout(
        title='Distribution of Final Prices ' + Name,
        xaxis_title='Final Price ($)',
        xaxis=dict(showgrid=True, tickformat='$.2f'),
        yaxis_title='Density',
        yaxis=dict(range=[-1*y_max/2.2, 1.2*y_max], tickformat=".2f"),
        barmode='overlay',
        autosize=False,
        width=1000,
        height=600  # Increased height to accommodate the table
    )

    # Return the figure
    return fig

def plot_probability_evolution(df_simulations, price_target, tolerance):
    probability_df = price_probability(df_simulations, price_target, tolerance)
    
    # Create a 2D bar graph with a 3D perspective
    fig = go.Figure(data=[
        go.Bar(
            x=probability_df.index,
            y=probability_df['Within Range'],
            name='Within Range',
            marker_color='rgb(55, 83, 109)',
            marker_line_color='rgb(8, 48, 107)',
            marker_line_width=1.5,
            opacity=0.6
        ),
        go.Bar(
            x=probability_df.index,
            y=probability_df['Above Target'],
            name='Above Target',
            marker_color='rgb(26, 118, 255)',
            marker_line_color='rgb(8, 48, 107)',
            marker_line_width=1.5,
            opacity=0.6
        ),
        go.Bar(
            x=probability_df.index,
            y=probability_df['Below Target'],
            name='Below Target',
            marker_color='rgb(50, 171, 96)',
            marker_line_color='rgb(8, 48, 107)',
            marker_line_width=1.5,
            opacity=0.6
        )
    ])
    
    # Create layout
    layout = go.Layout(
        title=f'Probability Evolution for Target Price: {price_target}',
        barmode='group',
        xaxis=dict(title='Time'),
        yaxis=dict(title='Probability', tickformat=".2%"),
        autosize=False,
        width=800,
        height=500, 
        scene=dict(
            aspectmode='manual',
            aspectratio=dict(x=2, y=1, z=0.5)
        ),
        hovermode='closest'
    )
    
    # Add layout to figure
    fig.update_layout(layout)
    
    # Show the figure
    #fig.show()
    return fig

# Example usage
# Assuming df_simulations is already defined
# Name = "Altria - MO"
"""
fig_dist = Dist_Fitting(df_simulations, Ndist, "Dummy")


pio.write_html(fig_dist, file='final_prices_histogram.html', auto_open=True)

fig_evo = plot_probability_evolution(df_simulations, price_target=20.17, tolerance=0.01)
pio.write_html(fig_evo, file='Price Evolution.html', auto_open=True)
"""
