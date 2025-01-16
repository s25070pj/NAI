
# Flag Recognition using Webcam

This project is a real-time flag recognition system that uses a webcam to detect and identify flags from a predefined set of countries. The program uses color detection and histogram comparison techniques to match a detected flag with images of known flags.


## Prerequisites

Before running the project, ensure you have the following libraries installed:

- **OpenCV**: For image processing and webcam handling.
- **NumPy**: For handling arrays and mathematical operations.

You can install the necessary dependencies using `pip`:

```bash
pip install opencv-python numpy
```

## Running the Program

1. Place your flag images (e.g., `Irlandia.png`, `Niemcy.png`, `Francja.png`) in the `flags` folder.
2. Run the Python script:

```bash
python main.py
```

3. The program will use the webcam to detect flags in real-time. It will show a rectangle around any detected flag and display the corresponding country's name on the image.

4. To exit the program, press the 'q' key.

## How It Works

- **Color Detection**: The program uses color ranges in the HSV color space to detect flag-like regions in the camera frame.
- **Flag Matching**: After detecting a flag, the program compares its color histogram to predefined flag histograms to determine the country.
- **Drawing**: If a match is found, the country name is displayed on the frame, and a rectangle is drawn around the flag.

# Authors
- Kacper Tokarzewski
- Adrian Stoltmann