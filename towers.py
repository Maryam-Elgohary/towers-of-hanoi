
import pygame
import sys
import heapq
import time

pygame.init()

# Window setup
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Towers of Hanoi - AI Mode")

# Fonts
FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("Arial", 48, bold=True)

# Colors
WHITE = (250, 250, 250)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 200, 100)
BG_COLOR = (240, 245, 255)

# Sounds
move_sound = pygame.mixer.Sound("move.mp3")
victory_sound = pygame.mixer.Sound("victory.mp3")

# Towers positions
tower_x = [250, 450, 650]

# Draw towers and disks
# state ==> a list representing the three towers and disks on them [[],[],[]]
# num_disks ==> total number of disks
# shake ==> for animation
def draw_towers(state, num_disks, shake=False):
    screen.fill(BG_COLOR)
    offset = 3 if shake else 0

    # Base
    # 150 - offset ==> X-Coordinates
    # 500 ==> Y-Coordinates
    # 600 ==> wide
    # 10 ==> tall
    pygame.draw.rect(screen, BLACK, (150 - offset, 500, 600, 10))
    
    # Towers
    # tower_x ==> contains the X-Coordinates of the three towers
    # x- 10 ==> centers the tower
    for x in tower_x:
        pygame.draw.rect(screen, BLACK, (x - 10 + offset, 200, 20, 300))
    
    # Disks
    colors = [pygame.Color("#FFADAD"), pygame.Color("#FFD6A5"), pygame.Color("#FDFFB6"),
              pygame.Color("#CAFFBF"), pygame.Color("#9BF6FF"), pygame.Color("#A0C4FF")]

    # loops through the three towers
    for i in range(3):
        tower = state[i]
        # loops through disks on the tower
        # j ==> position of the disk from bottom to up
        # disk ==> disk's size (1 for smallest, 2 for medium, etc)
        for j, disk in enumerate(tower):
            # disk size
            width = 30 + disk * 20
            rect = pygame.Rect(
                tower_x[i] - width // 2 + offset,
                500 - (j + 1) * 20,
                width,
                20
            )
            pygame.draw.rect(screen, colors[disk - 1], rect)
            # draws a 2-pixel-wide-black outline around the disk for visibility
            pygame.draw.rect(screen, BLACK, rect, 2)

# A* algorithm for Hanoi
def a_star_hanoi(start_state, goal_state):
    def heuristic(state):
        return sum(disk not in goal for disk, goal in zip(state, goal_state))

    def state_to_tuple(state):
        return tuple(tuple(peg) for peg in state)

    visited = set()
    heap = [(0, start_state, [])]

    while heap:
        cost, state, path = heapq.heappop(heap)
        state_tuple = state_to_tuple(state)
        if state_tuple in visited:
            continue
        visited.add(state_tuple)

        if state == goal_state:
            return path

        for from_peg in range(3):
            if not state[from_peg]:
                continue
            disk = state[from_peg][-1]
            for to_peg in range(3):
                if from_peg == to_peg:
                    continue
                if not state[to_peg] or state[to_peg][-1] > disk:
                    new_state = [list(peg) for peg in state]
                    new_state[from_peg].pop()
                    new_state[to_peg].append(disk)
                    heapq.heappush(heap, (
                        cost + 1 + heuristic(new_state),
                        new_state,
                        path + [(from_peg, to_peg)]
                    ))
    return []

# Auto solve using A*
def auto_solve(state, num_disks):
    goal_state = [[], [], list(reversed(range(1, num_disks + 1)))]
    moves = a_star_hanoi(state, goal_state)
    for move in moves:
        from_peg, to_peg = move
        disk = state[from_peg].pop()
        state[to_peg].append(disk)
        draw_towers(state, num_disks)
        pygame.display.flip()
        move_sound.play()
        pygame.time.delay(400)

# Welcome screen
def welcome_screen():
    selected_disks = 3
    start_button = pygame.Rect(350, 400, 200, 50)
    minus_button = pygame.Rect(350, 250, 40, 40)
    plus_button = pygame.Rect(510, 250, 40, 40)

    while True:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Towers of Hanoi", True, BLUE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        disk_text = FONT.render(f"Number of disks: {selected_disks}", True, BLACK)
        screen.blit(disk_text, (WIDTH // 2 - disk_text.get_width() // 2, 200))

        pygame.draw.rect(screen, RED, minus_button)
        pygame.draw.rect(screen, GREEN, plus_button)
        screen.blit(FONT.render("-", True, WHITE), (minus_button.x + 12, minus_button.y + 5))
        screen.blit(FONT.render("+", True, WHITE), (plus_button.x + 12, plus_button.y + 5))
        pygame.draw.rect(screen, BLUE, start_button)
        screen.blit(FONT.render("Start Game", True, WHITE), (start_button.x + 30, start_button.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if minus_button.collidepoint(event.pos) and selected_disks > 3:
                    selected_disks -= 1
                elif plus_button.collidepoint(event.pos) and selected_disks < 6:
                    selected_disks += 1
                elif start_button.collidepoint(event.pos):
                    return selected_disks

# Win screen
def game_won():
    victory_sound.play()
    for _ in range(4):
        draw_towers([[], [], []], 0, shake=True)
        pygame.display.flip()
        pygame.time.delay(100)
        draw_towers([[], [], []], 0, shake=False)
        pygame.display.flip()
        pygame.time.delay(100)
    screen.fill(BG_COLOR)
    msg = BIG_FONT.render("Well Done! Puzzle Solved!", True, GREEN)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.flip()
    pygame.time.delay(2000)

# Main game loop
def main():
    num_disks = welcome_screen()
    towers = [list(reversed(range(1, num_disks + 1))), [], []]

    solve_button = pygame.Rect(680, 40, 180, 40)
    restart_button = pygame.Rect(680, 90, 180, 40)

    dragging = False
    selected_peg = None

    while True:
        draw_towers(towers, num_disks)
        pygame.draw.rect(screen, RED, solve_button)
        screen.blit(FONT.render("Solve with A*", True, WHITE), (solve_button.x + 20, solve_button.y + 8))
        pygame.draw.rect(screen, BLUE, restart_button)
        screen.blit(FONT.render("Restart", True, WHITE), (restart_button.x + 50, restart_button.y + 8))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if solve_button.collidepoint(event.pos):
                    auto_solve(towers, num_disks)
                    if towers == [[], [], list(reversed(range(1, num_disks + 1)))]:
                        game_won()
                        return main()
                elif restart_button.collidepoint(event.pos):
                    return main()
                else:
                    x = event.pos[0]
                    for i, tx in enumerate(tower_x):
                        if abs(x - tx) < 50:
                            if towers[i]:
                                dragging = True
                                selected_peg = i
            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                x = event.pos[0]
                for i, tx in enumerate(tower_x):
                    if abs(x - tx) < 50:
                        if i != selected_peg and (not towers[i] or towers[i][-1] > towers[selected_peg][-1]):
                            towers[i].append(towers[selected_peg].pop())
                            move_sound.play()
                            if towers == [[], [], list(reversed(range(1, num_disks + 1)))]:
                                game_won()
                                return main()
                        break
                dragging = False
                selected_peg = None

main()
