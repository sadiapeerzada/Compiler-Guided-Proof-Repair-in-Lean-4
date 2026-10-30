"""Explicit post-hoc statistical methods; conventional exact McNemar at b=c=0."""
from collections import defaultdict
import math
from functools import lru_cache
from statistics import NormalDist
import numpy as np

SEED=20271021
RESAMPLES=10000


def wilson(k,n,alpha=.05):
    if n<=0:return None
    z=NormalDist().inv_cdf(1-alpha/2);p=k/n;scale=1+z*z/n
    center=(p+z*z/(2*n))/scale;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/scale
    return [max(0,center-half),min(1,center+half)]


@lru_cache(maxsize=None)
def mcnemar(b,c):
    if min(b,c)<0:raise ValueError('Negative discordance')
    n=b+c
    return 1.0 if n==0 else min(1.0,2*sum(math.comb(n,k) for k in range(min(b,c)+1))/(2**n))


def newcombe_paired(a,b,c,d,alpha=.05):
    """Paired method 10: Wilson marginals, positive covariance minus n/2.

    Table [[a,b],[c,d]] is first/second success classification. The phi
    adjustment and zero-marginal convention follow Newcombe (1998), method 10;
    checked against the official statsmodels documented example [[10,5],[2,20]].
    This score sensitivity assumes independent pairs, not independent repairs.
    """
    n=a+b+c+d
    if n<=0 or min(a,b,c,d)<0:raise ValueError('Invalid matched table')
    p=(a+b)/n;q=(a+c)/n;lo1,hi1=wilson(a+b,n,alpha);lo2,hi2=wilson(a+c,n,alpha)
    product=(a+b)*(c+d)*(a+c)*(b+d)
    covariance=a*d-b*c
    corrected=max(covariance-n/2,0) if covariance>0 else covariance
    rho=corrected/math.sqrt(product) if product else 0
    left=math.sqrt(max(0,(p-lo1)**2+(hi2-q)**2-2*rho*(p-lo1)*(hi2-q)))
    right=math.sqrt(max(0,(hi1-p)**2+(q-lo2)**2-2*rho*(hi1-p)*(q-lo2)))
    return {'interval':[max(-1,p-q-left),min(1,p-q+right)],'corrected_phi':rho,'difference':p-q,
            'method':'Newcombe (1998) paired method 10: Wilson marginal intervals with positive covariance n/2 correction; undefined phi set to zero.'}


def identification_bounds(rows,first='C',second='B'):
    if not rows:raise ValueError('No cases')
    low=high=0
    for r in rows:
        x,y=r['outcomes'][first],r['outcomes'][second]
        low+=(0 if x is None else int(x))-(1 if y is None else int(y))
        high+=(1 if x is None else int(x))-(0 if y is None else int(y))
    return [low/len(rows),high/len(rows)]


def bootstrap_difference(records,field,unit='family',conditions=('B','C'),resamples=RESAMPLES,seed=SEED):
    """Whole-family (primary) or whole-problem (secondary), ratio of sums."""
    grouped=defaultdict(lambda:np.zeros(4))
    for r in records:
        if r['condition'] not in conditions or r.get(field) is None:continue
        offset=0 if r['condition']==conditions[0] else 2
        v=grouped[r[unit]];v[offset]+=r[field];v[offset+1]+=1
    if not grouped:return {'estimable':False,'reason':'No observed eligible metric records'}
    values=np.array(list(grouped.values()));total=values.sum(axis=0)
    if total[1]==0 or total[3]==0:return {'estimable':False,'reason':'One condition has no eligible completed observations'}
    draws=np.random.default_rng(seed).multinomial(len(values),[1/len(values)]*len(values),size=resamples)
    sums=draws@values;valid=(sums[:,1]>0)&(sums[:,3]>0)
    differences=sums[valid,2]/sums[valid,3]-sums[valid,0]/sums[valid,1]
    return {'estimable':True,'difference':total[2]/total[3]-total[0]/total[1],
            'interval':np.quantile(differences,[.025,.975]).tolist(),'B_denominator':int(total[1]),'C_denominator':int(total[3]),
            'units':len(values),'unit':unit,'resamples':resamples,'valid_resamples':int(valid.sum()),'seed':seed,
            'method':'Percentile whole-unit bootstrap, NumPy default_rng multinomial cluster counts, ratio of observed sums; no missing outcome imputation.'}


def approximate_mde(n,q,alpha=.05,power=.8):
    if n<=0 or not 0<q<=1:raise ValueError('Specify positive n and assumed discordance q')
    delta=(NormalDist().inv_cdf(1-alpha/2)+NormalDist().inv_cdf(power))*math.sqrt(q/n)
    return {'n':n,'assumed_discordance':q,'expected_discordant_pairs':n*q,'alpha':alpha,'power':power,
            'normal_approximation_MDE':delta,'feasible_under_q':delta<=q,
            'formula':'(z_(1-alpha/2) + z_power) * sqrt(q/n); independent pairs, specified discordance probability q.'}


def exact_power(n,q,delta,alpha=.05):
    """Multinomial paired outcomes: D~Bin(n,q), C-only|D~Bin(D,(1+delta/q)/2)."""
    if not 0<q<=1 or not 0<=delta<=q:raise ValueError('Require 0 <= delta <= q <= 1')
    p=(1+delta/q)/2;value=0.0
    for discordant in range(n+1):
        pd=math.comb(n,discordant)*q**discordant*(1-q)**(n-discordant)
        reject=0
        for positive in range(discordant+1):
            if mcnemar(positive,discordant-positive)<=alpha:
                reject+=math.comb(discordant,positive)*p**positive*(1-p)**(discordant-positive)
        value+=pd*reject
    return value


def exact_mde(n,q,alpha=.05,power=.8):
    if exact_power(n,q,q,alpha)<power:return None
    low,high=0,q
    for _ in range(35):
        mid=(low+high)/2
        if exact_power(n,q,mid,alpha)>=power:high=mid
        else:low=mid
    return high
