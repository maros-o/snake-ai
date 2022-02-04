import pygame
import os
import random
import queue

pygame.font.init()

X, Y = 32, 22
BLOCK_SIZE = 32
HALF_X = X//2
HALF_Y = Y//2
WIDTH, HEIGHT = X * BLOCK_SIZE, Y * BLOCK_SIZE

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
SNAKE_SPRITE = pygame.image.load(os.path.join('assets', 'snake_sprite.png'))
FONT = pygame.font.SysFont('consolas', 20)
CYCFONT = pygame.font.SysFont('consolas', 12)

BGCOLOR = (30, 30, 60)
TEXTCOLOR = (255, 255, 255)
CYCTEXTCOLOR = (180, 180, 180)
PATHCOLOR = (50, 50, 80)
RED = (255, 0, 0)
GOLD = (255, 215, 0)

FPS = 20
STARTING_LEN = 3

class Node():
    def __init__(self, pos, number):
        self.pos = pos
        self.number = number

    def get_pos(self):
        return self.pos

    def get_number(self):
        return self.number  

def create_nodes():
    nodes = [[Node((x * 2 + 1, y * 2 + 1), x + y * HALF_X) for y in range(0, HALF_Y)] for x in range(0, HALF_X)]
    return nodes

def create_edges():
    edges = [[0 for y in range(0, HALF_Y * HALF_X)] for x in range(0, HALF_X * HALF_Y)]

    skiplist = [HALF_X * x for x in range(0, HALF_X)]
    for x in range(0, HALF_X * HALF_Y):
        for y in range(0, HALF_Y * HALF_X):
            if not (x == y):
                if (x + 1 == y and y not in skiplist): edges[x][y] = random.randint(1, 3)
                elif (x + HALF_X == y): edges[x][y] = random.randint(1, 3)

    return edges

