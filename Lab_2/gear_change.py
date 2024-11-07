import sys
from fuzzylogic.classes import Domain, Set, Rule
from fuzzylogic.functions import R, S, triangular, trapezoid

"""
This implementation uses fuzzy logic to determine the recommended gear for a vehicle 
based on its speed, engine load, and throttle position. By using fuzzy sets and rules, 
this system provides flexible decision-making for choosing the optimal gear, which can 
aid in smoother driving and improve fuel efficiency. Fuzzy logic enables the system to 
handle continuous data and gradual transitions rather than rigid, rule-based thresholds.

Key variables:
    - speed (Domain): Defines the range and fuzzy sets for vehicle speed.
    - engine_load (Domain): Defines the range and fuzzy sets for engine load.
    - throttle_position (Domain): Defines the range and fuzzy sets for throttle position.
    - gear (Domain): Defines the range and fuzzy sets representing gears (1-5).
    - rules (list of Rule): Contains the fuzzy logic rules mapping speed, engine load, 
      and throttle position to a recommended gear.

Each rule evaluates the current conditions and determines the gear that most closely 
matches the given inputs based on fuzzy membership values.
"""

speed = Domain("speed", 0, 250)
engine_load = Domain("engine_load", 0, 100)
throttle_position = Domain("throttle_position", 0, 100)
gear = Domain("gear", 1, 5)

speed.slow = trapezoid(0, 5, 20, 40)
speed.medium = triangular(40, 90)
speed.fast = trapezoid(70, 90, 240, 250)

engine_load.low = trapezoid(0, 5, 20, 40)
engine_load.medium = triangular(30, 70)
engine_load.high = trapezoid(60, 80, 95, 100)

throttle_position.low = trapezoid(0, 5, 20, 40)
throttle_position.medium = triangular(20, 70)
throttle_position.high = trapezoid(60, 80, 95, 100)

gear.first = Set(R(0, 10))
gear.second = Set(S(5, 30)) & Set(R(30, 45))
gear.third = Set(S(25, 50)) & Set(R(50, 65))
gear.fourth = Set(S(45, 70)) & Set(R(65, 85))
gear.fifth = Set(S(75, 90))

rules = [
    Rule({(speed.slow, engine_load.low, throttle_position.low): gear.first}),
    Rule({(speed.slow, engine_load.medium, throttle_position.low): gear.first}),
    Rule({(speed.slow, engine_load.medium, throttle_position.medium): gear.second}),
    Rule({(speed.slow, engine_load.high, throttle_position.medium): gear.third}),
    Rule({(speed.slow, engine_load.high, throttle_position.high): gear.third}),
    Rule({(speed.medium, engine_load.low, throttle_position.medium): gear.third}),
    Rule({(speed.medium, engine_load.medium, throttle_position.medium): gear.fourth}),
    Rule({(speed.medium, engine_load.medium, throttle_position.high): gear.fourth}),
    Rule({(speed.medium, engine_load.high, throttle_position.high): gear.fourth}),
    Rule({(speed.medium, engine_load.high, throttle_position.medium): gear.fourth}),
    Rule({(speed.fast, engine_load.medium, throttle_position.medium): gear.fifth}),
    Rule({(speed.fast, engine_load.high, throttle_position.high): gear.fifth}),
]

def calculate_gear(current_speed, current_engine_load, current_throttle_position):
    """
    Determines the recommended gear based on current speed, engine load, and throttle position.

    This function uses a set of fuzzy logic rules to calculate the degree of membership
    for each possible gear (1-5). Based on these memberships, the gear with the highest
    combined membership value is chosen as the recommended gear.

    Parameters:
        current_speed (float): The vehicle's current speed in km/h.
        current_engine_load (float): The current engine load as a percentage (0-100).
        current_throttle_position (float): The current throttle position as a percentage (0-100).

    Returns:
        Domain: The gear with the highest membership degree according to the fuzzy logic rules.

    Variables:
        gear_memberships (dict): Stores the calculated membership value for each gear.
        rule (Rule): Each fuzzy rule applied to the input conditions.
        condition (tuple): The conditions in a rule (speed, engine load, throttle position).
        target_gear (Set): The gear suggested by the rule.
        combined_membership (float): The highest membership value for the evaluated conditions.

    Example usage:
        calculate_gear(45, 60, 30)  # Returns a recommended gear based on fuzzy logic.
    """
    gear_memberships = {}

    for rule in rules:
        condition, target_gear = list(rule.conditions.items())[0]
        speed_condition, load_condition, throttle_condition = condition

        speed_membership = speed_condition(current_speed)
        load_membership = load_condition(current_engine_load)
        throttle_membership = throttle_condition(current_throttle_position)

        combined_membership = max(speed_membership, load_membership, throttle_membership)

        if target_gear not in gear_memberships:
            gear_memberships[target_gear] = combined_membership
        else:
            gear_memberships[target_gear] = max(gear_memberships[target_gear], combined_membership)

    print(
        f"Speed: {current_speed}, Membership in slow: {speed.slow(current_speed)}, "
        f"medium: {speed.medium(current_speed)}, fast: {speed.fast(current_speed)}"
    )
    print(
        f"Engine load: {current_engine_load}, Membership in low: {engine_load.low(current_engine_load)}, "
        f"medium: {engine_load.medium(current_engine_load)}, high: {engine_load.high(current_engine_load)}"
    )
    print(
        f"Throttle position: {current_throttle_position}, Membership in low: "
        f"{throttle_position.low(current_throttle_position)}, "
        f"medium: {throttle_position.medium(current_throttle_position)}, "
        f"high: {throttle_position.high(current_throttle_position)}"
    )

    selected_gear = max(gear_memberships, key=gear_memberships.get)
    return selected_gear

if __name__ == "__main__":
    """
    Main entry point for calculating the gear recommendation based on user input.

    Accepts three command-line arguments for speed, engine load, and throttle position.
    Calls calculate_gear() to compute and print the recommended gear.

    Usage:
        python <script_name>.py <speed> <engine_load> <throttle_position>

    Example:
        python <script_name>.py 30 75 60
    """
    if len(sys.argv) != 4:
        print("Usage: python <script_name>.py <speed> <engine_load> <throttle_position>")
        print("Example: python <script_name>.py 30 75 60")
        sys.exit(1)

    try:
        current_speed = float(sys.argv[1])
        current_engine_load = float(sys.argv[2])
        current_throttle_position = float(sys.argv[3])

        gear_selected = calculate_gear(current_speed, current_engine_load, current_throttle_position)
        print(
            f"For speed {current_speed} km/h, engine load {current_engine_load}% "
            f"and throttle position {current_throttle_position}%, the recommended gear is: {gear_selected}"
        )
    except ValueError:
        print("Please enter valid numeric input values.")
