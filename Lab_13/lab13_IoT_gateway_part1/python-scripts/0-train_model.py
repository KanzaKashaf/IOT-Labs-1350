# basic code (given before lab)

#Overfitting due to simple problem of 2 input features and 5 classes well separated while deeper network
# This code generates synthetic data for a DHT sensor classification problem and trains a neural network to classify the data into 5 classes.


# Import necessary libraries
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import random

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate synthetic data with 5 classes
def generate_data(samples=15000):
    X = []
    y = []

    for _ in range(samples):
        r = random.random()
        if r < 0.2:
            # Normal: 20–28°C, 40–60%
            temp = random.uniform(20, 28)
            hum = random.uniform(40, 60)
            label = 0
        elif r < 0.4:
            # Hot and Humid: >28°C, >60%
            temp = random.uniform(29, 40)
            hum = random.uniform(61, 90)
            label = 1
        elif r < 0.6:
            # Cold and Dry: <18°C, <40%
            temp = random.uniform(5, 17)
            hum = random.uniform(10, 39)
            label = 2
        elif r < 0.8:
            # Hot and Dry: >28°C, <40%
            temp = random.uniform(29, 40)
            hum = random.uniform(10, 39)
            label = 3
        else:
            # Cold and Humid: <18°C, >60%
            temp = random.uniform(5, 17)
            hum = random.uniform(61, 90)
            label = 4

        X.append([temp, hum])
        y.append(label)

    return np.array(X), np.array(y)

# Generate data
X, y = generate_data(20000)

# Normalize features
X_min = X.min(axis=0)
X_max = X.max(axis=0)
X_norm = (X - X_min) / (X_max - X_min)

# Build a deeper neural network
model = Sequential([
    Dense(32, activation='relu', input_shape=(2,)),
    Dense(64, activation='relu'),
    Dense(64, activation='relu'),
    Dense(32, activation='relu'),
    Dense(5, activation='softmax')  # 5 classes
])

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train
model.fit(X_norm, y, epochs=10, batch_size=32, validation_split=0.2, verbose=1)

# Save model and normalization data
model.save("dht_classifier.h5")
np.savez("normalization.npz", min=X_min, max=X_max)

print("[OK] Model and normalization data saved.")
