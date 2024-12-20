"""
Problem:
- Image Classification with Neural Networks

Description:
This program uses a convolutional neural network (CNN) to classify images.
It processes the Fruit-360 dataset, trains a model, and evaluates its performance.

Workflow:
1. Load and preprocess the Fruit-360 dataset.
2. Build and compile a CNN model for classification.
3. Train the model on the dataset.
4. Save the trained model to a file.
5. Load and preprocess custom images for prediction.
6. Use the model to classify custom images and display results.

Authors: Adrian Stoltmann, Kacper Tokarzewski
"""

import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = 64
BATCH_SIZE = 32

def load_data(data_dir):
    """
    Load and preprocess the Fruit-360 dataset.

    :param data_dir: Path to the dataset directory.
    :return: Tuple of (x_train, y_train, x_test, y_test) and the class names.
    """
    train_dir = os.path.join(data_dir, "Training")
    test_dir = os.path.join(data_dir, "Test")

    datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_generator = datagen.flow_from_directory(
        train_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    test_generator = datagen.flow_from_directory(
        test_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    x_train, y_train = zip(*[(x, y) for x, y in train_generator])
    x_test, y_test = zip(*[(x, y) for x, y in test_generator])

    x_train = np.concatenate(x_train)
    y_train = np.concatenate(y_train)
    x_test = np.concatenate(x_test)
    y_test = np.concatenate(y_test)

    class_names = list(train_generator.class_indices.keys())

    return x_train, y_train, x_test, y_test, class_names

def build_model(input_shape, num_classes):
    """
    Build and compile a CNN model for image classification.

    :param input_shape: The shape of the input images.
    :param num_classes: The number of classes to predict.
    :return: The compiled model.
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

    :param image_path: The path to the image file.
    :return: The preprocessed image.
    """
    img = load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = img_to_array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

def main():
    """
    Train the model on Fruit-360 and use it to predict custom images.
    """
    data_dir = "fruits-360"
    print("Loading data...")
    x_train, y_train, x_test, y_test, class_names = load_data(data_dir)
    print(f"Dataset loaded! Classes: {class_names}")

    print("Building model...")
    model = build_model(x_train.shape[1:], len(class_names))

    print("Training the model...")
    model.fit(x_train, y_train, epochs=10, batch_size=64, validation_data=(x_test, y_test))

    model.save('fruit_classifier.h5')
    print("Model saved successfully as 'fruit_classifier.h5'.")

    print("Loading and preprocessing images...")
    apple_image = preprocess_image('apple.jpg')
    banana_image = preprocess_image('banana.jpg')

    print("Predicting images...")
    apple_prediction = model.predict(apple_image)
    banana_prediction = model.predict(banana_image)

    apple_class = class_names[np.argmax(apple_prediction)]
    banana_class = class_names[np.argmax(banana_prediction)]

    print(f"apple.jpg was classified as: {apple_class}")
    print(f"banana.jpg was classified as: {banana_class}")

if __name__ == "__main__":
    main()
