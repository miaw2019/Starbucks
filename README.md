Starbuck_Capstone
==============================

My goal of this project is to build a predict model to find out whether a customer will respond to an certain offer based on the simulated. The model I choose is LighGBM. 


Results
------------

After several round of tunning the result of RMSE for test data reaches 0.000556 and the log_loss is lower than 0.000166. From the model we can tell that the top 3 important features for split are:

1.Customers' income

2.Offer view time

3.The year of the customer becomes the member

the top 5 important features for gain are:

1.whether the offer is complete

2.whether the offer is viewed

3.Offer view time
