import yfinance as yf
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objs as go
import plotly.express as px

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

# Download Historical Data
ticker = yf.Ticker("MO")
data = ticker.history(period="1d", start="2024-01-01", end="2024-11-10")

# Calculate Daily Returns
data['Daily_Return'] = data['Close'].pct_change().dropna()
returns = data['Daily_Return'].dropna()

# Calculate statistics for the Gaussian distribution
mean = np.mean(returns)
std = np.std(returns)

# Calculate lambda for Poisson distribution
lambda_poisson = np.mean(returns)

# Create x values
x = np.linspace(min(returns), max(returns), 100)

# Perform distribution tests and get top N distributions
results = []
for dtype in dist_name:
    try:
        ks, pvalue = Ptest(dtype, returns)
        results.append([dtype, ks, pvalue])
    except:
        continue

df_results = pd.DataFrame(results, columns=["Distribution", "KS Statistic", "P Value"])
df_sorted = df_results.sort_values(by="P Value", ascending=False).head(Ndist)

# Plot using Plotly
fig = go.Figure()

# Plot Histogram
fig.add_trace(go.Histogram(x=returns, nbinsx=50, histnorm='density', name='Daily Returns'))

# Plot Gaussian Distribution
fig.add_trace(go.Scatter(x=x, y=stats.norm.pdf(x, mean, std), mode='lines', name='Gaussian PDF'))

# Plot top N distributions
for dtype in df_sorted.Distribution:
    fig.add_trace(go.Scatter(x=x, y=DistFun(dtype, x, returns), mode='lines', name=f'{dtype} PDF'))

fig.update_layout(
    title='Distribution of Daily Returns for ' + ticker.info["shortName"],
    xaxis_title='Daily Return',
    yaxis_title='Density',
    barmode='overlay'
)

fig.update_traces(opacity=0.75)
fig.write_html("D:/Professional_WorkTools/Github/StockSillines/Distributions/Plot")
fig.show()

