# cropNet

## Overview

The main objective of this project is to collect and process data from the selected HOBO and CAMPBELL stations that are managed by this project. The stored data can be accessed through the URL queries. The server starts updating the local database at 1:00 AM (HST) and generates a set of forecasts for the future days. The entire process takes about an hour. This API only give access to the latest forecasts.

+ To see the server in action please visit [https://cropnet.eng.hawaii.edu/](https://cropnet.eng.hawaii.edu/)
+ To learn how to use the **API**, please visit [https://cropnet.eng.hawaii.edu/api](https://cropnet.eng.hawaii.edu/api)

## Gaussian Process Autoregression

To establish a benchmark for the most simple forecasting scenario, we execute a basic Gaussian Process Regression (GPR) code. In this scenario, the entire series is used for training.

This analysis and all other analysis in this document are based on an autoregressive approach that assumes the pattern of fluctuations is repeated and the value at each point is correlated with the past values. 

<img src="https://user-images.githubusercontent.com/13570487/125725551-183ba71d-d824-44db-bee6-071410360c69.jpg" width=50% height=50%>

GPR is a statistical machine learning technique based on a Bayesian approach that generates predictions following the behaviour of data (e.g. Gibbs & MacKay 1997; Rasmussen & Williams 2006). This method has been used in various fields. 

In our analysis, we used [*George Python Package*](https://george.readthedocs.io/en/latest/), developed by Ambikasaran et al. (2015), to efficiently calculate the likelihood function and to make predictions. 

### Particle Swarm Optimization (PSO)

The large number of hyperparameters and the size of the training data increases the complexity of the optimization algorithms, calling for an extensive computational power. We use the Particle Swarm Optimization (PSO) algorithm to explore the hyperparameter space to maximize the likelihood function.

<img src="https://user-images.githubusercontent.com/13570487/125727951-cfb74bf9-1619-4701-b0b4-4a9558561511.png" width=50% height=50%>

The Particle Swarm Optimization (PSO) technique wasoriginally developed  by  Kennedy  and  Eberhart  (1995); Shi and Eberhart (1998) to simulate the behavioral evolution of social organisms that are in group motions suchas bird flocks or fish schools. This approach leverages thepower of a swarm of particles to explore the parameterspace  hoping  to  find  the  optimum  solution. In this approach, each individual particle in the parameter space isdenoted by its position and velocity. The performance of each particle is evaluated based on the value of the objective function at its position. Each particle has a memory of its “best” previous position.  Moreover, the best position that is ever found in the past history of the evolution of all particles is recorded. In this optimization algorithm, the position and velocity of all particles are randomly initialized and iteratively updated. In each iteration, the position and velocity of each particle is updated according toits previous “best” location and the historical “best” position of the entire group. At the end of the desired number of iterations, the optimum point is reported to be the best position ever achieved by the ensemble of particles over the entire course of their evolution.


## Jupyter Notebook (an implementation in Python)

This notebook represetns how the GPR+PSO model has been implementd.

+ [GitHub](https://github.com/ekourkchi/Weather_research/blob/master/HOBO_GPR_PSO.ipynb)
+ [Google Colab](https://colab.research.google.com/drive/1N_zgGgf0pUAxjN3XdXOUCl9piThZsY7e?usp=sharing)