def hamiltonian_cycle(nodes, edges):
    points = []
    for edge in edges:
        for pos_x in range(0, HALF_X):
            for pos_y in range(0, HALF_Y):
                if (nodes[pos_x][pos_y].get_number() == edge[0][0]):
                    start = nodes[pos_x][pos_y].get_pos()
                if (nodes[pos_x][pos_y].get_number() == edge[0][1]):
                    end = nodes[pos_x][pos_y].get_pos()
        points.append(start)
        points.append(((start[0]+end[0])//2, (start[1]+end[1])//2))
        points.append(end)

    cycle = [(0, 0)]

    curr = cycle[0]
    dir = (1, 0)

    while len(cycle) < X * Y:
        x = curr[0]
        y = curr[1]

        if dir == (1, 0): #right
            if ((x + dir[0], y + dir[1] + 1) in points and (x + 1, y) not in points):
                curr = (x + dir[0], y + dir[1])
            else:
                if ((x, y + 1) in points and (x + 1, y + 1) not in points):
                    dir = (0, 1)
                else:
                    dir = (0, -1)
        
        elif dir == (0, 1): #down
            if ((x + dir[0], y + dir[1]) in points and (x + dir[0] + 1, y + dir[1]) not in points):
                curr = (x + dir[0], y + dir[1])
            else:
                if ((x, y + 1) in points and (x + 1, y + 1) in points):
                    dir = (1, 0)
                else:
                    dir = (-1, 0)

        elif dir == (-1, 0): #left
            if ((x, y) in points and (x, y+1) not in points):
                curr = (x + dir[0], y + dir[1])
            else:
                if ((x, y + 1) not in points):
                    dir = (0, -1)
                else:
                    dir = (0, 1)

        elif dir == (0, -1): #up
            if ((x, y) not in points and (x+1, y) in points):
                curr = (x + dir[0], y + dir[1])
            else:
                if ((x+1, y) in points):
                    dir = (-1, 0)
                else:
                    dir = (1, 0)

        if curr not in cycle:
            cycle.append(curr)

    return cycle

def prims_algoritm(edges):
    clean_edges = []
    for x in range(0, HALF_X * HALF_Y):
        for y in range(0, HALF_Y * HALF_X):
            if not (edges[x][y] == 0):
                clean_edges.append(((x, y), edges[x][y]))
            
    visited = []
    unvisited = [x for x in range(HALF_X * HALF_Y)]
    curr = 0

    final_edges = []
    while len(unvisited) > 0:
        visited.append(curr)

        for number in unvisited:
            if number in visited:
                unvisited.remove(number)

        my_edges = []
        for edge in clean_edges:
            if ((edge[0][0] in visited or edge[0][1] in visited) and not (edge[0][0] in visited and edge[0][1] in visited)):
                my_edges.append(edge)

        min_edge = ((-1, -1), 999)

        for edge in my_edges:
            if (edge[1] < min_edge[1]):
                min_edge = edge
        
        if len(unvisited) == 0:
            break

        final_edges.append(min_edge)

        if min_edge[0][0] == -1:
            curr = unvisited[0]
        else:
            if (min_edge[0][1] in visited):
                curr = min_edge[0][0]
            else:
                curr = min_edge[0][1]

    return final_edges

def draw_cycle(points):
    prev = points[0]
    for point in points:
        pygame.draw.line(WIN, PATHCOLOR, [point[0] * BLOCK_SIZE + BLOCK_SIZE//2, point[1] * BLOCK_SIZE + BLOCK_SIZE//2], [prev[0] * BLOCK_SIZE + BLOCK_SIZE//2, prev[1] * BLOCK_SIZE + BLOCK_SIZE//2], 2)
        prev = point
    pygame.draw.line(WIN, PATHCOLOR, [points[0][0] * BLOCK_SIZE + BLOCK_SIZE//2, points[0][1] * BLOCK_SIZE + BLOCK_SIZE//2], [points[len(points)-1][0] * BLOCK_SIZE + BLOCK_SIZE//2, points[len(points)-1][1] * BLOCK_SIZE + BLOCK_SIZE//2], 2)

    for index, point in enumerate(points):
        text = CYCFONT.render(str(index), 1, CYCTEXTCOLOR)
        WIN.blit(text, [point[0] * BLOCK_SIZE + BLOCK_SIZE//2 - text.get_rect().width//2, point[1] * BLOCK_SIZE + BLOCK_SIZE//2 - text.get_rect().height//2])

def draw_prey(prey):
    pygame.draw.circle(WIN, GOLD, [prey[0] * BLOCK_SIZE + BLOCK_SIZE//2, prey[1] * BLOCK_SIZE + BLOCK_SIZE//2], 13)
    pygame.draw.circle(WIN, RED, [prey[0] * BLOCK_SIZE + BLOCK_SIZE//2, prey[1] * BLOCK_SIZE + BLOCK_SIZE//2], 11)

def draw_snake(snake):
    x = snake[0][0]
    y = snake[0][1]

    for index, coord in enumerate(snake):
        x = coord[0]
        y = coord[1]

        left = False
        right = False
        up = False
        down = False

        substracter = 155
        if (index < substracter):
            snake_color = (0, 255 - index, 0)
        else:
            snake_color = (0, 255 - substracter, 0)

        if (index == 0):
            WIN.blit(SNAKE_SPRITE, (x * BLOCK_SIZE, y * BLOCK_SIZE))
            continue
        
        if (index == len(snake)-1):
            if (snake[index-1] == (x-1, y)): left = True
            if (snake[index-1] == (x+1, y)): right = True
            if (snake[index-1] == (x, y-1)): up = True
            if (snake[index-1] == (x, y+1)): down = True
        else:
            if (snake[index-1] == (x-1, y) or snake[index+1] == (x-1, y)): left = True
            if (snake[index-1] == (x+1, y) or snake[index+1] == (x+1, y)): right = True
            if (snake[index-1] == (x, y-1) or snake[index+1] == (x, y-1)): up = True
            if (snake[index-1] == (x, y+1) or snake[index+1] == (x, y+1)): down = True
                
        if (left and right): pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE, y * BLOCK_SIZE + 4, 32, 24])
        elif (left and up): 
            pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE, y * BLOCK_SIZE + 4, 28, 24])
            pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE, 24, 4])
        elif (left and down): 
            pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE, y * BLOCK_SIZE + 4, 28, 24])
            pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE + 28, 24, 4])
        elif (right and up): 
            pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE + 4, 28, 24])
            pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE, 24, 4])
        elif (right and down): 
            pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE + 4, 28, 24])
            pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE + 28, 24, 4])
        elif (up and down): pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE, 24, 32])
        elif (left): pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE, y * BLOCK_SIZE + 4, 28, 24])
        elif (right): pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE + 4, 28, 24])
        elif (up): pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE, 24, 28])
        elif (down): pygame.draw.rect(WIN, snake_color, [x * BLOCK_SIZE + 4, y * BLOCK_SIZE + 4, 24, 28])

