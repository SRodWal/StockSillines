import pandas as pd
import numpy as np
from math import sqrt
import datetime as dt
import seaborn as sb
import matplotlib.pyplot as plt
import scipy, warnings

import yfinance as yf

warnings.filterwarnings("ignore")

def probadensityfun(dtype,x,stats):
    fit = getattr(scipy.stats,dtype).pdf
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

Cols = ["Historical"," 52 Weeks", "6 Months", "13 Weeks","2 Months"]
disttype = ['alpha','anglit','arcsine','beta','betaprime','bradford','burr','burr12','cauchy','chi','chi2',
            'cosine','dgamma','dweibull','erlang','expon','exponnorm','exponweib','exponpow','f','fatiguelife',
            'fisk','foldcauchy','foldnorm','frechet_r','frechet_l','genlogistic','genpareto','gennorm','genexpon',
            'genextreme','gausshyper','gamma','gengamma','genhalflogistic','gilbrat','gompertz','gumbel_r','gumbel_l',
            'halfcauchy','halflogistic','halfnorm','halfgennorm','hypsecant','invgamma','invgauss','invweibull',
            'johnsonsb','johnsonsu','kstwobign','laplace','levy','levy_l','logistic','loggamma','loglaplace','lognorm',
            'lomax','maxwell','mielke','nakagami','ncx2','ncf','nct','norm','pareto','pearson3','powerlaw','powerlognorm',
            'powernorm','rdist','reciprocal','rayleigh','rice','recipinvgauss','semicircular','t','triang','truncexpon',
            'truncnorm','tukeylambda','uniform','wald','weibull_min','weibull_max']
df = yf.Ticker("BA.MX").history( period = "max")
removecols = ["Dividends","Stock Splits","Volume"]
df.drop(removecols, axis = 1, inplace = True)
print(df)

# Dates ranges
Numweek = [52,26,13,8]
tnow = dt.datetime.now()
today = tnow.strftime("%Y-%m-%d") 
lastd = [df.index[0]]
for wks in Numweek:
    lastd.append((tnow-dt.timedelta(days = wks*7)).strftime("%Y-%m-%d"))
# DataFrame to matrix
#Measure %change: historical changes ,52 weeks, 6months (26 weeks), 2 months (4 weeks) 
changelist = []
plt.figure(figsize = (6,6), dpi = 350)
for firstd in lastd:
    rawdata = np.array(df.loc[firstd:today])
    perchange = 100*(rawdata[:,0]-rawdata[:,3])/rawdata[:,0]
    sb.distplot(perchange)
    changelist.append(perchange)
plt.legend(labels = Cols )
plt.show()

x = np.linspace(min(changelist[0]),max(changelist[0]), 250)
for name, data in zip(Cols, changelist):
    stats = getattr(scipy.stats,"norm").fit(data)
    print("{}: Mean={},  STD={}".format(name, stats[0],stats[1]))
    







