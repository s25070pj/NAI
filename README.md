# Quoridor - Python Game

## Game Instructions

### Pawn Movements:
- A player can move their pawn by one square in any direction (up, down, left, or right).

### Placing Walls:
- Players can place walls to block their opponent. Each player has a limited number of walls.

### Objective of the Game:
- Win by moving your pawn to the opposite side of the board.
---

## Authors
- Adrian Stoltmann, Kacper Tokarzewski

---

## Project Description
Quoridor is a strategic board game where two players attempt to move their pawn across the board while placing walls to block their opponent's path. This Python
implementation includes a playable game with basic AI using a Negamax algorithm.

---

## Environment Setup Instructions

### Prerequisites
Before you can run the project, make sure you have the following installed on your system:
- Python 3.x
- `pygame` library

### Installation

1. **Clone the repository:**

   git clone https://github.com/your-repo/quoridor-game.git
   cd quoridor-game

1.   ***Create a virtual environment (optional but recommended):***

  python -m venv venv
  source venv/bin/activate  # On Windows use: venv\Scripts\activate
  
3. ***Install the required dependencies:***

  pip install pygame
  pip install easyai

  
4.  ***Run the game:***

  python main.py

5.  ***Gameplay:***

  Left-click to move your pawn.
  Right-click to place walls (if available).
  The first player to reach the opponent's side of the board wins.

  ![image](https://github.com/user-attachments/assets/9c68a6a7-c2a7-47ca-aa65-422cb53b3472)

