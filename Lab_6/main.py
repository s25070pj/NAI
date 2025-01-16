import cv2
import numpy as np
import os

flags_folder = 'flags'
selected_countries = ['Irlandia', 'Niemcy', 'Francja']

# Mapping country names to flag image file paths
flags_dict = {country: os.path.join(flags_folder, f"{country}.png") for country in selected_countries}


def fetch_flag_image(file_path):
    """
    Fetches an image from the specified file path.

    Args:
        file_path (str): The path to the flag image.

    Returns:
        np.ndarray: The image if successfully loaded, or None if an error occurs.
    """
    try:
        flag_image = cv2.imread(file_path)
        if flag_image is None:
            raise ValueError(f"Unable to read the image from the file: {file_path}")
        return flag_image
    except Exception as e:
        print(f"Error fetching image from {file_path}: {e}")
        return None


def preprocess_image(image):
    """
    Converts the input image from BGR to HSV color space for better color detection.

    Args:
        image (np.ndarray): The input image in BGR format.

    Returns:
        np.ndarray: The image in HSV color space.
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv_image


def match_flag_by_colors(detected_flag_hsv, flag_images):
    """
    Matches the detected flag's color distribution with a list of known flags.

    Args:
        detected_flag_hsv (np.ndarray): The HSV image of the detected flag.
        flag_images (dict): A dictionary where keys are country names and values are flag images.

    Returns:
        str: The country name corresponding to the matched flag, or None if no match is found.
    """
    matched_country = None
    highest_similarity = 0

    for country, flag_image in flag_images.items():
        flag_hsv = cv2.cvtColor(flag_image, cv2.COLOR_BGR2HSV)

        # Calculate histograms in HSV color space
        hist_detected = cv2.calcHist([detected_flag_hsv], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist_flag = cv2.calcHist([flag_hsv], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

        # Normalize histograms
        cv2.normalize(hist_detected, hist_detected)
        cv2.normalize(hist_flag, hist_flag)

        # Compare histograms
        similarity = cv2.compareHist(hist_detected, hist_flag, cv2.HISTCMP_CORREL)

        if similarity > highest_similarity:
            highest_similarity = similarity
            matched_country = country

    return matched_country


def draw_rect_and_name(frame, x, y, w, h, matched_country):
    """
    Draws a rectangle around the detected flag and displays the matched country's name.

    Args:
        frame (np.ndarray): The image frame.
        x (int): The x-coordinate of the top-left corner of the flag.
        y (int): The y-coordinate of the top-left corner of the flag.
        w (int): The width of the flag.
        h (int): The height of the flag.
        matched_country (str): The name of the matched country.

    Returns:
        np.ndarray: The frame with the rectangle and country name drawn.
    """
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display country name
    if matched_country:
        cv2.putText(frame, matched_country, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "No match found", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame


def main():
    """
    Main function that initializes the webcam, captures frames, detects flags, and matches them with predefined flags.

    The program continuously captures frames from the webcam, processes them, detects flags based on color,
    and matches them with a predefined set of flags. The matching flag's country name is displayed on the screen.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Unable to access the camera.")
        return

    # Load flag images from the folder
    flag_images = {name: fetch_flag_image(path) for name, path in flags_dict.items() if fetch_flag_image(path) is not None}
    if not flag_images:
        print("Failed to load any flag images!")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera.")
            break

        hsv_frame = preprocess_image(frame)

        # Find flag contours based on color detection
        lower_bound = np.array([0, 50, 50])  # Lower color bound for colors like white and red
        upper_bound = np.array([180, 255, 255])  # Upper color bound
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)

        # Find contours based on the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the largest contour
        flag_contour = None
        max_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500 and area > max_area:  # Filter small contours
                x, y, w, h = cv2.boundingRect(contour)
                flag_contour = (x, y, w, h)
                max_area = area

        if flag_contour:
            x, y, w, h = flag_contour
            detected_flag_region = frame[y:y + h, x:x + w]
            detected_flag_hsv = preprocess_image(detected_flag_region)

            # Match the detected flag based on color
            matched_country = match_flag_by_colors(detected_flag_hsv, flag_images)

            # Draw rectangle and country name on the frame
            frame = draw_rect_and_name(frame, x, y, w, h, matched_country)

        cv2.imshow("Flag Recognition", frame)

        # Check if the user wants to exit the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
