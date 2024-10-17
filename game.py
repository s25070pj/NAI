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

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Quoridor")


def draw_grid():
    screen.fill(BACKGROUND_COLOR)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)


def draw_pawns(pawns):
    for i, pawn in enumerate(pawns):
        pygame.draw.circle(screen, PAWN_COLOR[i], pawn, SQUARE_SIZE // 3)


def switch_turn():
    global current_turn
    current_turn = 1 - current_turn


def move_player(player_pos, direction):
    if direction == "UP" and player_pos[1] > 0:
        player_pos[1] -= SQUARE_SIZE
    elif direction == "DOWN" and player_pos[1] < (GRID_SIZE - 1) * SQUARE_SIZE:
        player_pos[1] += SQUARE_SIZE
    elif direction == "LEFT" and player_pos[0] > 0:
        player_pos[0] -= SQUARE_SIZE
    elif direction == "RIGHT" and player_pos[0] < (GRID_SIZE - 1) * SQUARE_SIZE:
        player_pos[0] += SQUARE_SIZE


def draw_walls(walls):
    for wall in walls:
        pygame.draw.rect(screen, WALL_COLOR, wall)


def place_wall(walls, position, orientation):
    if orientation == "VERTICAL":
        wall = pygame.Rect(position[0], position[1], SQUARE_SIZE // 4, SQUARE_SIZE * 2)
    elif orientation == "HORIZONTAL":
        wall = pygame.Rect(position[0], position[1], SQUARE_SIZE * 2, SQUARE_SIZE // 4)
    walls.append(wall)


def main():
    player1_pos = [SQUARE_SIZE * 4.5, SQUARE_SIZE * 0.5]
    player2_pos = [SQUARE_SIZE * 4.5, SQUARE_SIZE * GRID_SIZE * 0.945]

    pawns = [player1_pos, player2_pos]
    walls = []

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if current_turn == 0:
                    if event.key == pygame.K_UP:
                        move_player(pawns[0], "UP")
                        switch_turn()
                    elif event.key == pygame.K_DOWN:
                        move_player(pawns[0], "DOWN")
                        switch_turn()
                    elif event.key == pygame.K_LEFT:
                        move_player(pawns[0], "LEFT")
                        switch_turn()
                    elif event.key == pygame.K_RIGHT:
                        move_player(pawns[0], "RIGHT")
                        switch_turn()

                    # Player 2's turn (using WASD keys)
                elif current_turn == 1:
                    if event.key == pygame.K_w:
                        move_player(pawns[1], "UP")
                        switch_turn()
                    elif event.key == pygame.K_s:
                        move_player(pawns[1], "DOWN")
                        switch_turn()
                    elif event.key == pygame.K_a:
                        move_player(pawns[1], "LEFT")
                        switch_turn()
                    elif event.key == pygame.K_d:
                        move_player(pawns[1], "RIGHT")
                        switch_turn()

                elif event.key == pygame.K_q:
                    place_wall(walls, pawns[0], "VERTICAL")
                elif event.key == pygame.K_e:
                    place_wall(walls, pawns[0], "HORIZONTAL")
                    # Player 2 places vertical or horizontal walls with Z and C
                elif event.key == pygame.K_z:
                    place_wall(walls, pawns[1], "VERTICAL")
                elif event.key == pygame.K_c:
                    place_wall(walls, pawns[1], "HORIZONTAL")

        draw_grid()
        draw_pawns(pawns)
        draw_walls(walls)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()