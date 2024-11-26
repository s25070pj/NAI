from sklearn import svm, metrics
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA


def load_data():
    """Load CSV data into Pandas objects and split it into training and test sets."""
    seeds_df = pd.read_csv('seeds_dataset.csv')
    x = seeds_df.iloc[:, :-1]
    y = seeds_df.iloc[:, -1]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=109)
    return x_train, x_test, y_train, y_test


def visualize_data(x_train, y_train):
    pca = PCA(n_components=2)  # Reduce to 2 dimensions for visualization
    x_train_pca = pca.fit_transform(x_train)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=x_train_pca[:, 0], y=x_train_pca[:, 1], hue=y_train, palette='viridis', s=100)
    plt.title("Data classification")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend(title="Class")
    plt.show()


if __name__ == '__main__':
    x_train, x_test, y_train, y_test = load_data()

    svm_model = svm.SVC(kernel='linear')
    svm_model.fit(x_train, y_train)
    svm_pred = svm_model.predict(x_test)

    dt_model = DecisionTreeClassifier(random_state=109)
    dt_model.fit(x_train, y_train)
    dt_pred = dt_model.predict(x_test)

    print("SVM classifier")
    print("Accuracy:",metrics.accuracy_score(y_test, svm_pred))
    print("Precision:",metrics.precision_score(y_test, svm_pred, average='macro'))
    print("Recall:",metrics.recall_score(y_test, svm_pred, average='macro'))

    print("\nDecision Tree classifier")
    print("Accuracy: ",metrics.accuracy_score(y_test, dt_pred))
    print("Precision: ",metrics.precision_score(y_test, dt_pred, average='macro'))
    print("Recall: ",metrics.recall_score(y_test, dt_pred, average='macro'))

    visualize_data(x_train, y_train)
