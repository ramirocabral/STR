import numpy as np
import pandas as pd
from matplotlib import pylab as plt
from IPython import display
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from lib.preprocessing import preprocess_data


data = pd.read_csv("data/new_data.csv")

data = preprocess_data(data)

# Separar features y labels
X = data.drop(columns=["consumption"])
T = data["consumption"]

data['daylight'].value_counts()

import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

from lib.normalization import normalize_data

X_train, X_test, T_train, T_test, x_scaler, y_scaler = normalize_data(X, T, scaler_dir="models")

# --- importamos modelo ---

model = tf.keras.models.load_model('models/best_energy_model.keras')

# --- Callbacks ---

# 1. Detiene el entrenamiento si no hay mejora después de 30 épocas
es = EarlyStopping(
    monitor='val_loss', 
    patience=75, 
    min_delta=0.0001,
    verbose=1
)

# 2. Reduce el Learning Rate si no hay mejora después de 5 épocas
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=5,
    min_lr=1e-6,
    verbose=1
)

# --- Entrenamiento ---
history = model.fit(
    X_train, T_train,
    batch_size=16,
    epochs=1000,
    verbose=1,
    validation_data=(X_test, T_test),
    callbacks=[es, reduce_lr]  # Añadimos el nuevo callback
)

# --- Post-entrenamiento ---
print("Entrenamiento finalizado.")

# -----------------------------------------------------------------
# CÓDIGO NUEVO PARA CARGAR Y EVALUAR EL MEJOR MODELO
# -----------------------------------------------------------------


# Cargar el modelo guardado y evaluarlo (MÉTODO RECOMENDADO)
# Esto confirma que el archivo se guardó bien y te da su 'loss' en los datos de prueba
print("Cargando el mejor modelo guardado por ModelCheckpoint...")

# Carga el modelo desde el archivo que guardó el callback
best_model = tf.keras.models.load_model('models/best_energy_model.keras')

print("Evaluando el mejor modelo con los datos de prueba...")

# .evaluate() devuelve la pérdida (loss) y cualquier otra métrica (ej. accuracy)
# La pérdida (loss) es siempre el primer elemento (índice 0)
results = best_model.evaluate(X_test, T_test, verbose=0)

print(f"Pérdida (Loss) del mejor modelo cargado: {results[0]:.6f}")
