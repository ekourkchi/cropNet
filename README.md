# cropNet

## Overview

The main objective of this project is to collect and process data from the selected HOBO and CAMPBELL stations that are managed by this project. The stored data can be accessed through the URL queries. The server starts updating the local database at 1:00 AM (HST) and generates a set of forecasts for the future days. The entire process takes about an hour. This API only give access to the latest forecasts.

+ To see the server in action please visit [https://cropnet.eng.hawaii.edu/](https://cropnet.eng.hawaii.edu/)
+ To learn how to use the **API**, please visit [https://cropnet.eng.hawaii.edu/api](https://cropnet.eng.hawaii.edu/api)

## Introduction

To establish a benchmark for the most simple forecasting scenario, we execute the basic GPR code (implemented in Matlab). In this scenario, the entire series is used for training, except the last three years that is used for testing. 

This analysis and all other analysis in this document are based on an autoregressive approach that assumes the pattern of fluctuations is repeated and the value at each point is correlated with the past values. 

<img src="https://user-images.githubusercontent.com/13570487/125725551-183ba71d-d824-44db-bee6-071410360c69.jpg" width=50% height=50%>




## Jupyter Notebook

This notebook represetns how the GPR+PSO model has been implementd.

+ GitHub ([https://github.com/ekourkchi/Weather_research/blob/master/HOBO_GPR_PSO.ipynb](here))
+ Google Colab ([https://colab.research.google.com/drive/1N_zgGgf0pUAxjN3XdXOUCl9piThZsY7e?usp=sharing](here))

