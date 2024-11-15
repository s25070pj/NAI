import heapq

import pygame
import sys

from collections import deque
from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax

pygame.init()

current_turn = 0
MAX_WALLS = 10
SCREEN_WIDTH, SCREEN_HEIGHT = 720, 720
GRID_SIZE = 9
SQUARE_SIZE = SCREEN_WIDTH // GRID_SIZE
LINE_COLOR = (0, 0, 0)
BACKGROUND_COLOR = (255, 255, 255)
PAWN_COLOR = [(255, 0, 0), (0, 0, 255)]  # Red for player1, Blue for player2
WALL_COLOR = (0, 255, 0)
HIGHLIGHT_COLOR = (128, 128, 128)
MOVE_DOT_COLOR = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Quoridor")
font = pygame.font.SysFont(None, 36)

player1_pos = [4, 0]
player2_pos = [4, 8]
pawns = [player1_pos, player2_pos]
walls = {"VERTICAL": [], "HORIZONTAL": []}
wall_counts = [MAX_WALLS, MAX_WALLS]

game_over = False


def draw_grid():
    """
       Draw the grid for the Quoridor game.
       The grid is a 9x9 board where players can move their pawns.
       """
    screen.fill(BACKGROUND_COLOR)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)


def draw_walls():
    """
      Draw the vertical and horizontal walls on the board.
      Walls are placed by players to block their opponent's movement.
      """
    for wall in walls["VERTICAL"]:
        pygame.draw.rect(screen, WALL_COLOR, wall)
    for wall in walls["HORIZONTAL"]:
        pygame.draw.rect(screen, WALL_COLOR, wall)


