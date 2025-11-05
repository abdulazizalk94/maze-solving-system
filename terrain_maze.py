import pygame, random, sys, time
from heapq import heappush, heappop

# === CONFIG ===
CELL = 10
GRID_W, GRID_H = 81, 61   # must be odd for proper maze
SCREEN_W, SCREEN_H = CELL * GRID_W, CELL * GRID_H
FPS = 60
AUTO_RESET_DELAY = 3  # seconds before generating a new maze

# Colors
BLACK = (0, 0, 0)
WHITE = (240, 240, 240)
BLUE  = (50, 120, 255)
GREEN = (0, 255, 0)
RED   = (255, 80, 80)

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Connected Maze with A* Auto Reset")
clock = pygame.time.Clock()

# ---------- Maze Generation ----------
def make_maze(w, h):
    maze = [[1 for _ in range(h)] for _ in range(w)]  # 1=wall, 0=path
    stack = []
    sx, sy = 1, 1
    maze[sx][sy] = 0
    stack.append((sx, sy))

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(2,0),(-2,0),(0,2),(0,-2)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx < w-1 and 1 <= ny < h-1 and maze[nx][ny] == 1:
                neighbors.append((nx, ny))
        if neighbors:
            nx, ny = random.choice(neighbors)
            wx, wy = (x + nx)//2, (y + ny)//2
            maze[wx][wy] = 0
            maze[nx][ny] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    return maze

# ---------- A* Pathfinding ----------
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def a_star(maze, start, goal):
    open_heap = []
    heappush(open_heap, (0, start))
    came_from = {}
    g_score = {start: 0}
    visited = set()

    while open_heap:
        _, current = heappop(open_heap)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        visited.add(current)

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = current[0] + dx, current[1] + dy
            if not (0 <= nx < GRID_W and 0 <= ny < GRID_H): continue
            if maze[nx][ny] == 1: continue
            new_g = g_score[current] + 1
            if new_g < g_score.get((nx,ny), 1e9):
                g_score[(nx,ny)] = new_g
                f = new_g + heuristic((nx,ny), goal)
                heappush(open_heap, (f, (nx,ny)))
                came_from[(nx,ny)] = current
    return None

# ---------- Drawing ----------
def draw_maze_lines(maze, path=None, start=None, goal=None):
    screen.fill(BLACK)

    # Draw white connected paths as thin lines
    for x in range(GRID_W):
        for y in range(GRID_H):
            if maze[x][y] == 0:
                cx, cy = x * CELL + CELL // 2, y * CELL + CELL // 2
                pygame.draw.circle(screen, WHITE, (cx, cy), 2)

    # Draw path as continuous blue line
    if path:
        points = [(x*CELL + CELL//2, y*CELL + CELL//2) for (x,y) in path]
        if len(points) > 1:
            pygame.draw.lines(screen, BLUE, False, points, 2)

    # Start & End points
    if start:
        sx, sy = start[0]*CELL + CELL//2, start[1]*CELL + CELL//2
        pygame.draw.circle(screen, GREEN, (sx, sy), 4)
    if goal:
        gx, gy = goal[0]*CELL + CELL//2, goal[1]*CELL + CELL//2
        pygame.draw.circle(screen, RED, (gx, gy), 4)

    pygame.display.flip()

# ---------- Main ----------
def main():
    maze = make_maze(GRID_W, GRID_H)
    start = (1, 1)
    goal = (GRID_W - 2, GRID_H - 2)
    running = True
    path = None
    solved = False
    last_solve_time = 0

    draw_maze_lines(maze, start=start, goal=goal)
    print("Press SPACE to solve, ESC to quit.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE and not solved:
                    print("Solving...")
                    path = a_star(maze, start, goal)
                    solved = True
                    draw_maze_lines(maze, path=path, start=start, goal=goal)
                    if path:
                        print(f"✅ Path length: {len(path)}")
                        last_solve_time = time.time()
                    else:
                        print("❌ No path found.")

        # Automatically regenerate maze after delay
        if solved and (time.time() - last_solve_time) >= AUTO_RESET_DELAY:
            maze = make_maze(GRID_W, GRID_H)
            path = None
            solved = False
            draw_maze_lines(maze, start=start, goal=goal)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
