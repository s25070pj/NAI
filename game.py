import pygame
import sys

pygame.init()

current_turn = 0

SCREEN_WIDTH, SCREEN_HEIGHT = 720, 720
GRID_SIZE = 9
SQUARE_SIZE = SCREEN_WIDTH // GRID_SIZE
LINE_COLOR = (0, 0, 0)

BACKGROUND_COLOR = (255, 255, 255)
PAWN_COLOR = [(255, 0, 0), (0, 0, 255)]  # Red for player1, Blue for player2
WALL_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (128, 128, 128)
MOVE_DOT_COLOR = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Quoridor")


player1_pos = [4, 0]
player2_pos = [4, 8]
pawns = [player1_pos, player2_pos]
walls = {"VERTICAL": [], "HORIZONTAL": []}

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
        if dx + dy == 1:
            pawns[current_turn] = new_pos
            switch_turn()

def place_wall(mouse_pos):
    x, y = mouse_pos
    grid_x = x // SQUARE_SIZE
    grid_y = y // SQUARE_SIZE
    margin = 10

    if abs(x % SQUARE_SIZE) < margin:
        wall = pygame.Rect(grid_x * SQUARE_SIZE - SQUARE_SIZE // 8, grid_y * SQUARE_SIZE, SQUARE_SIZE // 4, SQUARE_SIZE * 2)
        walls["VERTICAL"].append(wall)
        switch_turn()
    elif abs(y % SQUARE_SIZE) < margin:
        wall = pygame.Rect(grid_x * SQUARE_SIZE, grid_y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2, SQUARE_SIZE // 4)
        walls["HORIZONTAL"].append(wall)
        switch_turn()

def highlight_wall(mouse_pos):
    x, y = mouse_pos
    grid_x = x // SQUARE_SIZE
    grid_y = y // SQUARE_SIZE
    margin = 10

    if abs(x % SQUARE_SIZE) < margin:
        wall = pygame.Rect(grid_x * SQUARE_SIZE - SQUARE_SIZE // 8, grid_y * SQUARE_SIZE, SQUARE_SIZE // 4, SQUARE_SIZE * 2)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, wall)
    elif abs(y % SQUARE_SIZE) < margin:
        wall = pygame.Rect(grid_x * SQUARE_SIZE, grid_y * SQUARE_SIZE - SQUARE_SIZE // 8, SQUARE_SIZE * 2, SQUARE_SIZE // 4)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, wall)

def available_moves():
    current_pos = pawns[current_turn]
    moves = []
    x, y = current_pos

    if y > 0:  # Góra
        moves.append([x, y - 1])
    if y < GRID_SIZE - 1:  # Dół
        moves.append([x, y + 1])
    if x > 0:  # Lewo
        moves.append([x - 1, y])
    if x < GRID_SIZE - 1:  # Prawo
        moves.append([x + 1, y])

    return moves

def draw_move_dots():
    moves = available_moves()
    for move in moves:
        x = move[0] * SQUARE_SIZE + SQUARE_SIZE // 2
        y = move[1] * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, MOVE_DOT_COLOR, (x, y), 10)

def main():
    clock = pygame.time.Clock()

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    grid_x = mouse_pos[0] // SQUARE_SIZE
                    grid_y = mouse_pos[1] // SQUARE_SIZE
                    move_player(pawns[current_turn], [grid_x, grid_y])
                elif event.button == 3:  # right mouse button
                    place_wall(mouse_pos)

        draw_grid()
        draw_pawns()
        draw_walls()
        draw_move_dots()
        highlight_wall(mouse_pos)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
