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
    """
    Pobiera obraz flagi z podanego URL.

    Args:
        url (str): URL obrazu flagi.

    Returns:
        np.ndarray: Obraz flagi jako macierz (lub None, jeśli nie udało się pobrać).
    """
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

def main():
    """
    Główna funkcja programu. Wyświetla flagę na podstawie wybranego kraju.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Nie można uzyskać dostępu do kamerki.")
        return

    # Wybierz przykładowy kraj (możesz dodać logikę dynamicznego wyboru)
    example_country = "Poland"
    flag_url = flags_dict.get(example_country)
    flag_image = fetch_flag_image(flag_url)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Nie udało się odczytać obrazu z kamerki.")
            break

        # Dodaj flagę i nazwę kraju do ramki
        frame = draw_flag_on_frame(frame, flag_image, example_country)

        # Wyświetlenie obrazu
        cv2.imshow("Rozpoznawanie Flag", frame)

        # Wyjście z programu po wciśnięciu klawisza 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()