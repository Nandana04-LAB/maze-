import random
import svgwrite
import heapq
import math

class MazeNode:
    def __init__(self, row, col):
        # Coordinates of the node in the maze
        self.row = row
        self.col = col
        # Pointers to adjacent nodes (up, down, left, right)
        self.left = None
        self.right = None
        self.up = None
        self.down = None
        # Attributes for pathfinding
        self.distance = float('inf')  # Distance from the start node (initialized as infinity)
        self.visited = False  # Flag to track if the node has been visited
        self.is_enemy = False  # Flag to indicate if the node contains an enemy

    def __lt__(self, other):
        return self.distance < other.distance

# Generate a random maze layout
def generate_random_maze(rows, cols, num_enemies=10, num_rewards=5):
    maze = [[MazeNode(row, col) for col in range(cols)] for row in range(rows)]

    # Create random connections between adjacent cells
    for row in range(rows):
        for col in range(cols):
            if col < cols - 1 and random.choice([True, False]):
                maze[row][col].right = maze[row][col + 1]
                maze[row][col + 1].left = maze[row][col]
            if row < rows - 1 and random.choice([True, False]):
                maze[row][col].down = maze[row + 1][col]
                maze[row + 1][col].up = maze[row][col]

    # Add random enemies to the maze
    for _ in range(num_enemies):
        enemy_row = random.randint(0, rows - 1)
        enemy_col = random.randint(0, cols - 1)
        maze[enemy_row][enemy_col].is_enemy = True

    return maze

# Generate a random starting point on the border of the maze
def generate_start_on_border(rows, cols):
    return (random.randint(1, rows - 2), 0)

# Generate a random ending point on the border of the maze, avoiding the start
def generate_end_on_border(rows, cols, start):
    # Randomly choose a side for the end point and ensure it's different from the start point's side
    # Adjust the end point's position based on the start point
    # If the chosen side is not valid, recursively find a new end point
    # (Avoid having start and end points on the same side)
    # Finally, return the generated end point
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top" and start[0] != 0:
        return (0, random.randint(1, cols - 2))
    elif side == "bottom" and start[0] != rows - 1:
        return (rows - 1, random.randint(1, cols - 2))
    elif side == "left" and start[1] != 0:
        return (random.randint(1, rows - 2), 0)
    elif side == "right" and start[1] != cols - 1:
        return (random.randint(1, rows - 2), cols - 1)
    else:
        return generate_end_on_border(rows, cols, start)

# Define a heuristic function for A* search
def heuristic(node, end):
    return math.sqrt(abs((node.row - end[0]) * 2 + (node.col - end[1]) * 2))

# Implement the A* search algorithm to find the shortest path
def astar(maze, start, end):
    # Initialize distances and visited flags for all nodes in the maze
    for row in maze:
        for node in row:
            node.visited = False
            node.distance = float('inf')

    # Get the start and end nodes from the maze
    start_node = maze[start[0]][start[1]]
    end_node = maze[end[0]][end[1]]

    # Initialize priority queue with the start node and its heuristic value
    priority_queue = [(0 + heuristic(start_node, end), 0, start_node)]

    # A* search loop
    while priority_queue:
        # Pop the node with the lowest combined cost (f = g + h) from the priority queue
        current_f, current_g, current_node = heapq.heappop(priority_queue)

        # Skip if the node has already been visited
        if current_node.visited:
            continue

        # Mark the current node as visited and update its distance from the start
        current_node.visited = True
        current_node.distance = current_g

        # Explore neighbors of the current node
        neighbors = [current_node.left, current_node.right, current_node.up, current_node.down]
        for neighbor in filter(None, neighbors):
            # Check if the neighbor is not visited and is not an enemy
            if not neighbor.visited and not neighbor.is_enemy:
                # Calculate the new tentative distance from the start
                new_g = current_g + 1
                # If the new distance is shorter, update the neighbor's distance and add it to the priority queue
                if new_g < neighbor.distance:
                    neighbor.distance = new_g
                    heapq.heappush(priority_queue, (new_g + heuristic(neighbor, end), new_g, neighbor))

    # If the end node's distance is still infinity, there is no path
    if end_node.distance == float('inf'):
        return None

    # Reconstruct and return the path from end to start
    path = []
    current_node = end_node
    while current_node != start_node:
        path.append((current_node.row, current_node.col))
        neighbors = [current_node.left, current_node.right, current_node.up, current_node.down]
        # Filter out neighbors that are enemies
        valid_neighbors = [n for n in neighbors if n and not n.is_enemy]
        # Move to the neighbor with the minimum distance
        current_node = min(valid_neighbors, key=lambda x: x.distance)

    # Include the start node in the path and reverse the list
    path.append((start_node.row, start_node.col))
    return list(reversed(path))

