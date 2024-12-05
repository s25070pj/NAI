from sklearn import svm
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import seaborn as sns

"""
Machine Learning Project: Data Classification with Decision Tree and Support Vector Machine (SVM).

This project focuses on comparing the classification performance of Decision Tree and SVM algorithms using two distinct datasets:  

1. **Marine Fish Dataset**:  
   This dataset contains various features of marine fish, such as their physical and biological characteristics, and the goal is to classify them into different species.  

2. **Seeds Dataset**:  
   This dataset includes measurements of wheat kernels, such as area, perimeter, and compactness, to classify them into three distinct seed varieties.  

The purpose is to evaluate how effectively these algorithms handle classification tasks across diverse datasets with unique feature sets.  

Authors: Adrian Stoltmann, Kacper Tokarzewski
"""



def load_dataset(file_path, columns=None):
    """
    Load a dataset from a local file.

    Parameters:
    file_path (str): Path to the dataset file.
    columns (list, optional): List of column names to assign to the dataset. Default is None.

    Returns:
    DataFrame: A pandas DataFrame containing the dataset.
    """
    return pd.read_csv(file_path, names=columns) if columns else pd.read_csv(file_path)


def prepare_features_and_target(dataframe, target_label):
    """
    Split a dataset into features and target variables.

    Parameters:
    dataframe (DataFrame): The input dataset as a pandas DataFrame.
    target_label (str): The name of the column to be used as the target variable.

    Returns:
    Tuple[DataFrame, Series]: A tuple containing the feature set (X) and target variable (y).
    """
    X = dataframe.drop(columns=[target_label])
    y = dataframe[target_label]
    return X, y


def train_decision_tree_model(features_train, target_train):
    """
    Train a Decision Tree model on the given data.

    Parameters:
    features_train (DataFrame): Training features.
    target_train (Series): Training target labels.

    Returns:
    DecisionTreeClassifier: A trained Decision Tree classifier.
    """
    model = DecisionTreeClassifier()
    model.fit(features_train, target_train)
    return model


def train_svm_model(features_train, target_train):
    """
    Train a Support Vector Machine (SVM) model on the given data.

    Parameters:
    features_train (DataFrame): Training features.
    target_train (Series): Training target labels.

    Returns:
    SVC: A trained SVM classifier.
    """
    model = svm.SVC()
    model.fit(features_train, target_train)
    return model


def assess_model_performance(model, features_test, target_test):
    """
    Evaluate the performance of a trained model.

    Parameters:
    model: The trained machine learning model.
    features_test (DataFrame): Testing features.
    target_test (Series): True labels for the testing data.

    Returns:
    None
    """
    predictions = model.predict(features_test)
    print("Accuracy:", accuracy_score(target_test, predictions))
    print("Classification Report:\n", classification_report(target_test, predictions, zero_division=0))
    print("Confusion Matrix:\n", confusion_matrix(target_test, predictions))


def plot_dataset_histograms(dataframe, numeric_only=True):
    """
    Plot histograms for numeric columns in a dataset.

    Parameters:
    dataframe (DataFrame): The dataset to visualize.
    numeric_only (bool): If True, only numeric columns will be plotted. Default is True.

    Returns:
    None
    """
    if numeric_only:
        dataframe = dataframe.select_dtypes(include=[np.number])
    if dataframe.empty:
        print("No numeric data available for visualization.")
    else:
        dataframe.hist(bins=16, figsize=(15, 10))
        plt.tight_layout()
        plt.show()


def main():
    """
    Main execution function to demonstrate data classification on two datasets
    using Decision Tree and SVM algorithms.
    """
    # Marine Fish Dataset
    fish_dataset_path = "resources/Marine_Fish_Data.csv"
    fish_target_column = "Species_Name"
    fish_data = load_dataset(fish_dataset_path)

    print("=== Processing Marine Fish Dataset ===")
    plot_dataset_histograms(fish_data)

    fish_features, fish_target = prepare_features_and_target(fish_data, fish_target_column)
    X_train_fish, X_test_fish, y_train_fish, y_test_fish = train_test_split(
        fish_features.select_dtypes(include=[np.number]), fish_target, test_size=0.3, random_state=45
    )

    print("\nDecision Tree on Marine Fish Dataset:")
    fish_tree_model = train_decision_tree_model(X_train_fish, y_train_fish)
    assess_model_performance(fish_tree_model, X_test_fish, y_test_fish)

    print("\nSVM on Marine Fish Dataset:")
    fish_svm_model = train_svm_model(X_train_fish, y_train_fish)
    assess_model_performance(fish_svm_model, X_test_fish, y_test_fish)

    # Seeds Dataset
    seeds_dataset_path = "resources/seeds_dataset.csv"
    seeds_column_names = [
        "Area", "Perimeter", "Compactness", "Kernel_Length", "Kernel_Width",
        "Asymmetry_Coeff", "Kernel_Groove", "Class"
    ]
    seeds_target_column = "Class"
    seeds_data = load_dataset(seeds_dataset_path, seeds_column_names)

    print("\n=== Processing Seeds Dataset ===")
    plot_dataset_histograms(seeds_data)

    seeds_features, seeds_target = prepare_features_and_target(seeds_data, seeds_target_column)
    X_train_seeds, X_test_seeds, y_train_seeds, y_test_seeds = train_test_split(
        seeds_features, seeds_target, test_size=0.3, random_state=45
    )

    print("\nDecision Tree on Seeds Dataset:")
    seeds_tree_model = train_decision_tree_model(X_train_seeds, y_train_seeds)
    assess_model_performance(seeds_tree_model, X_test_seeds, y_test_seeds)

    print("\nSVM on Seeds Dataset:")
    seeds_svm_model = train_svm_model(X_train_seeds, y_train_seeds)
    assess_model_performance(seeds_svm_model, X_test_seeds, y_test_seeds)


if __name__ == "__main__":
    main()
