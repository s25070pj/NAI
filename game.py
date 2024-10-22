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


def switch_turn():
    global current_turn
    current_turn = 1 - current_turn


def draw_grid():
    screen.fill(BACKGROUND_COLOR)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)


def draw_pawns():
    for i, pawn in enumerate(pawns):
        x = pawn[0] * SQUARE_SIZE + SQUARE_SIZE // 2
        y = pawn[1] * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, PAWN_COLOR[i], (x, y), SQUARE_SIZE // 3)


def draw_walls():
    for wall in walls["VERTICAL"]:
        pygame.draw.rect(screen, WALL_COLOR, wall)
    for wall in walls["HORIZONTAL"]:
        pygame.draw.rect(screen, WALL_COLOR, wall)


def move_player(player, new_pos):
    if 0 <= new_pos[0] < GRID_SIZE and 0 <= new_pos[1] < GRID_SIZE:
        current_pos = pawns[current_turn]
        dx, dy = abs(new_pos[0] - current_pos[0]), abs(new_pos[1] - current_pos[1])
        if dx + dy == 1 and not is_move_blocked(current_pos, new_pos):
            pawns[current_turn] = new_pos
            switch_turn()


def bfs(start_pos, goal_row):
    queue = deque([start_pos])
    visited = set()
    visited.add(tuple(start_pos))

    while queue:
        x, y = queue.popleft()

        if y == goal_row:
            return True

        for move in available_moves_from_position(x, y):
            if tuple(move) not in visited:
                visited.add(tuple(move))
                queue.append(move)

    return False


def is_path_to_goal():
    if not bfs(pawns[0], GRID_SIZE - 1):
        return False

    if not bfs(pawns[1], 0):
        return False

    return True