# Add enemies randomly along the given path in the maze
def add_enemies_along_path(maze, path, num_enemies):
    enemies_added = 0
    for _ in range(num_enemies):
        random_index = random.randint(1, len(path) - 2)
        row, col = path[random_index]
        if not maze[row][col].is_enemy:
            maze[row][col].is_enemy = True
            enemies_added += 1
    return enemies_added

# Visualize the maze, path, start and end points, and enemies in an SVG file
def visualize_maze_svg(maze, path, start, end, enemies, file_name='maze_with_paths.svg'):
    # Define parameters for SVG drawing
    cell_size = 20
    padding = 2
    maze_width = cell_size * len(maze[0])
    maze_height = cell_size * len(maze)

    # Create a small rectangle as the box beside the maze
    box_width = 350
    box_height = 90
    box_x = maze_width + padding
    box_y = padding

    # Create an SVG drawing object
    dwg = svgwrite.Drawing(file_name, profile='tiny')
    dwg.viewbox(0, 0, maze_width + box_width + padding, maze_height + padding)

    # Draw the maze
    #By using enumerate, we can simultaneously access the index of each row and column
    #while iterating through the maze, which is helpful for determining the position of each cell in the SVG output.
    for row_index, row in enumerate(maze):
        for col_index, node in enumerate(row):
            x = col_index * cell_size
            y = row_index * cell_size

            # Draw maze walls
            #For a vertical line, the x-coordinate remains the same (representing the start and end on the same vertical line),
            #while the y-coordinate changes to draw the line from the top to the bottom of the cell.
            if node.left is None:
                dwg.add(dwg.line((x, y), (x, y + cell_size), stroke=svgwrite.rgb(0, 0, 0, '%')))
            if node.right is None:
                dwg.add(dwg.line((x + cell_size, y), (x + cell_size, y + cell_size), stroke=svgwrite.rgb(0, 0, 0, '%')))
            if node.up is None:
                dwg.add(dwg.line((x, y), (x + cell_size, y), stroke=svgwrite.rgb(0, 0, 0, '%')))
            if node.down is None:
                dwg.add(dwg.line((x, y + cell_size), (x + cell_size, y + cell_size), stroke=svgwrite.rgb(0, 0, 0, '%')))

            # Draw enemies as bombs
            if node.is_enemy:
                ghost_size = cell_size / 1.5
                ghost_x = x + cell_size / 2 - ghost_size / 2
                ghost_y = y + cell_size / 1 - ghost_size / 2
                dwg.add(dwg.text('💣', insert=(ghost_x, ghost_y), font_size=ghost_size, fill=svgwrite.rgb(120, 0, 120, '%')))

    # Draw the path
    if path:
        for i in range(len(path) - 1):
            row1, col1 = path[i]
            row2, col2 = path[i + 1]
            x1, y1 = col1 * cell_size + cell_size / 2, row1 * cell_size + cell_size / 2
            x2, y2 = col2 * cell_size + cell_size / 2, row2 * cell_size + cell_size / 2
            dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(0, 0, 255, '%'), stroke_width=4))

    # Draw start and end points
    #to calculate its center coordinates in the maze grid. 
    #This process ensures that the start and end points are positioned at the center of their respective cells
    start_x, start_y = start[1] * cell_size + cell_size / 2, start[0] * cell_size + cell_size / 2
    end_x, end_y = end[1] * cell_size + cell_size / 2, end[0] * cell_size + cell_size / 2

    dwg.add(dwg.text('🚩', insert=(start_x - cell_size / 4, start_y - cell_size / 4),
                     font_size=cell_size / 2, fill=svgwrite.rgb(255, 0, 0, '%')))
    dwg.add(dwg.text('🏁', insert=(end_x - cell_size / 4, end_y - cell_size / 4),
                     font_size=cell_size / 2, fill=svgwrite.rgb(0, 255, 0, '%')))

    # Draw enemies' paths
    if enemies:
        for i in range(len(enemies) - 1):
            row1, col1 = enemies[i]
            row2, col2 = enemies[i + 1]
            x1, y1 = col1 * cell_size + cell_size / 2, row1 * cell_size + cell_size / 2
            x2, y2 = col2 * cell_size + cell_size / 2, row2 * cell_size + cell_size / 2
            dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(0, 255, 0, '%'), stroke_width=4))

    # Draw a small rectangle as the box beside the maze
    dwg.add(dwg.rect(insert=(box_x, box_y), size=(box_width, box_height),
                     fill=svgwrite.rgb(240, 240, 240, '%'), stroke=svgwrite.rgb(0, 0, 0, '%')))

    # Add notes indicating the paths and the presence of enemies
    #By adding a padding value, we ensures that there is a specified amount of space between box_x and note_x. 
    #This can be useful for creating visual separation or alignment within the layout or design being implemented.
    note_x = box_x + padding
    note_y = box_y + box_height-(box_height-12)
    dwg.add(dwg.line(start=(note_x, note_y), end=(note_x + 20, note_y), stroke=svgwrite.rgb(0, 0, 255, '%'),stroke_width=4))
    dwg.add(dwg.text('Shortest Path', insert=(note_x + 25, note_y + 5), font_size=20, font_weight='bold',
                     fill=svgwrite.rgb(0, 0, 0, '%')))
    note_x = box_x + padding
    note_y = box_y + box_height-(box_height-44)
    dwg.add(dwg.line(start=(note_x, note_y), end=(note_x + 20, note_y), stroke=svgwrite.rgb(0,255 ,0, '%'),stroke_width=4))
    dwg.add(dwg.text('Shortest Path Avoiding Enemies', insert=(note_x + 25, note_y + 5), font_size=20, font_weight='bold',
                     fill=svgwrite.rgb(0, 0, 0, '%')))

    note_x = box_x + padding
    note_y = box_y + box_height-(box_height-80)
    dwg.add(dwg.text(' 💣 Enemies', insert=(note_x , note_y ), font_size=20, font_weight='bold',
                     fill=svgwrite.rgb(0, 0, 0, '%')))
    dwg.save()
