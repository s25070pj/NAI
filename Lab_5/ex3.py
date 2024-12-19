"""
Problem:
- Image Prediction with Neural Networks

Program Overview:
This program classifies images using a convolutional neural network (CNN) trained on the Fashion-MNIST dataset. It involves the following steps:

1. Loading the Fashion-MNIST Dataset:
    - The dataset is loaded and filtered to include specific classes relevant to the classification task.
2. Building and Compiling the CNN Model:
    - The CNN consists of convolutional, pooling, and dense layers for feature extraction and classification.
    - It is compiled using an optimizer, loss function, and evaluation metrics suitable for multiclass classification.
3. Training the Model:
    - The filtered dataset is used to train the CNN.
    - The training process monitors accuracy and loss metrics for evaluation.
4. Saving the Trained Model:
    - The trained model is saved to a file for future use.
5. Preprocessing Custom Images:
    - Custom images are loaded and resized to match the model’s input requirements.
6. Predicting Classes of Custom Images:
    - The trained model predicts the class of input images.

            Authors: Adrian Stoltmann, Kacper Tokarzewski
    """

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.utils import to_categorical
import numpy as np

# List of classes to classify
CLASSES = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat']
IMG_SIZE = 28  # Input image size

def load_fashion_mnist(classes):
    """
    Load the Fashion-MNIST dataset and filter it for specific classes.

    :param classes: List of class names to include in the dataset.
    :return: Filtered training and testing datasets.
    """
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0  # Normalize pixel values

    class_indices = [i for i, cls in enumerate(CLASSES)]
    train_mask = np.isin(y_train, class_indices)
    test_mask = np.isin(y_test, class_indices)

    x_train, y_train = x_train[train_mask], y_train[train_mask]
    x_test, y_test = x_test[test_mask], y_test[test_mask]

    # Remap labels to match the filtered classes
    label_mapping = {old: new for new, old in enumerate(class_indices)}
    y_train = np.array([label_mapping[label] for label in y_train])
    y_test = np.array([label_mapping[label] for label in y_test])

    # Convert labels to one-hot encoding
    y_train = to_categorical(y_train, num_classes=len(classes))
    y_test = to_categorical(y_test, num_classes=len(classes))

    return x_train, y_train, x_test, y_test

def build_model(input_shape, num_classes):
    """
    Build and compile a CNN model for image classification.

    :param input_shape: Shape of the input images.
    :param num_classes: Number of classes to predict.
    :return: Compiled CNN model.
    """
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def preprocess_image(image_path):
    """
    Preprocess a single image for prediction.

    :param image_path: Path to the image file.
    :return: Preprocessed image ready for prediction.
    """
    img = load_img(image_path, color_mode='grayscale', target_size=(IMG_SIZE, IMG_SIZE))
    img_array = img_to_array(img) / 255.0
    return np.expand_dims(img_array, axis=-1)

def main():
    """
    Main workflow for training and evaluating the CNN on Fashion-MNIST.
    """
    print("Loading dataset...")
    x_train, y_train, x_test, y_test = load_fashion_mnist(CLASSES)
    print(f"Dataset loaded! Classes: {CLASSES}")

    # Expand dimensions for grayscale images
    x_train = np.expand_dims(x_train, axis=-1)
    x_test = np.expand_dims(x_test, axis=-1)

    print("Building the model...")
    model = build_model(x_train.shape[1:], len(CLASSES))

    print("Training the model...")
    model.fit(x_train, y_train, epochs=10, batch_size=64, validation_data=(x_test, y_test))

    model.save('fashion_mnist_model.h5')
    print("Model saved as 'fashion_mnist_model.h5'.")

    print("Preprocessing custom images...")
    tshirt_image = preprocess_image('tshirt.png')
    dress_image = preprocess_image('dress.png')

    print("Predicting custom images...")
    tshirt_prediction = model.predict(np.expand_dims(tshirt_image, axis=0))
    dress_prediction = model.predict(np.expand_dims(dress_image, axis=0))

    tshirt_class = CLASSES[np.argmax(tshirt_prediction)]
    dress_class = CLASSES[np.argmax(dress_prediction)]

    print(f"tshirt.png identified as: {tshirt_class}")
    print(f"dress.png identified as: {dress_class}")

if __name__ == "__main__":
    main()
