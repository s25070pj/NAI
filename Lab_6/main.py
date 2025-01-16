import cv2
import numpy as np
import pandas as pd
import urllib.request

# Wczytanie danych z pliku CSV
file_path = '/mnt/data/flags.csv'
flags_data = pd.read_csv(file_path, sep=';')

# Mapowanie nazw krajów do linków z obrazami flag
flags_dict = dict(zip(flags_data['name'], flags_data['image']))

def fetch_flag_image(url):
    try:
        with urllib.request.urlopen(url) as response:
            image_data = np.asarray(bytearray(response.read()), dtype="uint8")
            flag_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            return flag_image
    except Exception as e:
        print(f"Nie udało się pobrać obrazu z {url}: {e}")
        return None

def draw_flag_on_frame(frame, flag, country_name):
    """
    Wyświetla flagę i nazwę kraju na ramce obrazu.

    Args:
        frame (np.ndarray): Główna ramka z kamerki.
        flag (np.ndarray): Obraz flagi.
        country_name (str): Nazwa kraju.

    Returns:
        np.ndarray: Ramka obrazu z dodaną flagą i nazwą kraju.
    """
    if flag is not None:
        # Skalowanie flagi
        flag_height, flag_width = flag.shape[:2]
        scale_factor = 100 / flag_height  # Ustaw flagę na wysokość 100 px
        flag_resized = cv2.resize(flag, (int(flag_width * scale_factor), 100))

        # Wklejenie flagi w lewym górnym rogu
        frame[10:10+flag_resized.shape[0], 10:10+flag_resized.shape[1]] = flag_resized

    # Dodanie nazwy kraju
    cv2.putText(
        frame, country_name, (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )

    return frame

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    return edged


def find_flag_contour(frame):
    edged = preprocess_image(frame)
    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    flag_contour = None
    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500 and area > max_area:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            if 0.8 < aspect_ratio < 1.2:  # Przyjmujemy, że flaga jest mniej więcej kwadratowa
                flag_contour = (x, y, w, h)
                max_area = area
    return flag_contour


def match_flag(detected_flag, flag_images):
    min_diff = float('inf')
    matched_country = None
    for country, flag_image in flag_images.items():
        resized_flag = cv2.resize(detected_flag, (flag_image.shape[1], flag_image.shape[0]))
        diff = cv2.absdiff(flag_image, resized_flag)
        diff_sum = np.sum(diff)
        if diff_sum < min_diff:
            min_diff = diff_sum
            matched_country = country
    return matched_country


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Nie można uzyskać dostępu do kamerki.")
        return

    # Pobranie wszystkich obrazów flag
    flag_images = {name: fetch_flag_image(url) for name, url in flags_dict.items() if fetch_flag_image(url) is not None}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Nie udało się odczytać obrazu z kamerki.")
            break

        flag_contour = find_flag_contour(frame)
        if flag_contour is not None:
            x, y, w, h = flag_contour
            detected_flag = frame[y:y+h, x:x+w]

            matched_country = match_flag(detected_flag, flag_images)
            if matched_country:
                draw_flag_on_frame(frame, detected_flag, matched_country)

        cv2.imshow("Rozpoznawanie Flag", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