# Generate a new maze, find the shortest path, add enemies, and visualize the results
def generate_a_new_maze():
    rows, cols = 20,20  # Adjust the size of the maze as needed
    random_num_rows = random.randint(1, 10) + rows
    random_num_cols = random.randint(1, 10) + cols
    # Generate a random number of enemies
    random_num_enemies = 0

    print("Generating a new maze")
    # Generate a random maze layout
    random_maze = generate_random_maze(rows, cols, num_enemies=random_num_enemies)
    # Generate a random starting point on the border
    start_point = generate_start_on_border(rows, cols)
    # Generate a random ending point on the border, avoiding the start
    end_point = generate_end_on_border(rows, cols, start_point)

    try:
        # Find the shortest path in the maze using A*
        shortest_path = astar(random_maze, start_point, end_point)

        if shortest_path is not None:
            # Add two enemies randomly along the path
            enemies_added = add_enemies_along_path(random_maze, shortest_path, num_enemies=2)

            if enemies_added == 2:
                # Find a new shortest path after adding enemies
                new_shortest_path = astar(random_maze, start_point, end_point)

                if new_shortest_path is not None:
                    # Visualize the maze with paths and enemies
                    visualize_maze_svg(random_maze, shortest_path, start_point, end_point, new_shortest_path,
                                        file_name='maze_with_paths.svg')
                    # Print information about the maze, paths, and enemies
                    print("\nStart Point:", start_point)
                    print("End Point:", end_point)
                    print("\nNumber of rows:", random_num_rows)
                    print("Number of Columns:", random_num_cols)
                    print("Number of Enemies:", random_num_enemies)
                    print("Shortest Path (Original):", shortest_path)
                    print("Shortest Path (Avoiding Enemies):", new_shortest_path)

                else:
                    print("No path found after adding enemies.")
                    # Try generating a new maze
                    generate_a_new_maze()
                    

            else:
                print("Failed to add enemies along the path.")
                # Try generating a new maze
                generate_a_new_maze()

        else:
            print("No path found from start to end.")
            # Try generating a new maze
            generate_a_new_maze()

    except ValueError as e:
        print("Error: " + str(e))

# Call the function to generate a new maze and visualize it
generate_a_new_maze()