def draw_window(snake, prey, cycle):
    WIN.fill(BGCOLOR)

    draw_cycle(cycle)
    draw_prey(prey)
    draw_snake(snake)
    
    text = FONT.render("len:"+str(len(snake)), 1, TEXTCOLOR)
    WIN.blit(text, (X//3, Y//3))

    pygame.display.update()

def spawn_prey(snake):
    x = -1
    y = -1
    while(x == -1 and y == -1):
        x = random.randint(0, X - 1)
        y = random.randint(0, Y - 1)
        if (x, y) in snake:
            x = -1
            y = -1
            
    return (x, y)

def get_neighbors(point, snake):
    forbidden = snake.copy()
    for x in range(-1, X+1):
        for y in range(-1, Y+1):
            if (x == -1 or y == -1 or x == X or y == Y):
                forbidden.append((x, y))

    neighbors = []
    x = point[0]
    y = point[1]

    if not ((x+1, y) in forbidden): neighbors.append((x+1, y))
    if not ((x-1, y) in forbidden): neighbors.append((x-1, y))
    if not ((x, y+1) in forbidden): neighbors.append((x, y+1))
    if not ((x, y-1) in forbidden): neighbors.append((x, y-1))

    return neighbors

def h(point, end):
    return abs(point[0] - end[0]) + abs(point[1] - end[1])

def reconstruct_path(came_from, current):
    path_coords = [current]
    while current in came_from:
        current = came_from[current]
        path_coords.append(current)
    path_coords.reverse()

    path = ""
    for index, coord in enumerate(path_coords):
        x = coord[0]
        y = coord[1]

        if (index >= len(path_coords)-1):
            break

        if (path_coords[index+1] == (x-1, y)): path = "L" + path
        if (path_coords[index+1] == (x+1, y)): path = "R" + path
        if (path_coords[index+1] == (x, y-1)): path = "U" + path
        if (path_coords[index+1] == (x, y+1)): path = "D" + path

    path = path[::-1]

    return path

def calculate_path(snake, end):
    start = snake[0]
    count = 0
    open_set = queue.PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {(x, y): float("inf") for x in range(0, X) for y in range(0, Y)}
    g_score[start] = 0
    f_score = {(x, y): float("inf") for x in range(0, X) for y in range(0, Y)}
    f_score[start] = h(start, end)

    open_set_hash = {start}

    closed = snake.copy()
    been_there = []

    while not open_set.empty():
        current = open_set.get()[2]
        been_there.append(current)
        open_set_hash.remove(current)
        if current == end:
            return reconstruct_path(came_from, end)

        for neighbor in get_neighbors(current, closed):
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor, end)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

        if current != start:
            closed.append(neighbor)

def get_indexes(cycle, prey, tail, up, down, left, right):
    up_index = -1
    down_index = -1
    left_index = -1
    right_index = -1

    for index, coord in enumerate(cycle):
        if coord == prey:
            prey_index = index
        elif coord == tail:
            tail_index = index
        if coord == up:
            up_index = index
        elif coord == down:
            down_index = index
        elif coord == left:
            left_index = index
        elif coord == right:
            right_index = index

    return prey_index, tail_index, up_index, down_index, left_index, right_index

def snake_brain(snake, prey, curr_path, cycle, index):
    new_x = snake[0][0]
    new_y = snake[0][1]

    if (snake[0] == cycle[index]):
        index += 1
        if (index == len(cycle)):
            index = 0
        curr_path = calculate_path(snake, cycle[index])

    if curr_path == None:
        return True, snake, prey, curr_path, cycle, index
        
    move = curr_path[0]
    if (move == 'U'):
        new_y -= 1
    elif (move == 'D'):
        new_y += 1
    elif (move == 'L'):
        new_x -= 1
    elif (move == 'R'):
        new_x += 1

    for coord in snake:
        if ((new_x, new_y) == coord):
            print("you lose with score:", len(snake) - STARTING_LEN)
            return True, snake, prey, curr_path[1:], cycle, 0
    
    if (new_x < 0 or new_x >= X or new_y < 0 or new_y >= Y):
        print("you lose with score:", len(snake) - STARTING_LEN)
        return True, snake, prey, curr_path[1:], cycle, 0

    snake.insert(0, (new_x, new_y))

    if ((new_x, new_y) == prey):
        prey = spawn_prey(snake)
    else:
        snake.pop()
        curr_path = curr_path[1:]

    prey_index, tail_index, up, down, left, right = get_indexes(cycle, prey, snake[len(snake)-1], (new_x, new_y-1), (new_x, new_y+1), (new_x-1, new_y), (new_x+1, new_y))
    moves = [up, down, left, right]

    if (len(snake) < (X * Y) // 1.8):
        max = -1
        if (prey_index > index and len(snake) < (X * Y) // 3):
            for move in moves:
                if move > index and move < prey_index and move > max:
                    if (tail_index > index):
                        if (move < tail_index):
                            max = move
                    else:
                        max = move

        elif (prey_index > index and ((tail_index > prey_index and tail_index > index) or (tail_index < prey_index and tail_index < index))):
            for move in moves:
                if move > index and move < prey_index and move > max:
                    max = move

        elif (prey_index < index):
            for move in moves:
                if move > index and move > max:
                    if (tail_index > index):
                        if (move < tail_index):
                            max = move
                    else:
                        max = move
        if max != -1:
            index = max
            curr_path = calculate_path(snake, cycle[index])

    return False, snake, prey, curr_path, cycle, index

def generate_cycle():
    nodes = create_nodes()
    edges = create_edges()
    final_edges = prims_algoritm(edges)
    cycle = hamiltonian_cycle(nodes, final_edges)

    return cycle

def main():
    pygame.display.set_caption("Snake Game AI")
    clock = pygame.time.Clock()
    snake = [(0, 0), (0, 1), (0, 2)]
    prey = spawn_prey(snake)

    cycle = generate_cycle()
    index = 0

    path = calculate_path(snake, cycle[index])

    lost = False
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if not lost:
            lost, snake, prey, path, cycle, index = snake_brain(snake, prey, path, cycle, index)
            draw_window(snake, prey, cycle)

    pygame.quit()

main()
