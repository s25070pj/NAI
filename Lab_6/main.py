import cv2
import numpy as np
import os

# Folder z lokalnymi obrazami flag
flags_folder = 'flags'

# Lista przykładowych krajów
selected_countries = ['Polska', 'Niemcy', 'Francja']

# Mapowanie nazw krajów do ścieżek obrazów flag
flags_dict = {country: os.path.join(flags_folder, f"{country}.png") for country in selected_countries}


def fetch_flag_image(file_path):
    try:
        flag_image = cv2.imread(file_path)
        if flag_image is None:
            raise ValueError("Nie udało się odczytać obrazu z pliku")
        return flag_image
    except Exception as e:
        print(f"Nie udało się pobrać obrazu z {file_path}: {e}")
        return None


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
            if 0.8 < aspect_ratio < 1.2:
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


def draw_flag_on_frame(frame, flag, country_name):
    if flag is not None:
        flag_height, flag_width = flag.shape[:2]
        scale_factor = 100 / flag_height
        flag_resized = cv2.resize(flag, (int(flag_width * scale_factor), 100))
        frame[10:10+flag_resized.shape[0], 10:10+flag_resized.shape[1]] = flag_resized

    cv2.putText(
        frame, country_name, (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )
    return frame


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Nie można uzyskać dostępu do kamerki.")
        return

    flag_images = {name: fetch_flag_image(path) for name, path in flags_dict.items() if fetch_flag_image(path) is not None}

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
                frame = draw_flag_on_frame(frame, detected_flag, matched_country)

        cv2.imshow("Rozpoznawanie Flag", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
