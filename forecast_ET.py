import sys
import time
import os
import subprocess
import math
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import Table, Column 
from scipy.stats import linregress
from scipy import interpolate
from scipy import polyval, polyfit
from scipy import odr
import pylab as py
from matplotlib import gridspec
import sklearn.datasets as ds
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import scipy.optimize as op
from scipy.linalg import cholesky, inv,det
from scipy.optimize import minimize
import george
from george import kernels
import pandas as pd
from datetime import datetime, timedelta
import time
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold

# Commented out IPython magic to ensure Python compatibility.
# Import modules
import numpy as np
from pyswarms.single.global_best import GlobalBestPSO
# Import PySwarms
import pyswarms as ps
from pyswarms.utils.functions import single_obj as fx

   

stationInfo = {
    10906989:{"timeZone": "US/Hawaii", "name": "ALOUN_HELEMANO", "GPS": "21 32 8.9 N 158 02 05.0 W"},  
    20173022:{"timeZone": "US/Hawaii", "name": "HIRAKO", "GPS": "20 00 14.6 N 155 41 29.3 W"}, 
    20009161:{"timeZone": "US/Hawaii", "name": "KULA_AG_PARK", "GPS": "20 47 43.2 N 156 21 35.6 W"}, 
    20121046:{"timeZone": "Pacific/Guam", "name": "MALOJLOJ MEDA", "GPS": "13 20 21.0 N 144 45 49.0 E"},
    20006321:{"timeZone": "US/Hawaii", "name": "MAO", "GPS": "21 27 4.9 N 158 09 25.8 W"},
    20173020:{"timeZone": "US/Hawaii", "name": "PIONEER CORN", "GPS": "21 33 41.5 N 158 07 40.3 W"},
    20173019:{"timeZone": "US/Hawaii", "name": "SEIZEN", "GPS": "20 01 26.2 N 155 39 00.5 W"},
    20824841:{"timeZone": "Pacific/Guam", "name": "WATSON", "GPS": ""},
    20824842:{"timeZone": "Pacific/Guam", "name": "WUSSTIG", "GPS": ""},
    20121045:{"timeZone": "Pacific/Guam", "name": "YIGO", "GPS": "13 33 54.3 N 144 52 38.4 E"},   #            
    20121047:{"timeZone": "Pacific/Samoa", "name": "MALAEIMI ", "GPS": ""},
    20121048:{"timeZone": "Pacific/Samoa", "name": "TAFETA", "GPS": ""},
    20173018:{"timeZone": "US/Hawaii", "name": "TEXEIRA", "GPS": ""},
    'PH1':{"timeZone": "US/Hawaii", "name": "PIONEER Gay", "GPS": "21.568543N  -158.155975W"},
    'PH2':{"timeZone": "US/Hawaii", "name": "PIONEER Helemano", "GPS": "21.565335N  -158.097097W"},
    }

################################################################################
def metrics(y1, y2):

    '''
    y1 and y2 are two series of the same size

    This function outputs the MAE, RMSE and R^2 
    of the cross evaluated series.

    '''
    y1 = y1.reshape(-1)
    y2 = y2.reshape(-1)
    RMSE = np.sqrt(np.mean((y1-y2)**2))
    MAE = np.mean(np.abs(y1-y2))
    R2 = r2_score(y1, y2)

    return MAE, RMSE, R2

################################################################################

def funcMAX(func, X, y, addParam = 0, maxiter=500, method='L-BFGS-B', verbose=False):

    '''
    A function to find the optimum parameters of the input funtion "func",
    where yp = func(X) and RMSE(y-yp) is minimzed

    output: "results" is the object that contains everything about the fit
    result.x holds the optimized parameters
    '''

    t1 =  datetime.now()  # t1 and t2 are used for timing this process
    ###########################################
    n = X.shape[1]
    # Maximum Likelihood
    Param_init = np.random.rand(n+addParam)
    result = minimize(func(X, y), Param_init, 
                    method=method, options={"maxiter":maxiter})
    print("--------------------")
    if verbose:
        print(result)
    ###########################################
    if not verbose: 
        print("Fit Success: ", result.success)
    t2 =  datetime.now()
    print("Execution time: ", t2-t1)
    print("--------------------")

    return result

