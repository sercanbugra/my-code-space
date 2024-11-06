from keras.layers import Dense, GRU, Dropout

# Build the GRU model
model = Sequential()

# First GRU layer
model.add(GRU(units=128, return_sequences=True, input_shape=(x_train.shape[1], 1), activation='tanh'))
model.add(Dropout(0.2))

# Second GRU layer
model.add(GRU(units=64, return_sequences=True))
model.add(Dropout(0.2))

# Third GRU layer
model.add(GRU(units=64, return_sequences=False))
model.add(Dropout(0.2))

# Output layer
model.add(Dense(units=1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, batch_size=1, epochs=10)

# Testing and predictions
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# Future predictions logic (same as in LSTM)
