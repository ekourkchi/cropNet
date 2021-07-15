# cropNet

## Table of contents
1. [Overview](#intro)
2. [Gaussian Process Autoregression](#gpr)
3. [Particle Swarm Optimization](#pso)
4. [Code Structure](#code)
5. [Jupyter Notebook](#notebook)
6. [Disclaimer](#disclaimer)

## Overview <a name="intro"></a>

The main objective of this project is to collect and process data from the selected HOBO and CAMPBELL stations that are managed by this project. The stored data can be accessed through the URL queries. The server starts updating the local database at 1:00 AM (HST) and generates a set of forecasts for the future days. The entire process takes about an hour. This API only gives access to the latest forecasts.

+ To read about the technical details of our methodology, please refer to the draft of our manuscript: [GPR_forecasting.pdf](https://github.com/ekourkchi/cropNet/blob/main/GPR_forecasting.pdf)
+ To see the server in action please visit [https://cropnet.eng.hawaii.edu/](https://cropnet.eng.hawaii.edu/)
+ To learn how to use the **API**, please visit [https://cropnet.eng.hawaii.edu/api](https://cropnet.eng.hawaii.edu/api)

## Gaussian Process Autoregression <a name="gpr"></a>

To establish a benchmark for the most simple forecasting scenario, we execute a basic Gaussian Process Regression (GPR) code. In this scenario, the entire series is used for training.

This analysis and all other analysis in this document are based on an autoregressive approach that assumes the pattern of fluctuations is repeated and the value at each point is correlated with the past values.

<img src="https://user-images.githubusercontent.com/13570487/125725551-183ba71d-d824-44db-bee6-071410360c69.jpg" width=50% height=50%>

GPR is a statistical machine learning technique based on a Bayesian approach that generates predictions following the behavior of data (e.g. Gibbs & MacKay 1997; Rasmussen & Williams 2006).

In our analysis, we use [*George Python Package*](https://george.readthedocs.io/en/latest/), developed by Ambikasaran et al. (2015), to efficiently calculate the likelihood function and to make predictions.

### Particle Swarm Optimization (PSO) <a name="pso"></a>

The large number of hyperparameters and the size of the training data increases the complexity of the optimization algorithms, calling for an extensive computational power. We use the Particle Swarm Optimization (PSO) algorithm to explore the hyperparameter space to maximize the likelihood function.

<img src="https://user-images.githubusercontent.com/13570487/125727951-cfb74bf9-1619-4701-b0b4-4a9558561511.png" width=50% height=50%>

The Particle Swarm Optimization (PSO) technique was originally developed  by  Kennedy  and  Eberhart  (1995); Shi and Eberhart (1998) to simulate the behavioral evolution of social organisms that are in group motions such as bird flocks or fish schools. This approach leverages the power of a swarm of particles to explore the parameter space  hoping  to  find  the  optimum  solution. In this approach, each individual particle in the parameter space is denoted by its position and velocity. The performance of each particle is evaluated based on the value of the objective function at its position. Each particle has a memory of its “best” previous position.  Moreover, the best position that is ever found in the past history of the evolution of all particles is recorded. In this optimization algorithm, the position and velocity of all particles are randomly initialized and iteratively updated. In each iteration, the position and velocity of each particle is updated according to its previous “best” location and the historical “best” position of the entire group. At the end of the desired number of iterations, the optimum point is reported to be the best position ever achieved by the ensemble of particles over the entire course of their evolution.

## Code Structure <a name="code"></a>

1. Codes to extract data and populate the database
   - `ETxls.sh` This script is executed once a day at 1:00 AM and updates the database and generates the forecasts for the next coming days
     - `Hobo_LONG_getData.py` extracts data for the HOBO stations and populates the local database
     - `ET2XLS_HOBO.py` Reorganizes data and stores daily ETo and Rainfall in an excel spreadsheet
     - `ET2XLS_Campbell.py` extracts data for the CAMPBELL stations and appends the output to the excel spreadsheet
     - `forecaste_ETrain.py` runs the forecasts for all individual stations
2. Forecasting Code(s)
   - `forecaste_ETrain.py` invokes the forecasting routine multiple times to predict ETo and Rainfall for the next days. The forecasts are stored in a separate table in the database for the future use of the API calls
     - `forecast_ET.py` is the forecasting routine that leverages GPR+PSO methology to model the ETo and Rainfall time-series. The prototype of this code is also available in the form of [Jupyter Notebook](https://github.com/ekourkchi/Weather_research/blob/master/HOBO_GPR_PSO.ipynb), with more human readable comments.
3. Python flask code to launch the API
   - `api_server.sh` starts setting up the API service when the server boots up
     - `api_server.py` is the main python code that uses the [Flask](https://flask.palletsprojects.com/en/2.0.x/) package to handle the API requests. On each API call, the latest evaluated forecasts are queried from the database and the outputs are organized in a *JSON* structure


## Jupyter Notebook (an implementation in Python) <a name="notebook"></a>

This notebook represents how the GPR+PSO model has been implemented.

+ [GitHub](https://github.com/ekourkchi/Weather_research/blob/master/HOBO_GPR_PSO.ipynb)
+ [Google Colab](https://colab.research.google.com/drive/1N_zgGgf0pUAxjN3XdXOUCl9piThZsY7e?usp=sharing)

## Disclaimer <a name="Disclaimer"></a> <a name="disclaimer"></a>

 * All rights reserved. The material may not be reproduced or distributed, in whole or in part, without the prior agreement
 * Contact: *Ehsan Kourkchi* <ekourkchi@gmail.com>