def is_move_blocked(start, end):
    x1, y1 = start
    x2, y2 = end

    if x1 == x2:
        if y2 > y1:
            for wall in walls["HORIZONTAL"]:
                if wall.collidepoint(x1 * SQUARE_SIZE + SQUARE_SIZE // 2, y1 * SQUARE_SIZE + SQUARE_SIZE):
                    return True
        elif y2 < y1:
            for wall in walls["HORIZONTAL"]:
                if wall.collidepoint(x1 * SQUARE_SIZE + SQUARE_SIZE // 2, y2 * SQUARE_SIZE + SQUARE_SIZE):
                    return True
    elif y1 == y2:
        if x2 > x1:
            for wall in walls["VERTICAL"]:
                if wall.collidepoint(x1 * SQUARE_SIZE + SQUARE_SIZE, y1 * SQUARE_SIZE + SQUARE_SIZE // 2):
                    return True
        elif x2 < x1:
            for wall in walls["VERTICAL"]:
                if wall.collidepoint(x2 * SQUARE_SIZE + SQUARE_SIZE, y1 * SQUARE_SIZE + SQUARE_SIZE // 2):
                    return True
    return False


def place_wall(mouse_pos):
    x, y = mouse_pos
    grid_x = x // SQUARE_SIZE
    grid_y = y // SQUARE_SIZE
    margin = 10

    if wall_counts[current_turn] > 0:
        if abs(x % SQUARE_SIZE) < margin:  # Placing a vertical wall
            wall = pygame.Rect(grid_x * SQUARE_SIZE - SQUARE_SIZE // 8, grid_y * SQUARE_SIZE, SQUARE_SIZE // 4, SQUARE_SIZE * 2)
            if is_wall_valid(wall, "VERTICAL"):
                walls["VERTICAL"].append(wall)
                wall_counts[current_turn] -= 1
                switch_turn()
            else:
                print("Invalid wall placement: Cannot place vertical wall here!")
        elif abs(y % SQUARE_SIZE) < margin:  # Placing a horizontal wall
            wall = pygame.Rect(grid_x * SQUARE_SIZE, grid_y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2, SQUARE_SIZE // 4)
            if is_wall_valid(wall, "HORIZONTAL"):
                walls["HORIZONTAL"].append(wall)
                wall_counts[current_turn] -= 1
                switch_turn()
            else:
                # Provide feedback if the wall cannot be placed
                print("Invalid wall placement: Cannot place horizontal wall here!")


def is_wall_valid(wall, orientation):
    # Check if the wall is out of bounds
    if wall.left < 0 or wall.right > SCREEN_WIDTH or wall.top < 0 or wall.bottom > SCREEN_HEIGHT:
        print("Wall is out of bounds!")
        print(f"{wall.left}, {wall.right}, {wall.top}, {wall.bottom}")
        return False

    # Check if the wall overlaps with another wall of the same orientation
    for existing_wall in walls[orientation]:
        if wall.colliderect(existing_wall):
            print("Wall overlaps with another wall!")
            return False

    # Check for intersections with walls of the opposite orientation
    opposite_orientation = "HORIZONTAL" if orientation == "VERTICAL" else "VERTICAL"
    for opposite_wall in walls[opposite_orientation]:
        wall_center = (wall.centerx, wall.centery)
        opp_wall_center = (opposite_wall.centerx, opposite_wall.centery)
        if (abs(wall_center[0] - opp_wall_center[0]) < SQUARE_SIZE // 2 and
                abs(wall_center[1] - opp_wall_center[1]) < SQUARE_SIZE // 2):
            print("Wall too close to an opposite wall!")
            return False

    # Check if placing the wall blocks all paths to the goal
    walls[orientation].append(wall)
    path_valid = is_path_to_goal()
    walls[orientation].remove(wall)

    if not path_valid:
        print("Wall placement blocks all paths!")
        return False

    return True


def available_moves_from_position(x, y):
    moves = []

    if y > 0 and not is_move_blocked([x, y], [x, y - 1]):  # Góra
        moves.append([x, y - 1])
    if y < GRID_SIZE - 1 and not is_move_blocked([x, y], [x, y + 1]):  # Dół
        moves.append([x, y + 1])
    if x > 0 and not is_move_blocked([x, y], [x - 1, y]):  # Lewo
        moves.append([x - 1, y])
    if x < GRID_SIZE - 1 and not is_move_blocked([x, y], [x + 1, y]):  # Prawo
        moves.append([x + 1, y])

    return moves


def is_wall_blocking(x, y, direction):
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


def check_win():
    if pawns[0][1] == GRID_SIZE - 1:
        return "Player Red Won"
    elif pawns[1][1] == 0:
        return "Player Blue Won"
    return None


def draw_win_message(message):
    font = pygame.font.SysFont(None, 48)
    text = font.render(message, True, (0, 255, 0))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))


def highlight_wall(mouse_pos):
    x, y = mouse_pos
    grid_x = x // SQUARE_SIZE
    grid_y = y // SQUARE_SIZE
    margin = 10

    if abs(x % SQUARE_SIZE) < margin:
        wall = pygame.Rect(grid_x * SQUARE_SIZE - SQUARE_SIZE // 8, grid_y * SQUARE_SIZE, SQUARE_SIZE // 4,
                           SQUARE_SIZE * 2)
        if is_wall_valid(wall, "VERTICAL"):
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, wall)
    elif abs(y % SQUARE_SIZE) < margin:
        wall = pygame.Rect(grid_x * SQUARE_SIZE, grid_y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2,
                           SQUARE_SIZE // 4)
        if is_wall_valid(wall, "HORIZONTAL"):
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, wall)


def draw_wall_counters():
    text_p1 = font.render(f"Player 1 walls: {wall_counts[0]}", True, PAWN_COLOR[0])
    text_p2 = font.render(f"Player 2 walls: {wall_counts[1]}", True, PAWN_COLOR[1])
    screen.blit(text_p1, (20, SCREEN_HEIGHT - 40))
    screen.blit(text_p2, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40))


def available_moves():
    current_pos = pawns[current_turn]
    moves = []
    x, y = current_pos

    if y > 0:
        moves.append([x, y - 1])
    if y < GRID_SIZE - 1:
        moves.append([x, y + 1])
    if x > 0:
        moves.append([x - 1, y])
    if x < GRID_SIZE - 1:
        moves.append([x + 1, y])

    return moves


def draw_move_dots():
    for move in available_moves_from_position(*pawns[current_turn]):
        x = move[0] * SQUARE_SIZE + SQUARE_SIZE // 2
        y = move[1] * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, MOVE_DOT_COLOR, (x, y), SQUARE_SIZE // 6)


class QuoridorGame(TwoPlayerGame):
    def __init__(self, players):
        # Initialize players
        self.players = players
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Each player has a pawn at the initial position
        self.pawns = [[4, 0], [4, 8]]  # Starting positions for player 1 and player 2
        self.walls = {"VERTICAL": [], "HORIZONTAL": []}
        self.wall_counts = [MAX_WALLS, MAX_WALLS]
        self.current_turn = 0  # Player 1 starts first

        # Inherit turn management from TwoPlayersGame
        self.current_player = 1

    def possible_moves(self):
        """ Return a list of all possible moves (pawn moves + wall placements) """
        moves = []

        # Add possible pawn moves (valid moves are determined by current position)
        current_pawn_pos = self.pawns[self.current_turn]
        pawn_moves = available_moves_from_position(current_pawn_pos[0], current_pawn_pos[1])
        for move in pawn_moves:
            moves.append(('MOVE', move))

        # Add possible wall placements (vertical or horizontal) if the player has walls left
        if self.wall_counts[self.current_turn] > 0:
            for x in range(GRID_SIZE):
                for y in range(GRID_SIZE):
                    # Check if vertical wall placement is valid
                    vertical_wall = pygame.Rect(x * SQUARE_SIZE - SQUARE_SIZE // 8, y * SQUARE_SIZE, SQUARE_SIZE // 4,
                                                SQUARE_SIZE * 2)
                    if is_wall_valid(vertical_wall, "VERTICAL"):
                        moves.append(('WALL_VERTICAL', (x, y)))

                    # Check if horizontal wall placement is valid
                    horizontal_wall = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2,
                                                  SQUARE_SIZE // 4)
                    if is_wall_valid(horizontal_wall, "HORIZONTAL"):
                        moves.append(('WALL_HORIZONTAL', (x, y)))

        return moves

    def make_move(self, move):
        """ Execute a move. Moves are tuples ('MOVE' or 'WALL', coordinates) """
        move_type, move_data = move

        if move_type == 'MOVE':
            new_pos = move_data
            # Check if the move is valid (from current pawn position to new position)
            if new_pos in available_moves_from_position(*self.pawns[self.current_turn]):
                self.pawns[self.current_turn] = new_pos

        elif move_type == 'WALL_VERTICAL':
            x, y = move_data
            wall = pygame.Rect(x * SQUARE_SIZE - SQUARE_SIZE // 8, y * SQUARE_SIZE, SQUARE_SIZE // 4, SQUARE_SIZE * 2)
            if is_wall_valid(wall, "VERTICAL"):
                self.walls["VERTICAL"].append(wall)
                self.wall_counts[self.current_turn] -= 1

        elif move_type == 'WALL_HORIZONTAL':
            x, y = move_data
            wall = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2, SQUARE_SIZE // 4)
            if is_wall_valid(wall, "HORIZONTAL"):
                self.walls["HORIZONTAL"].append(wall)
                self.wall_counts[self.current_turn] -= 1

        switch_turn()

    def unmake_move(self, move):
        """ Unmake a move (important for AI search algorithms like Negamax) """
        move_type, move_data = move
        if move_type == 'MOVE':
            # You can revert to the previous position or store the history of moves
            pass
        elif move_type == 'WALL_VERTICAL':
            self.walls["VERTICAL"].remove(
                pygame.Rect(move_data[0] * SQUARE_SIZE - SQUARE_SIZE // 8, move_data[1] * SQUARE_SIZE, SQUARE_SIZE // 4,
                            SQUARE_SIZE * 2))
            self.wall_counts[self.current_turn] += 1
        elif move_type == 'WALL_HORIZONTAL':
            self.walls["HORIZONTAL"].remove(
                pygame.Rect(move_data[0] * SQUARE_SIZE, move_data[1] * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2,
                            SQUARE_SIZE // 4))
            self.wall_counts[self.current_turn] += 1

    def win(self):
        """ Check if the current player has won after making a valid move """
        if self.current_turn == 0:
            # Player 1 wins when reaching the last row (bottom row)
            return self.pawns[0][1] == GRID_SIZE - 1
        else:
            # Player 2 wins when reaching the first row (top row)
            return self.pawns[1][1] == 0

    def is_over(self):
        """ Check if the game is over """
        return self.win()

    def show(self):
        """ Display the board (or update the Pygame screen) """
        draw_grid()
        draw_pawns()
        draw_walls()
        draw_wall_counters()
        pygame.display.flip()

    def scoring(self):
        """ This function returns the value of the current game state for the AI """
        if self.current_turn == 0:
            return pawns[0][1]  # Closer to the bottom row is better for player 1
        else:
            return GRID_SIZE - pawns[1][1]  # Closer to the top row is better for player 2


def main():
    clock = pygame.time.Clock()
    global game_over

    # Set up the game with AI
    ai_algo = Negamax(3)
    game = QuoridorGame([Human_Player(), AI_Player(ai_algo)])

    while not game_over:
        game.show()

        if isinstance(game.players[game.current_turn], Human_Player):
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    if event.button == 1:
                        grid_x = mouse_pos[0] // SQUARE_SIZE
                        grid_y = mouse_pos[1] // SQUARE_SIZE
                        game.make_move(('MOVE', [grid_x, grid_y]))
                    elif event.button == 3:
                        game.make_move(('WALL', mouse_pos))

        else:
            game.ai_move(ai_algo)

        if game.is_over():
            game_over = True
            draw_win_message("Game Over")

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    ai_algo = Negamax(3)

    game = QuoridorGame([Human_Player(), AI_Player(ai_algo)])

    main()