################################################################################

def dataPrepare2(y, n = 3, d = 1):

    '''
    Generating discrete data points out of the given series

    y: main signal, e.g. ET0
    n: the number of previous data points that are used for forcasting
    d: the number of days ahead for forecasting

    output: feature matrix XS, and target values ys
    '''

    N = len(y)
    dd = d - 1

    XS = np.zeros((N-n-dd, n))
    ys = np.zeros(N-n-dd)

    p = 0 

    for i in range(0, N-n-dd):
        if not np.isnan(y[i:i+n]).any() and not np.isnan(y[i+n+dd]):
            XS[p,:n]      = y[i:i+n]     
            ys[p] = y[i+n+dd]
            p+=1

    return XS[:p,:], ys[:p]

################################################################################

""" 
Defning the Gaussain Process using George package

Defning the *kernel*:

$k_{ij} = k(X_i, X_j) = \sigma^2 exp(-r^2)$,
where $r$ is the euclidean distance between $X_i$ and $X_j$.

$X$ is the parameter vector after normalization: $X=(x_1, x_2, ....)$. 
Let's assume, we use $ET0$ and $R_n$ as features. Then for each point in the feature space: $X= (ET0/L_1, R_n/L_2)$, where $L$ is the normalization factor. Vector $L$ and $\sigma$ are the free parameters of the kernel we are interested to find.To make use of the previous data points in the series, we can extend the number of features, i.e. $X= (ET0^{(1)}/L_1, R^{(1)}_n/L_2, ET0^{(2)}/L_3, R^{(2)}_n/L_4, ...)$. $ET0^{(1)}$ is the previous data point in the series, $ET0^{(2)}$ is the second previous data point etc. $X$ can hold as many as data point as we want. It can include a mixture of different parameters, other series, and basically anything that we think our problem depends on.
In the following function, $L$, $\sigma$, and $y_{err}$ are all given in the same array called $\theta$. $y_{err}$ represents the uncertainty of the target values (the present value of $ET0$) and is taken as a free parameter that basically prevents over-training.
"""

def GPR(X, y, lnlikelihood=True):
    '''
    The output of this function is another function, either the lnlikelihood, or 
    the gp (the gaussian process regressor that is dfined by giving theta)
    '''
    n = X.shape[1]
        
    def step(theta):

            L = np.exp(theta[:n])
            sigma = np.exp(theta[n])   
            yerr = np.exp(theta[n+1])
            
            kernel = sigma * kernels.ExpSquaredKernel(np.ones(n), ndim=n)

            gp = george.GP(kernel)

            if lnlikelihood:
                gp = george.GP(kernel)
                gp.compute(X / np.vstack([L]*X.shape[0]), yerr)
                return -gp.lnlikelihood(y)
            else:
                X0 = X / np.vstack([L]*X.shape[0])
                gp.compute(X0, yerr)
                return gp
        
    return step

################################################################################
################################################################################
################################################################################

