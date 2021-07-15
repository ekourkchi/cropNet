# cropNet

Overview

The main objective of this project is to collect and process data from the selected HOBO and CAMPBELL stations that are managed by this project. The stored data can be accessed through the URL queries. The server starts updating the local database at 1:00 AM (HST) and generates a set of forecasts for the future days. The entire process takes about an hour. This API only give access to the latest forecasts. The historical forecasts are not accessible at this time.

The forecasts for Evapotransportation is available for 1, 3 and 5 day(s) ahead of the last day with available measurements. The forecast for the rainfall is only available for the next day. 


