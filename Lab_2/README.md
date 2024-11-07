# System Doboru Biegów z Logiką Rozmytą

## Opis
Ten projekt wykorzystuje logikę rozmytą do wyznaczania zalecanego biegu na podstawie prędkości samochodu, obciążenia silnika oraz pozycji przepustnicy. System korzysta z funkcji trapezoidalnych i trójkątnych do definiowania zbiorów rozmytych.

## Wymagania
- Python 3.x
- Biblioteka `fuzzylogic`

Aby zainstalować bibliotekę `fuzzylogic`, użyj następującego polecenia:
```bash
pip install fuzzylogic
```
## Sposób użycia
Uruchom skrypt podając trzy parametry:
- Prędkość (w km/h, od 0 do 250)
- Obciążenie silnika (w procentach, od 0 do 100)
- Pozycję przepustnicy (w procentach, od 0 do 100)

Przykład:
```bash
python nazwa_pliku.py 30 75 60