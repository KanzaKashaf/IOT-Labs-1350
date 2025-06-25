import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import random

np.random.seed(42)
random.seed(42)

# Generate synthetic accelerometer data
def generate_accel_data(samples=10000):
    X, y = [], []

    for _ in range(samples):
        if random.random() < 0.7:
            # Class 0: Stable state
            x = random.uniform(-3, 3) + np.random.normal(0, 0.5)
            y_axis = random.uniform(-3, 3) + np.random.normal(0, 0.5)
            label = 0
        else:
            # Class 1: Sudden unstable/fall motion (higher abrupt values)
            x = random.uniform(-15, 15) + np.random.normal(0, 2)
            y_axis = random.uniform(-15, 15) + np.random.normal(0, 2)
            label = 1

        X.append([x, y_axis])
        y.append(label)

    return np.array(X), np.array(y)

# Generate dataset
X, y = generate_accel_data(15000)

# Normalize feature values
X_min = X.min(axis=0)
X_max = X.max(axis=0)
X_norm = (X - X_min) / (X_max - X_min)

# Split into training/validation sets
X_train, X_val, y_train, y_val = train_test_split(X_norm, y, test_size=0.2, random_state=42, stratify=y)

# Build neural network model
model = Sequential([
    Dense(32, activation='relu', input_shape=(2,)),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dropout(0.1),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train
history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50, batch_size=64, callbacks=[early_stop])

# Evaluate model
y_pred_prob = model.predict(X_val)
y_pred = (y_pred_prob > 0.5).astype(int)

print("\nClassification Report:\n", classification_report(y_val, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_val, y_pred))


model.save("fall_detection_model.h5")
# Plot confusion matrix
sns.heatmap(confusion_matrix(y_val, y_pred), annot=True, fmt="d", cmap="Blues")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()



# Convert to TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Optional, for size optimization
tflite_model = converter.convert()

# Save .tflite file
with open("my_accel_model.tflite", "wb") as f:
    f.write(tflite_model)
