#!/usr/bin/env python

#Install the dependencies
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import yfinance as yf
import streamlit as st
st.header("Forta Stock Price Modeling")
plt.style.use('bmh')
###Fetching the Data
tickers= ['FORT20622-USD']
df=yf.download(tickers,start="2023-1-1", end='2024-12-31')
df1=df['Close']

df.head()


# In[ ]:


df.tail()


# In[ ]:


########2
import numpy as np
from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler(feature_range=(0,1))
df1=scaler.fit_transform(np.array(df1).reshape(-1,1))


# In[ ]:


##split1
training_size=int(len(df1)*0.68)
test_size=len(df1)-training_size
train_data,test_data=df1[0:training_size,:],df1[training_size:len(df1),:1]


# In[ ]:


#ALGO1
import numpy
# convert an array of values into a dataset matrix
def create_dataset(dataset, time_step=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-time_step-1):
		a = dataset[i:(i+time_step), 0]   ###i=0, 0,1,2,3-----99   100 
		dataX.append(a)
		dataY.append(dataset[i + time_step, 0])
	return numpy.array(dataX), numpy.array(dataY)


# In[ ]:


# reshape1 
time_step = 100
X_train, y_train = create_dataset(train_data, time_step)
X_test, ytest = create_dataset(test_data, time_step)


# In[ ]:


# reshape2 
X_train =X_train.reshape(X_train.shape[0],X_train.shape[1] , 1)
X_test = X_test.reshape(X_test.shape[0],X_test.shape[1] , 1)


# In[ ]:


### Create the Stacked LSTM model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM


# In[ ]:


#ModelsRuns
model=Sequential()
model.add(LSTM(50,return_sequences=True,input_shape=(100,1)))
model.add(LSTM(50,return_sequences=True))
model.add(LSTM(50))
model.add(Dense(1))
model.compile(loss='mean_squared_error',optimizer='adam')


# In[ ]:


##100 Iterations
model.fit(X_train,y_train,validation_data=(X_test,ytest),epochs=50,batch_size=64,verbose=1)


# In[ ]:


#######3
import tensorflow as tf
### metrics
train_predict=model.predict(X_train)
test_predict=model.predict(X_test)


# In[ ]:


##Transformback to original form
train_predict=scaler.inverse_transform(train_predict)
test_predict=scaler.inverse_transform(test_predict)


# In[ ]:


#####4
### Calculate RMSE performance metrics
import math
from sklearn.metrics import mean_squared_error
BacktestError=math.sqrt(mean_squared_error(y_train,train_predict))
# BacktestError
len(train_predict)
len(y_train)

y= pd.DataFrame(train_predict)
x=pd.DataFrame(y_train)


# In[ ]:


#######
### Plotting 
# shift train predictions for plotting
look_back=100
trainPredictPlot = numpy.empty_like(df1)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[look_back:len(train_predict)+look_back, :] = train_predict
# shift test predictions for plotting
testPredictPlot = numpy.empty_like(df1)
testPredictPlot[:, :] = numpy.nan
testPredictPlot[len(train_predict)+(look_back*2)+1:len(df1)-1, :] = test_predict
# plot baseline and predictions
# plt.plot(scaler.inverse_transform(df1))
# plt.plot(trainPredictPlot)
# plt.plot(testPredictPlot)
# plt.show()


# In[ ]:


#########6
x_input=test_data[(len(test_data)-100):].reshape(1,-1)
temp_input=list(x_input)
temp_input=temp_input[0].tolist()


# In[ ]:


# demonstrate prediction for next 5 days
from numpy import array


# In[ ]:


lst_output=[]
n_steps=100
i=0
while(i<1):
    
    if(len(temp_input)>100):
        #print(temp_input)
        x_input=np.array(temp_input[1:])
        print("{} day input {}".format(i,x_input))
        x_input=x_input.reshape(1,-1)
        x_input = x_input.reshape((1, n_steps, 1))
        #print(x_input)
        yhat = model.predict(x_input, verbose=0)
        print("{} day output {}".format(i,yhat))
        temp_input.extend(yhat[0].tolist())
        temp_input=temp_input[1:]
        #print(temp_input)
        lst_output.extend(yhat.tolist())
        i=i+1
    else:
        x_input = x_input.reshape((1, n_steps,1))
        yhat = model.predict(x_input, verbose=0)
        print(yhat[0])
        temp_input.extend(yhat[0].tolist())
        print(len(temp_input))
        lst_output.extend(yhat.tolist())
        i=i+1
    

print(lst_output)


# In[ ]:


######7
day_new=np.arange(1,101)
day_pred=np.arange(101,101)


# In[ ]:


from datetime import datetime
from dateutil.relativedelta import relativedelta
date_now = datetime.now().date()
start_date = date_now + relativedelta(days=+1)


# In[ ]:


start_date


# In[ ]:


# predictions['Date'] = pd.date_range(start='8/27/2024', periods=len(predictions), freq='D')


# In[ ]:


##See all the predictions
predictions=pd.DataFrame(scaler.inverse_transform(lst_output))
predictions.columns=['Close']
predictions['Date'] = pd.date_range(start=start_date, periods=len(predictions), freq='D')
predictions


# In[ ]:





# In[ ]:


df=df.reset_index()
df2=df[['Date', 'Close']]
# df3 = df.append(predictions, ignore_index = True)
df3 = pd.concat([df, predictions], ignore_index=True)
df4=df3.reset_index()


data=df4.tail(10)
dat = data.style.format({"Close": "{:.6f}".format})
dat


# import plotly.express as px
# fig = px.line(df4, x="Date", y="Close")
# fig.show()

# st.plotly_chart(fig)
# st.plotly_chart(fig, use_container_width=False)
