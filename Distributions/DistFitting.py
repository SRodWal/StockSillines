import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter
import scipy.stats as stats
#import scipy
import numpy as np

# Download Historical Data
ticker = yf.Ticker("USDMXN=X")
data = ticker.history(period="1d", start="2023-01-01", end="2024-11-10")

# Calculate Daily Returns
data['Daily_Return'] = data['Close'].pct_change().dropna()
returns = data['Daily_Return'].dropna()

# Calculate statistics for the Gaussian distribution
mean = np.mean(returns)
std = np.std(returns)

# Calculate lambda for Poisson distribution
# Note: Since Poisson is typically used for count data, this might be less meaningful
lambda_poisson = np.mean(returns)

# Perform KS Test for Gaussian (Normal) Distribution
ks_stat_normal, p_value_normal = stats.kstest(returns, 'norm', args=(mean, std))
# Perform KS Test for Poisson Distribution
ks_stat_poisson, p_value_poisson = stats.kstest(returns, 'poisson', args=(lambda_poisson,))

print(f"KS Statistic (Gaussian): {ks_stat_normal}, P-Value: {p_value_normal}")
print(f"KS Statistic (Poisson): {ks_stat_poisson}, P-Value: {p_value_poisson}")

# Plot the Histogram with Gaussian and Poisson Distributions
plt.figure(figsize=(10, 6))
sns.histplot(returns, bins=50, kde=True, stat='density', label='Daily Returns')
x = np.linspace(min(returns), max(returns), 100)
plt.plot(x, stats.norm.pdf(x, mean, std), label='Gaussian PDF', linestyle='dashed')
plt.plot(x, stats.poisson.pmf(np.round(x), lambda_poisson), label='Poisson PMF', linestyle='dotted')
plt.title('Distribution of Daily Returns for USDMXN=X')
plt.xlabel('Daily Return')
plt.ylabel('Density')
plt.legend()
plt.gca().xaxis.set_major_formatter(PercentFormatter(1))
plt.show()


#Distribution Functions to compare
disttype = ['alpha','anglit','arcsine','beta','betaprime','bradford','burr','burr12','cauchy','chi','chi2','cosine','dgamma','dweibull','erlang','expon','exponnorm','exponweib','exponpow','f','fatiguelife','fisk','foldcauchy','foldnorm','frechet_r','frechet_l','genlogistic','genpareto','gennorm','genexpon','genextreme','gausshyper','gamma','gengamma','genhalflogistic','gilbrat','gompertz','gumbel_r','gumbel_l','halfcauchy','halflogistic','halfnorm','halfgennorm','hypsecant','invgamma','invgauss','invweibull','johnsonsb','johnsonsu','kstwobign','laplace','levy','levy_l','logistic','loggamma','loglaplace','lognorm','lomax','maxwell','mielke','nakagami','ncx2','ncf','nct','norm','pareto','pearson3','powerlaw','powerlognorm','powernorm','rdist','reciprocal','rayleigh','rice','recipinvgauss','semicircular','t','triang','truncexpon','truncnorm','tukeylambda','uniform','wald','weibull_min','weibull_max']
Ndist = 5 # Number of top most probable distributions.
legend = disttype+["Data-Hist"]

# Esta funcion crea las distribuciones con los parametros y tipo de distribucion de entrada
# DistributionFit = probadensityfun( distribution type - string, linespace - list, parameters - list )
def probadensityfun(dtype,x,stats):
    fit = getattr(stats,dtype).pdf
    if len(stats)==2:
        distfit = fit(x, stats[0], stats[1])
    if len(stats)==3:    
        distfit = fit(x, stats[0], stats[1], stats[2])
    if len(stats)==4:
        distfit = fit(x, stats[0], stats[1], stats[2], stats[3])
    if len(stats)==5:
        distfit = fit(x, stats[0], stats[1], stats[2], stats[3], stats[4])
    if len(stats)==6:
        distfit = fit(x, stats[0], stats[1], stats[2], stats[3], stats[4],stats[5])
    return distfit 


