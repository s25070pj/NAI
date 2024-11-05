from fuzzylogic.classes import Domain, Set, Rule
from fuzzylogic.functions import R, S

# Definiujemy domeny
speed = Domain("speed", 0, 250)
engine_load = Domain("engine_load", 0, 100)
throttle_position = Domain("throttle_position", 0, 100)
gear = Domain("gear", 1, 5)

# Określamy zbiory rozmyte dla prędkości
speed.slow = Set(R(0, 20)) & Set(S(10, 30))
speed.medium = Set(R(20, 80)) & Set(S(60, 100))
speed.fast = R(75, 250)

# Określamy zbiory rozmyte dla obciążenia silnika
engine_load.low = S(0, 30)  # Zakres dla low
engine_load.medium = Set(R(20, 60)) & Set(S(50, 75))
engine_load.high = R(60, 100)

# Określamy zbiory rozmyte dla pozycji przepustnicy
throttle_position.low = R(0, 30)  # Zakres dla low
throttle_position.medium = Set(S(20, 55)) & Set(R(50, 75))
throttle_position.high = R(60, 100)

# Definiujemy zbiory rozmyte dla biegów
gear.first = Set(R(0, 10))
gear.second = Set(S(5, 30)) & Set(R(30, 45))
gear.third = Set(S(25, 50)) & Set(R(50, 65))
gear.fourth = Set(S(45, 70)) & Set(R(65, 85))
gear.fifth = Set(S(75, 90))

# Definiujemy reguły logiki rozmytej jako funkcje
rules = [
    Rule({(speed.slow, engine_load.low, throttle_position.low): gear.first}),
    Rule({(speed.slow, engine_load.medium, throttle_position.medium): gear.second}),
    Rule({(speed.medium, engine_load.medium, throttle_position.medium): gear.third}),
    Rule({(speed.medium, engine_load.medium, throttle_position.high): gear.fourth}),
    Rule({(speed.slow, engine_load.high, throttle_position.high): gear.second}),
    Rule({(speed.medium, engine_load.high, throttle_position.medium): gear.third}),
    Rule({(speed.medium, engine_load.high, throttle_position.medium): gear.fourth}),
    Rule({(speed.fast, engine_load.high, throttle_position.high): gear.fifth}),
]

# Funkcja do wyliczenia biegu na podstawie prędkości, obciążenia silnika i pozycji przepustnicy
def calculate_gear(current_speed, current_engine_load, current_throttle_position):
    gear_memberships = {}

    # Przetwarzamy każdą regułę i obliczamy stopień przynależności do biegu
    for rule in rules:
        condition, target_gear = list(rule.conditions.items())[0]
        speed_condition, load_condition, throttle_condition = condition

        # Obliczamy wartość przynależności dla każdej zmiennej
        speed_membership = speed_condition(current_speed)
        load_membership = load_condition(current_engine_load)
        throttle_membership = throttle_condition(current_throttle_position)

        # Wyświetlanie przynależności dla diagnostyki
        print(f"Prędkość: {current_speed}, Przynależność do slow: {speed_membership}, medium: {speed_membership}, fast: {speed.fast(current_speed)}")
        print(f"Obciążenie silnika: {current_engine_load}, Przynależność do low: {load_membership}, medium: {load_membership}, high: {engine_load.high(current_engine_load)}")
        print(f"Pozycja przepustnicy: {current_throttle_position}, Przynależność do low: {throttle_membership}, medium: {throttle_position.medium(current_throttle_position)}, high: {throttle_position.high(current_throttle_position)}")

        # Łączymy przynależności przez min (reguła AND) i zapisujemy w słowniku przynależności
        combined_membership = min(speed_membership, load_membership, throttle_membership)

        # Jeśli bieg już istnieje, wybieramy maksymalną wartość przynależności (logika rozmyta OR)
        if target_gear not in gear_memberships:
            gear_memberships[target_gear] = combined_membership
        else:
            gear_memberships[target_gear] = max(gear_memberships[target_gear], combined_membership)

    # Wyznaczamy bieg o najwyższym stopniu przynależności
    selected_gear = max(gear_memberships, key=gear_memberships.get)
    return selected_gear

# Przykładowe wywołanie funkcji
current_speed = 44
current_engine_load = 75
current_throttle_position = 80
gear_selected = calculate_gear(current_speed, current_engine_load, current_throttle_position)

print(
    f"Dla prędkości {current_speed} km/h, obciążenia silnika {current_engine_load}% oraz pozycji przepustnicy {current_throttle_position}% zalecany bieg to: {gear_selected}")
