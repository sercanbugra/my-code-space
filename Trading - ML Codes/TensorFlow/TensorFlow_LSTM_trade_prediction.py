import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pandas_datareader import data as pdr
import yfinance as yf
from datetime import datetime, timedelta
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# Ensure yfinance overrides
yf.pdr_override()

# Get the stock quote
df = pdr.get_data_yahoo('DELL', start='2022-04-01', end=datetime.now())

# Create a new dataframe with only the 'Close' column
data = df.filter(['Close'])
# Convert the dataframe to a numpy array
dataset = data.values
# Get the number of rows to train the model on
training_data_len = int(np.ceil(len(dataset) * .95))

# Scale the data using TensorFlow
scaler = tf.keras.layers.Normalization(axis=-1)
scaler.adapt(dataset)

scaled_data = scaler(dataset)

# Create the training data set 
train_data = scaled_data[:training_data_len]
# Split the data into x_train and y_train data sets
x_train = []
y_train = []

for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i])
    y_train.append(train_data[i])

# Convert the x_train and y_train to numpy arrays 
x_train, y_train = np.array(x_train), np.array(y_train)

# Build the LSTM model with additional layers and dropout
model = Sequential([
    LSTM(128, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])),
    Dropout(0.2),
    LSTM(64, return_sequences=True),
    Dropout(0.2),
    LSTM(64),
    Dropout(0.2),
    Dense(25),
    Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Implement early stopping
early_stop = EarlyStopping(monitor='loss', patience=10)

# Train the model with more epochs
model.fit(x_train, y_train, batch_size=32, epochs=100, callbacks=[early_stop])

# Create the testing data set
test_data = scaled_data[training_data_len - 60:]
x_test = []
y_test = dataset[training_data_len:]

for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i])

# Convert the data to a numpy array
x_test = np.array(x_test)

# Get the model's predicted price values 
predictions = model.predict(x_test)
predictions = scaler.mean + predictions * scaler.variance ** 0.5

# Get the root mean squared error (RMSE)
rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))
print('RMSE: ', rmse)

# Predict the next 10 days
last_60_days = scaled_data[-60:]
next_10_days = []

for i in range(10):
    X_test = np.array([last_60_days])
    pred_price = model.predict(X_test)
    pred_price_unscaled = scaler.mean + pred_price * scaler.variance ** 0.5
    next_10_days.append(pred_price_unscaled[0, 0])
    last_60_days = np.append(last_60_days, pred_price, axis=0)[-60:]

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
with pd.ExcelWriter('stock_predictions.xlsx') as writer:
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
