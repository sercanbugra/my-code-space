import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import yfinance as yf
from datetime import datetime, timedelta
import tensorflow as tf
import xgboost as xgb
from sklearn.metrics import mean_squared_error

# Ensure yfinance overrides
yf.pdr_override()

# Get the stock quote
df = pdr.get_data_yahoo('SOUN', start='2022-10-01', end=datetime.now())

# Create a new dataframe with only the 'Close' column
data = df.filter(['Close'])
# Convert the dataframe to a numpy array
dataset = data.values
# Get the number of rows to train the model on
training_data_len = int(np.ceil(len(dataset) * .95))

# Scale the data using TensorFlow Normalization
normalizer = tf.keras.layers.Normalization()
normalizer.adapt(dataset)
scaled_data = normalizer(dataset)

# Create the training data set 
train_data = scaled_data[:training_data_len]
# Create the testing data set
test_data = scaled_data[training_data_len - 60:]

# Split the data into x_train and y_train data sets
x_train = []
y_train = []

for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i])
    y_train.append(train_data[i])

# Convert the x_train and y_train to numpy arrays 
x_train, y_train = np.array(x_train), np.array(y_train)

# Split the data into x_test and y_test data sets
x_test = []
y_test = dataset[training_data_len:]

for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i])

# Convert the x_test to a numpy array
x_test = np.array(x_test)

# Reshape the data for XGBoost
x_train = x_train.reshape((x_train.shape[0], x_train.shape[1]))
x_test = x_test.reshape((x_test.shape[0], x_test.shape[1]))

# Train the XGBoost model
model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=1000)
model.fit(x_train, y_train)

# Get the model's predicted price values 
predictions = model.predict(x_test)
predictions = predictions.reshape(-1, 1)
predictions = normalizer.mean.numpy() + predictions * normalizer.variance.numpy() ** 0.5

# Get the root mean squared error (RMSE)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
print('RMSE: ', rmse)

# Predict the next 10 days
last_60_days = scaled_data[-60:].numpy()  # Convert to numpy array
next_10_days = []

for i in range(10):
    X_test = last_60_days[-60:].reshape(1, -1)
    pred_price = model.predict(X_test)
    pred_price = normalizer.mean.numpy() + pred_price * normalizer.variance.numpy() ** 0.5
    next_10_days.append(pred_price[0])
    last_60_days = np.append(last_60_days, pred_price).reshape(-1, 1)[-60:]

# Create a dataframe for the next 10 days
last_date = df.index[-1]
future_dates = [last_date + timedelta(days=i) for i in range(1, 11)]
future_predictions = pd.DataFrame(data={'Date': future_dates, 'Close': next_10_days})
future_predictions.set_index('Date', inplace=True)

# Create dataframes for plotting and saving
train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predictions

# Save to Excel
with pd.ExcelWriter('stock_predictions_xgboost.xlsx') as writer:
    train.to_excel(writer, sheet_name='Train')
    valid.to_excel(writer, sheet_name='Validation')
    future_predictions.to_excel(writer, sheet_name='Future')

# Plot the data
plt.figure(figsize=(16, 6))
plt.title('Model')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
plt.plot(future_predictions['Close'], linestyle='dashed', color='red')
plt.legend(['Train', 'Val', 'Predictions', 'Future'], loc='upper left')
plt.show()