def forecast(xlsFile, serial, mode='ETo', mDelay = 3, nAhead = 1, n_particles=20, iters=50):

    """
    Load data
    data preparation
    We generate the first 3 main principal components that capture the most useful information of the data. P1, P2 and P3 are not correalted with each other while they are epressed as the linear cominination of the available featurdes, i.e. ET0, VPD, Rn and T (air temperature)

    **Note:** Make sure that the data file is addressed correctly and it's already avaialble in your Google drive.
    """

    station = stationInfo[serial]["name"]

    data = pd.read_excel(xlsFile, sheet_name=station)

    date = 'Date('+stationInfo[serial]["timeZone"]+')'

    if mode == 'ETo':
        Label = 'ETo_CIMIS (raw)'
    elif mode == 'Rain':
        Label = 'Rain (raw)'

    if serial == 'PH1' or serial == 'PH2':
        date = 'Date'
        if mode == 'ETo':
            Label = 'ETo.raw'
        elif mode == 'Rain':
            Label = 'Rainfall.raw'


    data = data[[date, Label]]

    # revising the column names
    for col in data.columns:
        newcol = col.split("(")[0].strip()
        data.rename(columns={col:newcol}, inplace=True)

    # setting up the index of the data frame
    data.set_index("Date", inplace=True)

    Label = Label.split("(")[0].strip()


    if np.isnan(data.iloc[-1][Label]):
        data = data.iloc[:-1]




    """
    Staging some data for ML modeling

    Generating train and test data sets.
    For the sake of speed, we use use a fraction of data for evaluation of our algorithm. Later to get the final results, we use the entire data set.
    """

    # training
    N = len(data)
    x = data.index
    y = data[Label]




    """ 
    Preparing the feature matrix, X, and the target vector, y
    for the given training and cross_validation sets.

    In the following example for mDelay=3, 3*4 features would be generated. 3-lags, four parameters each. So $X$ is 12-dimensional
    """

    XS2, ys2 = dataPrepare2(y, n=mDelay, d=nAhead)
    XS_test2 = y[-mDelay:].values.reshape(1,-1)

    n_components = mDelay



    """
    PSO with PySwarm
    Optimizing the GPR hyperparameters using the Particle Swarm Optimizer

    https://pyswarms.readthedocs.io/en/latest/index.html
    """

    kf = KFold(n_splits=3)
    kf.get_n_splits(XS2)

    def Xi2_swarm(x):
    
        nParticle = x.shape[0]
        out = np.zeros(nParticle)

        for train_index, cross_index in kf.split(XS2):
            
            X_train, X_cross = XS2[train_index], XS2[cross_index]
            y_train, y_cross = ys2[train_index], ys2[cross_index]

            n = X_cross.shape[1]
            m = X_cross.shape[0]

            for n_iter in range(nParticle):
                
                theta = x[n_iter,:]

                L = np.exp(theta[:n])

                gp = GPR(X_train, y_train, lnlikelihood=False)(theta)
                gp_yp_cross, gp_yp_cross_std = gp.predict(y_train, X_cross/np.vstack([L]*m), return_var=True)

                out[n_iter] += np.sum((y_cross - gp_yp_cross)**2)

        return out

    # Set-up hyperparameters
    options = {'c1': 0.5, 'c2': 0.3, 'w':0.9}

    # Call instance of PSO
    optimizer = GlobalBestPSO(n_particles=n_particles, dimensions=n_components+2, options=options)

    # Perform optimization
    cost, pos = optimizer.optimize(Xi2_swarm, iters=iters)

    truths = pos
    gp = GPR(XS2, ys2, lnlikelihood=False)(truths)


    n = XS2.shape[1]
    m_test = XS_test2.shape[0]
    m = XS2.shape[0]

    L = np.exp(truths[:n])


    gp_yp, gp_yp_std = gp.predict(ys2, XS2/np.vstack([L]*m), return_var=True)

    gp_yp_test, gp_yp_test_std = gp.predict(ys2, XS_test2/np.vstack([L]*m_test), return_var=True)

    # print(gp_yp_test, gp_yp_test_std, np.mean(XS_test2))
    # print(XS_test2)
    
    current_date = data.index[-1].strftime("%Y-%m-%d")
    forecast_date = (data.index[-1] + timedelta(days=nAhead)).strftime("%Y-%m-%d")

    MAE, RMSE, R2 = metrics(ys2, gp_yp)

    return current_date, forecast_date, gp_yp_test[0], np.mean(XS_test2), MAE, R2


