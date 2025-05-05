
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
# start_state ==> all disks on tower 1
# goal_state ==> all disks on tower 3
# returns a list of moves to get from start to goal
def a_star_hanoi(start_state, goal_state):
    # heuristic(state) ==> guesses how far the current state is from the goal
    # Counts how many disks are not in their goal position (if disk 1 is on tower 1 but should be on tower 3, it adds 1)
    # A lower number means the state is closer to the goal.
    def heuristic(state):
        return sum(disk not in goal for disk, goal in zip(state, goal_state))
    # converts the state (list of lists) into a tuple so it can be stored in a set ==> track visited states
    def state_to_tuple(state):
        return tuple(tuple(peg) for peg in state)
    # Keeps track of states we’ve already checked to avoid repeating work
    visited = set()
    # a priority queue 
    # Cost (0 at the start)
    # start_state ==> all disks on tower 1 [[1,2,3],[],[]]
    # [] ==> empty path , list of moves
    heap = [(0, start_state, [])]
    # Keeps going until the queue is empty or the goal is found
    
    while heap:
        # Picks the state with the lowest cost
        cost, state, path = heapq.heappop(heap)
        state_tuple = state_to_tuple(state) 
        # Checks if the state was visited before. If yes, skips it to avoid loops. If no, adds the state to visited
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        # If the current state matches the goal (e.g., all disks on tower 3), returns the path (list of moves).
        if state == goal_state:
            return path
        # Loops through each peg to see if it has disks
        for from_peg in range(3):
            # skips empty pegs
            if not state[from_peg]:
                continue
            # Takes the top disk from from_peg
            disk = state[from_peg][-1]
            # Tries moving it to each other peg
            for to_peg in range(3):
                # Skips if from_peg == to_peg (can’t move to the same peg).
                if from_peg == to_peg:
                    continue
                # Checks if the move is legal: The destination peg must be empty (not state[to_peg]) or have a larger disk on top (state[to_peg][-1] > disk)
                if not state[to_peg] or state[to_peg][-1] > disk:
                    # Creates a new_state by copying the current state.
                    new_state = [list(peg) for peg in state]
                    # Removes the disk from from_peg
                    new_state[from_peg].pop()
                    # Adds the disk to to_peg
                    new_state[to_peg].append(disk)
                    # Adds the new state to the queue with:
                    # New cost: cost + 1 + heuristic(new_state) (1 for the move, plus the heuristic guess)
                    # The new state
                    # Updated path: path + [(from_peg, to_peg)] (adds the move, e.g., “move from peg 1 to peg 3”)
                    heapq.heappush(heap, (
                        cost + 1 + heuristic(new_state),
                        new_state,
                        path + [(from_peg, to_peg)]
                    ))
    # If the queue runs out without finding the goal, returns [] (no solution)
    return []

# Auto solve using A*
def auto_solve(state, num_disks):
    # Creates the goal state, where all disks are stacked on peg 3 (the third peg) in order from largest to smallest
    # range(1, num_disks + 1) ==> makes a list of disk sizes
    goal_state = [[], [], list(reversed(range(1, num_disks + 1)))]
    # moves is a list of tuples, where each tuple is a move like (from_peg, to_peg)
    moves = a_star_hanoi(state, goal_state)
    # loop through each move in the moves list one by one to apply it to the game
    for move in moves:
        # Each move is a tuple like (1, 3)
        from_peg, to_peg = move
        disk = state[from_peg].pop()
        state[to_peg].append(disk)
        # Calls the draw_towers function (explained earlier) to redraw the game board with the updated state, showing the towers and disks in their new positions.
        draw_towers(state, num_disks)
        # Updates the Pygame window to show the new drawing
        pygame.display.flip()
        move_sound.play()
        pygame.time.delay(400)

# Welcome screen
# Shows a welcome screen with the game title, the number of disks, and buttons
# Lets the player adjust the number of disks (between 3 and 6) using “+” and “–” buttons.
# Starts the game when the player clicks a “Start Game” button
# Returns the chosen number of disks (e.g., 3, 4, 5, or 6) to use in the game
def welcome_screen():
    # Starts with 3 disks as the default number.
    selected_disks = 3
    start_button = pygame.Rect(350, 400, 200, 50)
    minus_button = pygame.Rect(350, 250, 40, 40)
    plus_button = pygame.Rect(510, 250, 40, 40)
    # Keeps the screen running until the player clicks “Start Game” or quits
    while True:
        screen.fill(BG_COLOR)
        # Creates the text “Towers of Hanoi” in blue using a big font
        title = BIG_FONT.render("Towers of Hanoi", True, BLUE)
        # Centers the title horizontally at y=100.
        # blit ==> draws text and buttons on the screen
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        # Shows “Number of disks: 3” (or 4, 5, etc.) in black
        disk_text = FONT.render(f"Number of disks: {selected_disks}", True, BLACK)
        # Centers it horizontally at y=200.
        screen.blit(disk_text, (WIDTH // 2 - disk_text.get_width() // 2, 200))

        pygame.draw.rect(screen, RED, minus_button)
        pygame.draw.rect(screen, GREEN, plus_button)
        screen.blit(FONT.render("-", True, WHITE), (minus_button.x + 12, minus_button.y + 5))
        screen.blit(FONT.render("+", True, WHITE), (plus_button.x + 12, plus_button.y + 5))
        pygame.draw.rect(screen, BLUE, start_button)
        screen.blit(FONT.render("Start Game", True, WHITE), (start_button.x + 30, start_button.y + 10))
        # Updates the screen to show all the drawings
        pygame.display.flip()
        # Checks for player actions (like clicking or closing the window)
        for event in pygame.event.get():
            # If the player closes the window, pygame.quit() and sys.exit() stop the program
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Checks if the player clicked the mouse.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # If the “–” button is clicked and selected_disks is more than 3, decrease selected_disks by 1 (e.g., 4 to 3)
                if minus_button.collidepoint(event.pos) and selected_disks > 3:
                    selected_disks -= 1
                # If the “+” button is clicked and selected_disks is less than 6, increase selected_disks by 1 (e.g., 3 to 4).
                elif plus_button.collidepoint(event.pos) and selected_disks < 6:
                    selected_disks += 1
                # If the “Start Game” button is clicked, return selected_disks (e.g., 3) to start the game with that number of disks.
                elif start_button.collidepoint(event.pos):
                    return selected_disks

# Win screen
# Plays a sound effect (defined elsewhere, like a cheerful tune) to celebrate the player solving the game
def game_won():
    victory_sound.play()
    # Loops 4 times to create a back-and-forth shaking effect
    for _ in range(4):
        # Calls the draw_towers function (explained earlier) to draw the towers, but with no disks ([[], [], []]) and num_disks = 0
        # shake=True ==> makes the towers wiggle slightly (shifts them by 3 pixels, as set in draw_towers).
        draw_towers([[], [], []], 0, shake=True)
        pygame.display.flip()
        pygame.time.delay(100)
        # Draws the towers again, but with shake=False (no wiggle, back to normal position)
        draw_towers([[], [], []], 0, shake=False)
        pygame.display.flip()
        pygame.time.delay(100)
    screen.fill(BG_COLOR)
    # Creates the text “Well Done! Puzzle Solved!” in green using a big font
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
