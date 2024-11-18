import yfinance as yf
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objs as go
import plotly.express as px

import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.io as pio
import pandas as pd


# Define functions
def GetParam(dtype, returns):
    return getattr(stats, dtype).fit(returns)

def DistFun(dtype, x, returns):
    params = GetParam(dtype, returns)
    fit = getattr(stats, dtype).pdf
    distfit = fit(x, *params)
    return distfit

def Ptest(dtype, returns):
    params = GetParam(dtype, returns)
    ks, pvalue = stats.kstest(returns, dtype, args=params)
    return ks, pvalue

# Distribution Functions to compare
dist_name = ['alpha', 'anglit', 'arcsine', 'beta', 'betaprime', 'bradford', 'burr', 'burr12', 'cauchy', 
             'chi', 'chi2', 'cosine', 'dgamma', 'dweibull', 'erlang', 'expon', 'exponnorm', 'exponweib', 
             'exponpow', 'f', 'fatiguelife', 'fisk', 'foldcauchy', 'foldnorm', 'frechet_r', 'frechet_l', 
             'genlogistic', 'genpareto', 'gennorm', 'genexpon', 'genextreme', 'gausshyper', 'gamma', 
             'gengamma', 'genhalflogistic', 'gilbrat', 'gompertz', 'gumbel_r', 'gumbel_l', 'halfcauchy', 
             'halflogistic', 'halfnorm', 'halfgennorm', 'hypsecant', 'invgamma', 'invgauss', 'invweibull', 
             'johnsonsb', 'johnsonsu', 'kstwobign', 'laplace', 'levy', 'levy_l', 'logistic', 'loggamma', 
             'loglaplace', 'lognorm', 'lomax', 'maxwell', 'mielke', 'nakagami', 'ncx2', 'ncf', 'nct', 
             'norm', 'pareto', 'pearson3', 'powerlaw', 'powerlognorm', 'powernorm', 'rdist', 'reciprocal', 
             'rayleigh', 'rice', 'recipinvgauss', 'semicircular', 't', 'triang', 'truncexpon', 'truncnorm', 
             'tukeylambda', 'uniform', 'wald', 'weibull_min', 'weibull_max']

Ndist = 5  # Number of top most probable distributions.

# Calculate statistics for the Gaussian distribution
def Dist_Fitting(df_simulations, Ndist):
    final_prices = df_simulations.iloc[:, -1]
    close_price = df_simulations.iloc[0,0]
    mean = np.mean(final_prices)
    std = np.std(final_prices)
    
    # Calculate lambda for Poisson distribution
    lambda_poisson = np.mean(final_prices)
    
    # Create x values
    x = np.linspace(min(final_prices), max(final_prices), 100)
    
    # Perform distribution tests and get top N distributions
    results = []
    for dtype in dist_name:
        try:
            ks, pvalue = Ptest(dtype, final_prices)
            results.append([dtype, ks, pvalue])
        except:
            continue
    
    df_results = pd.DataFrame(results, columns=["Distribution", "KS Statistic", "P Value"])
    df_sorted = df_results.sort_values(by="P Value", ascending=False).head(Ndist)
    
    # Plot using Plotly
    fig = go.Figure()
    
    # Plot Histogram
    fig = ff.create_distplot([final_prices], ["Final Price"], bin_size=0.025*close_price, show_rug=False, show_hist=True)
    #fig.add_trace(go.Histogram(x=final_prices, nbinsx=50, histnorm='density', name='Daily Returns'))
    
    # Plot Gaussian Distribution
    fig.add_trace(go.Scatter(x=x, y=stats.norm.pdf(x, mean, std), mode='lines', name='Gaussian PDF'))
    
    # Plot top N distributions
    for dtype in df_sorted.Distribution:
        fig.add_trace(go.Scatter(x=x, y=DistFun(dtype, x, final_prices), mode='lines', name=f'{dtype} PDF'))
    
    fig.update_layout(
        title='Distribution of Final Prices',
        xaxis_title='Final Price ($)',
        xaxis=dict(showgrid=True, tickformat='$#,##0.00'),
        yaxis_title='Density',
        barmode='overlay'
    )
    
    fig.update_traces(opacity=0.75)
    fig.write_html("D:/Professional_WorkTools/Github/StockSillines/Distributions/Plot.HTML")
    fig.show()

