import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter
import scipy.stats as stats
#import scipy
import numpy as np

#Lets define some functions:
# Allow us to collect relevant statistical fitting parameters given the desired distribution function;
# Say, mean and std for normal gaussian function given the data of daily returns.
def GetParam(dtype,returns):
    return getattr(stats,dtype).fit(returns)  

#Utilizes fitting parameters to plot the distribution function given the range x, 
def DistFun(dtype, x, returns):
    params = GetParam(dtype,returns)
    fit = getattr(stats, dtype).pdf
    distfit = fit(x, *params)
    return distfit

def Ptest(dtype,returns):
    params = GetParam(dtype,returns)
    ks,pvalue = stats.kstest(returns, dtype, args = params)
    return ks, pvalue

#Distribution Functions to compare
dist_name = ['alpha','anglit','arcsine','beta','betaprime','bradford','burr','burr12','cauchy',
            'chi','chi2','cosine','dgamma','dweibull','erlang','expon','exponnorm','exponweib',
            'exponpow','f','fatiguelife','fisk','foldcauchy','foldnorm','frechet_r','frechet_l',
            'genlogistic','genpareto','gennorm','genexpon','genextreme','gausshyper','gamma',
            'gengamma','genhalflogistic','gilbrat','gompertz','gumbel_r','gumbel_l',
            'halfcauchy','halflogistic','halfnorm','halfgennorm','hypsecant','invgamma',
            'invgauss','invweibull','johnsonsb','johnsonsu','kstwobign','laplace','levy',
            'levy_l','logistic','loggamma','loglaplace','lognorm','lomax','maxwell','mielke',
            'nakagami','ncx2','ncf','nct','norm','pareto','pearson3','powerlaw','powerlognorm',
            'powernorm','rdist','reciprocal','rayleigh','rice','recipinvgauss','semicircular',
            't','triang','truncexpon','truncnorm','tukeylambda','uniform','wald','weibull_min',
            'weibull_max']
Ndist = 5 # Number of top most probable distributions.

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
# Note: Since Poisson is typically used for count data, this might be less meaningful
lambda_poisson = np.mean(returns)

# Plot the Histogram with Gaussian and Poisson Distributions
plt.figure(figsize=(10, 6))
sns.histplot(returns, bins=50, kde=True, stat='density', label='Daily Returns')
x = np.linspace(min(returns), max(returns), 100)
plt.plot(x, stats.norm.pdf(x, mean, std), label='Gaussian PDF', linestyle='dashed')


results = []
for dtype in dist_name:
    try:
        ks, pvalue = Ptest(dtype,returns)
        results.append([dtype,ks,pvalue])
    except:
        continue

df_results = pd.DataFrame(results, columns = ["Distribution","KS Statistic","P Value"])
df_sorted = df_results.sort_values(by = "P Value", ascending = False).head(Ndist)

for dtype in df_sorted.Distribution:
    plt.plot(x, DistFun(dtype,x,returns), label=dtype, linestyle='dotted')


plt.title('Distribution of Daily Returns for '+ticker.info["shortName"])
plt.xlabel('Daily Return')
plt.ylabel('Density')
plt.legend()
plt.gca().xaxis.set_major_formatter(PercentFormatter(1))
plt.show()