def is_wall_blocking(x, y, direction):
    """
      Check if a wall is blocking the path in the specified direction.

      Parameters:
      x (int): X-coordinate of the pawn.
      y (int): Y-coordinate of the pawn.
      direction (str): Direction to check ('UP', 'DOWN', 'LEFT', 'RIGHT').

      Returns:
      bool: True if a wall blocks the path in the specified direction, False otherwise.
      """
    if direction == 'UP':
        return any(wall.colliderect(pygame.Rect(x * SQUARE_SIZE, (y - 1) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                   for wall in walls["HORIZONTAL"])
    elif direction == 'DOWN':
        return any(wall.colliderect(pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                   for wall in walls["HORIZONTAL"])
    elif direction == 'LEFT':
        return any(wall.colliderect(pygame.Rect((x - 1) * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                   for wall in walls["VERTICAL"])
    elif direction == 'RIGHT':
        return any(wall.colliderect(pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                   for wall in walls["VERTICAL"])


def draw_win_message(message):
    """
      Display a win message when a player wins the game.

      Parameters:
      message (str): The message to be displayed on the screen.
      """
    font = pygame.font.SysFont(None, 48)
    text = font.render(message, True, (0, 255, 0))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))


def draw_wall_counters():
    """
       Display the number of walls remaining for both players on the screen.
       """
    text_p1 = font.render(f"Player 1 walls: {wall_counts[0]}", True, PAWN_COLOR[0])
    text_p2 = font.render(f"Player 2 walls: {wall_counts[1]}", True, PAWN_COLOR[1])
    screen.blit(text_p1, (20, SCREEN_HEIGHT - 40))
    screen.blit(text_p2, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40))


class QuoridorGame(TwoPlayerGame):
    """
      The QuoridorGame class represents the Quoridor game logic, extending the TwoPlayerGame from easyAI.
      """

    def __init__(self, players):
        """
              Initialize the game with a list of players and set up the initial board state.

              Parameters:
              players (list): List of Human_Player or AI_Player instances.
              """
        self.players = players
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        self.pawns = [[4, 0], [4, 8]]  # Starting positions for player 1 and player 2
        self.walls = {"VERTICAL": [], "HORIZONTAL": []}
        self.previous_position = [[], []]
        self.current_turn = current_turn

        self.current_player = 1

    def switch_turn(self):
        """
                Switch to the next player's turn.
                """
        self.current_turn = 1 - self.current_turn
        global current_turn
        current_turn = self.current_turn

    def draw_pawns(self):
        """
               Draw the players' pawns on the board.
               """
        for i, pawn in enumerate(self.pawns):
            x = pawn[0] * SQUARE_SIZE + SQUARE_SIZE // 2
            y = pawn[1] * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(screen, PAWN_COLOR[i], (x, y), SQUARE_SIZE // 3)

    def is_move_blocked(self, start, end):
        """
                Check if a move from the start position to the end position is blocked by any walls.

                Parameters:
                start (list): Starting position of the pawn.
                end (list): Ending position of the pawn.

                Returns:
                bool: True if the move is blocked, False otherwise.
                """
        x1, y1 = start
        x2, y2 = end

        if x1 == x2:
            if y2 > y1:
                for wall in walls["HORIZONTAL"]:
                    if wall.collidepoint(x1 * SQUARE_SIZE + SQUARE_SIZE // 2, (y1 + 1) * SQUARE_SIZE):
                        return True
            elif y2 < y1:
                for wall in walls["HORIZONTAL"]:
                    if wall.collidepoint(x1 * SQUARE_SIZE + SQUARE_SIZE // 2, y1 * SQUARE_SIZE):
                        return True
        elif y1 == y2:
            if x2 > x1:
                for wall in walls["VERTICAL"]:
                    if wall.collidepoint((x1 + 1) * SQUARE_SIZE, y1 * SQUARE_SIZE + SQUARE_SIZE // 2):
                        return True
            elif x2 < x1:
                for wall in walls["VERTICAL"]:
                    if wall.collidepoint(x1 * SQUARE_SIZE, y1 * SQUARE_SIZE + SQUARE_SIZE // 2):
                        return True
        return False

    def available_moves_from_position(self, current_position):
        """
            Get a list of available moves from the given position.

            Parameters:
            current_position (list): The current position of the pawn.

            Returns:
            list: A list of valid moves (positions) that the pawn can move to.
            """
        moves = []

        if current_position[1] > 0 and not self.is_move_blocked(current_position,
                                                                [current_position[0], current_position[1] - 1]):  # Góra
            moves.append([current_position[0], current_position[1] - 1])
        if current_position[1] < GRID_SIZE - 1 and not self.is_move_blocked(current_position, [current_position[0],
                                                                                               current_position[
                                                                                                   1] + 1]):  # Dół
            moves.append([current_position[0], current_position[1] + 1])
        if current_position[0] > 0 and not self.is_move_blocked(current_position,
                                                                [current_position[0] - 1, current_position[1]]):  # Lewo
            moves.append([current_position[0] - 1, current_position[1]])
        if current_position[0] < GRID_SIZE - 1 and not self.is_move_blocked(current_position, [current_position[0] + 1,
                                                                                               current_position[
                                                                                                   1]]):  # Prawo
            moves.append([current_position[0] + 1, current_position[1]])

        return moves

    def bfs(self, start_pos, goal_row):
        """
               Use breadth-first search (BFS) to check if there is a valid path from start_pos to goal_row.

               Parameters:
               start_pos (list): The starting position of the pawn.
               goal_row (int): The row to reach (8 for Player 1, 0 for Player 2).

               Returns:
               bool: True if there is a path to the goal row, False otherwise.
               """
        queue = deque([start_pos])
        visited = set()
        visited.add(tuple(start_pos))

        while queue:
            x, y = queue.popleft()

            if y == goal_row:
                return True

            for move in self.available_moves_from_position([x, y]):
                if tuple(move) not in visited:
                    visited.add(tuple(move))
                    queue.append(move)

        return False

    def bfs_shortest_path(self, start, goal_row, walls=None):
        """
               Find the shortest path from start to the goal_row using BFS.

               Parameters:
               start (list): The starting position of the pawn.
               goal_row (int): The row to reach.
               walls (dict): Optional parameter for walls configuration.

               Returns:
               int: The shortest distance to the goal_row, or infinity if no path exists.
               """
        """Find the shortest path from start to goal_row using BFS"""
        if walls is None:
            walls = self.walls

        queue = [(0, start)]  # (distance, position)
        visited = set()
        while queue:
            (dist, current) = heapq.heappop(queue)
            if current[1] == goal_row:
                return dist
            if tuple(current) in visited:
                continue
            visited.add(tuple(current))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                x, y = current[0] + dx, current[1] + dy
                if (0 <= x < GRID_SIZE) and (0 <= y < GRID_SIZE):
                    if not is_wall_blocking(x, y,
                                            'LEFT' if dx == -1 else 'RIGHT' if dx == 1 else 'UP' if dy == -1 else 'DOWN'):
                        heapq.heappush(queue, (dist + 1, (x, y)))

        return float('inf')

    def is_path_to_goal(self):
        """
         Check if both players have a valid path to their respective goal rows.

         Returns:
         bool: True if both players can reach their goal row without being blocked, False otherwise.
         """
        if not self.bfs(pawns[0], GRID_SIZE - 1):
            return False

        if not self.bfs(pawns[1], 0):
            return False

        return True

    def is_wall_valid(self, wall, orientation):
        """
          Check if a wall placement is valid based on several criteria:
          1. Wall must be within the grid boundaries.
          2. Wall must not intersect with existing walls of the same orientation.
          3. Wall must not intersect with walls of the opposite orientation.
          4. Wall must not block all paths to the goal for either player.

          Parameters:
          wall (pygame.Rect): The wall to be placed.
          orientation (str): The orientation of the wall ('VERTICAL' or 'HORIZONTAL').

          Returns:
          bool: True if the wall placement is valid, False otherwise.
          """
        grid_width = GRID_SIZE - 1
        grid_height = GRID_SIZE - 1

        if orientation == "VERTICAL":
            if wall.x < 0 or wall.x > grid_width * SQUARE_SIZE or wall.y < 0 or wall.y > grid_height * SQUARE_SIZE:
                return False
        elif orientation == "HORIZONTAL":
            if wall.x < 0 or wall.x > grid_width * SQUARE_SIZE or wall.y < 0 or wall.y > grid_height * SQUARE_SIZE:
                return False

        for existing_wall in walls[orientation]:
            if wall.colliderect(existing_wall):
                return False

        # Check for intersections with walls of the opposite orientation
        opposite_orientation = "HORIZONTAL" if orientation == "VERTICAL" else "VERTICAL"
        for opposite_wall in walls[opposite_orientation]:
            if wall.colliderect(opposite_wall):
                return False

        # Check if placing the wall blocks all paths to the goal
        walls[orientation].append(wall)
        path_valid = self.is_path_to_goal()
        walls[orientation].remove(wall)

        if not path_valid:
            return False

        return True

    def highlight_wall(self, mouse_pos):
        """
         Highlight a potential wall placement based on the mouse position.

         Parameters:
         mouse_pos (tuple): The (x, y) coordinates of the mouse cursor.

         This function draws a highlighted wall on the screen if the proposed
         wall placement is valid according to the game rules.
         """
        x, y = mouse_pos
        grid_x = x // SQUARE_SIZE
        grid_y = y // SQUARE_SIZE
        margin = 10

        if abs(x % SQUARE_SIZE) < margin:
            wall = pygame.Rect(grid_x * SQUARE_SIZE - SQUARE_SIZE // 8, grid_y * SQUARE_SIZE, SQUARE_SIZE // 4,
                               SQUARE_SIZE * 2)
            if self.is_wall_valid(wall, "VERTICAL"):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, wall)
        elif abs(y % SQUARE_SIZE) < margin:
            wall = pygame.Rect(grid_x * SQUARE_SIZE, grid_y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2,
                               SQUARE_SIZE // 4)
            if self.is_wall_valid(wall, "HORIZONTAL"):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, wall)

    def possible_moves(self):
        """
              Get the list of possible moves for the current player.

              Returns:
              list: A list of valid moves for the current player.
              """
        moves = []

        current_pawn_pos = self.pawns[self.current_turn]
        pawn_moves = self.available_moves_from_position(current_pawn_pos)
        for move in pawn_moves:
            moves.append(('MOVE', move))

        if wall_counts[self.current_turn] > 0:
            for x in range(max(0, current_pawn_pos[0] - 1), min(GRID_SIZE - 1, current_pawn_pos[0] + 1)):
                for y in range(max(0, current_pawn_pos[1] - 1), min(GRID_SIZE - 1, current_pawn_pos[1] + 1)):
                    vertical_wall = pygame.Rect(x * SQUARE_SIZE - SQUARE_SIZE // 8, y * SQUARE_SIZE, SQUARE_SIZE // 4,
                                                SQUARE_SIZE * 2)
                    horizontal_wall = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2,
                                                  SQUARE_SIZE // 4)
                    if self.is_wall_valid(vertical_wall, "VERTICAL"):
                        moves.append(('WALL_VERTICAL', (x, y)))
                    if self.is_wall_valid(horizontal_wall, "HORIZONTAL"):
                        moves.append(('WALL_HORIZONTAL', (x, y)))

        return moves

    def draw_move_dots(self):
        """
          Draw circles on the screen to indicate available moves for the current player's pawn.
          The circles are drawn at the center of each valid move position.

          This function calculates the available moves from the current position and
          visualizes them on the game board.
          """
        for move in self.available_moves_from_position(self.pawns[current_turn]):
            x = move[0] * SQUARE_SIZE + SQUARE_SIZE // 2
            y = move[1] * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(screen, MOVE_DOT_COLOR, (x, y), SQUARE_SIZE // 6)

    def evaluate_wall_impact(self, wall, orientation):
        """
          Evaluate the strategic value of placing a wall by comparing
          the distances of both players to their goals before and after
          the wall is placed.

          Parameters:
          wall (pygame.Rect): The wall to be placed.
          orientation (str): The orientation of the wall ('VERTICAL' or 'HORIZONTAL').

          Returns:
          int: The score reflecting the strategic impact of placing the wall.
               Positive values indicate a disadvantage for Player 1, while
               negative values indicate an advantage for Player 2.
          """
        x, y = wall.x // SQUARE_SIZE, wall.y // SQUARE_SIZE

        if orientation == "VERTICAL":
            self.walls["VERTICAL"].append(wall)
        else:
            self.walls["HORIZONTAL"].append(wall)

        p1_dist_before = self.bfs_shortest_path(self.pawns[0], GRID_SIZE - 1)
        p2_dist_before = self.bfs_shortest_path(self.pawns[1], 0)
        p1_dist_after = self.bfs_shortest_path(self.pawns[0], GRID_SIZE - 1, self.walls)
        p2_dist_after = self.bfs_shortest_path(self.pawns[1], 0, self.walls)

        if orientation == "VERTICAL":
            self.walls["VERTICAL"].pop()
        else:
            self.walls["HORIZONTAL"].pop()

        score = 0
        if p1_dist_after > p1_dist_before:
            score += (p1_dist_after - p1_dist_before) * 5  # Penalize for harming player 1
        if p2_dist_after > p2_dist_before:
            score -= (p2_dist_after - p2_dist_before) * 10  # Reward for hindering player 2
        return score

    def place_wall(self, mouse_pos):
        """
          Place a wall based on the mouse position if valid.
          Updates the wall count for the current player and switches the turn.

          Parameters:
          mouse_pos (tuple): The (x, y) coordinates of the mouse cursor when a wall is placed.

          This function checks if the wall placement is valid before adding it to the game state.
          """
        x, y = mouse_pos
        grid_x = x // SQUARE_SIZE
        grid_y = y // SQUARE_SIZE
        margin = 10

        if wall_counts[current_turn] > 0:
            if abs(x % SQUARE_SIZE) < margin:
                wall = pygame.Rect(grid_x * SQUARE_SIZE - SQUARE_SIZE // 8, grid_y * SQUARE_SIZE, SQUARE_SIZE // 4,
                                   SQUARE_SIZE * 2)
                if self.is_wall_valid(wall, "VERTICAL"):
                    walls["VERTICAL"].append(wall)
                    wall_counts[current_turn] -= 1
                    self.switch_turn()
            elif abs(y % SQUARE_SIZE) < margin:
                wall = pygame.Rect(grid_x * SQUARE_SIZE, grid_y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2,
                                   SQUARE_SIZE // 4)
                if self.is_wall_valid(wall, "HORIZONTAL"):
                    walls["HORIZONTAL"].append(wall)
                    wall_counts[current_turn] -= 1
                    self.switch_turn()

    def make_move(self, move):
        """
         Execute a move, which can be a pawn move or wall placement.

         Parameters:
         move (tuple): A tuple containing the move type ('MOVE' or 'WALL') and the move data
                       (coordinates for the move or wall).

         This function updates the game state according to the type of move and the validity of the move.
         """
        move_type, move_data = move
        possible_moves = self.possible_moves()

        if move_type == 'MOVE' and move in possible_moves:
            if move_data in self.available_moves_from_position(self.pawns[self.current_turn]):
                self.previous_position[current_turn] = self.pawns[current_turn]
                self.pawns[self.current_turn] = move_data

        elif move_type == 'WALL_VERTICAL' and move in possible_moves:
            x, y = move_data
            wall = pygame.Rect(x * SQUARE_SIZE - SQUARE_SIZE // 8, y * SQUARE_SIZE, SQUARE_SIZE // 4, SQUARE_SIZE * 2)
            if self.is_wall_valid(wall, "VERTICAL"):
                self.walls["VERTICAL"].append(wall)
                wall_counts[self.current_turn] -= 1

        elif move_type == 'WALL_HORIZONTAL' and move in possible_moves:
            x, y = move_data
            wall = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2, SQUARE_SIZE // 4)
            if self.is_wall_valid(wall, "HORIZONTAL"):
                self.walls["HORIZONTAL"].append(wall)
                wall_counts[self.current_turn] -= 1

        self.switch_turn()

    def unmake_move(self, move):
        """
           Unmake a previously executed move, restoring the game state.

           Parameters:
           move (tuple): A tuple containing the move type ('MOVE' or 'WALL') and the move data
                         (coordinates for the move or wall).

           This function is important for implementing AI search algorithms that require
           evaluating multiple potential game states.
           """
        move_type, move_data = move
        self.switch_turn()
        if move_type == 'MOVE':
            self.pawns[self.current_turn] = self.previous_position[self.current_turn]
        elif move_type == 'WALL_VERTICAL':
            wall_counts[self.current_turn] += 1
            try:
                self.walls["VERTICAL"].remove(
                    pygame.Rect(move_data[0] * SQUARE_SIZE, move_data[1] * SQUARE_SIZE - SQUARE_SIZE // 8,
                                SQUARE_SIZE * 2, SQUARE_SIZE // 4))
            except ValueError:
                pass
        elif move_type == 'WALL_HORIZONTAL':
            wall_counts[self.current_turn] += 1
            try:
                self.walls["HORIZONTAL"].remove(
                    pygame.Rect(move_data[0] * SQUARE_SIZE, move_data[1] * SQUARE_SIZE - SQUARE_SIZE // 8,
                                SQUARE_SIZE * 2, SQUARE_SIZE // 4))
            except ValueError:
                pass

    def win(self):
        """
           Check if the current player has won the game by reaching their goal row.

           Returns:
           bool: True if the current player has won, False otherwise.
           """
        if self.current_turn == 0:
            return self.pawns[0][1] == GRID_SIZE - 1
        else:
            return self.pawns[1][1] == 0

    def is_over(self):
        """
         Check if the game is over based on win conditions.

         Returns:
         bool: True if the game is over, False otherwise.
         """
        return self.win()

    def show(self, mouse_pos):
        """
           Display the game board and update the screen.

           Parameters:
           mouse_pos (tuple): The (x, y) coordinates of the mouse cursor for highlighting.

           This function draws the grid, pawns, walls, and highlights potential wall placements.
           """
        draw_grid()
        self.draw_pawns()
        draw_walls()
        draw_wall_counters()
        self.highlight_wall(mouse_pos)
        pygame.display.flip()

    def scoring(self):
        """
         Evaluate the current game state for AI decision-making.

         Returns:
         int: A score reflecting the desirability of the current state for the AI.
               Higher scores indicate more favorable conditions for the AI player.
         """
        if self.pawns[0][1] == GRID_SIZE - 1:  # Player 1 reached the last row
            return -1000
        if self.pawns[1][1] == 0:  # Player 2 reached the first row
            return 10000000000000000000

        wall_score = 0
        for x in range(GRID_SIZE - 1):
            for y in range(GRID_SIZE - 1):
                vertical_wall = pygame.Rect(x * SQUARE_SIZE - SQUARE_SIZE // 8, y * SQUARE_SIZE, SQUARE_SIZE // 4,
                                            SQUARE_SIZE * 2)
                horizontal_wall = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2,
                                              SQUARE_SIZE // 4)
                if self.is_wall_valid(vertical_wall, "VERTICAL"):
                    wall_score += self.evaluate_wall_impact(vertical_wall, "VERTICAL")
                if self.is_wall_valid(horizontal_wall, "HORIZONTAL"):
                    wall_score += self.evaluate_wall_impact(horizontal_wall, "HORIZONTAL")

        player1_position = self.pawns[0][1]
        player2_position = self.pawns[1][1]
        score = (GRID_SIZE - player2_position) * 10
        score -= player1_position * 10
        score += (player1_position - player2_position) * 5
        score += wall_score
        if self.previous_position[self.current_turn] == self.pawns[self.current_turn]:
            score -= 200
        return score


def main():
    """
       Main function to run the Quoridor game.

       This function initializes the game loop, handles player input,
       and updates the game state until the game is over.
       """
    clock = pygame.time.Clock()
    global game_over

    # Set up the game with AI
    ai_algo = Negamax(2)
    game = QuoridorGame([Human_Player(), AI_Player(ai_algo)])

    while not game_over:
        mouse_pos = pygame.mouse.get_pos()
        game.show(mouse_pos)

        if isinstance(game.players[current_turn], Human_Player):
            game.draw_move_dots()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    if event.button == 1:
                        grid_x = mouse_pos[0] // SQUARE_SIZE
                        grid_y = mouse_pos[1] // SQUARE_SIZE
                        game.make_move(("MOVE", [grid_x, grid_y]))
                    elif event.button == 3:
                        game.place_wall(mouse_pos)

        else:
            ai_move = game.players[current_turn].ask_move(game)
            game.make_move(ai_move)

        if game.is_over():
            game_over = True
            draw_win_message("Game Over")

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    ai_algo = ()

    game = QuoridorGame([Human_Player(), AI_Player(ai_algo)])

    main()
