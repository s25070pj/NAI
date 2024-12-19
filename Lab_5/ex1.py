"""
Problem:
- Data Classification with Neural Networks

Description:
This program uses a feedforward neural network to classify data from a CSV file.
It processes the data, trains a neural network model, and evaluates its performance.

Workflow:
1. Load the dataset from a CSV file.
2. Prepare the data: features (X) and binary target (Y).
3. Split the data into training and test sets.
4. Build and train a feedforward neural network.
5. Evaluate the model using accuracy, precision, recall, and confusion matrix.

            Authors: Adrian Stoltmann, Kacper Tokarzewski
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tensorflow.keras.regularizers import l2


def load_data(file_path):
    """
    Load a CSV file into a pandas DataFrame.

    :param file_path: Path to the CSV file.
    :return: DataFrame containing the dataset.
    """
    return pd.read_csv(file_path    )


def prepare_data(df, feature_columns, target_column, threshold):
    """
    Extract features and transform the target column into binary classes.

    :param df: DataFrame containing the dataset.
    :param feature_columns: List of columns to use as features.
    :param target_column: Index of the target column.
    :param threshold: Value to binarize the target column.
    :return: Feature matrix (X) and binary target vector (y).
    """
    X = df.iloc[:, feature_columns].values  # Extract feature columns
    y = np.where(df.iloc[:, target_column] > threshold, 1, 0)  # Binarize target
    return X, y


def build_model(input_dim):
    """
    Build and compile a feedforward neural network.

    :param input_dim: Number of input features.
    :return: Compiled neural network model.
    """
    model = Sequential([
        Dense(16, activation='relu', kernel_regularizer=l2(0.01), input_shape=(input_dim,)),
        Dense(8, activation='relu', kernel_regularizer=l2(0.01)),
        Dense(1, activation='sigmoid')  # Output layer for binary classification
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained neural network on test data.

    :param model: Trained neural network model.
    :param X_test: Test feature matrix.
    :param y_test: Test target vector.
    """
    y_pred = (model.predict(X_test) > 0.5).astype(int)
    print("Accuracy Score:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))


def main():
    # File path to the dataset
    file_path = "seeds_dataset.csv"

    # Load the dataset
    df = load_data(file_path)

    # Define features (all but the last column) and the target column (last column)
    feature_columns = list(range(0, df.shape[1] - 1))  # All columns except the last one
    target_column = df.shape[1] - 1  # The last column
    threshold = 1  # Threshold for binarizing the target column

    # Prepare the data
    X, y = prepare_data(df, feature_columns, target_column, threshold)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Build the neural network
    model = build_model(input_dim=X_train.shape[1])

    # Train the model
    print("Training the neural network...")
    model.fit(X_train, y_train, epochs=50, batch_size=8, verbose=0)

    # Evaluate the model
    print("\nEvaluating the neural network:")
    evaluate_model(model, X_test, y_test)


if __name__ == "__main__":
    main()
