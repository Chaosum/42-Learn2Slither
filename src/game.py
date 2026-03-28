import random
from src.snake import Snake


class Game:
    """Game class for Learn2Slither"""

    def initmap(self, mapsize=1):
        """Initialize a square map of size n x n (only walls and empty spaces)"""
        self.map = [
            ["W" if (i == 0 or i == mapsize + 1 or
                     j == 0 or j == mapsize + 1) else "0"
             for j in range(mapsize + 2)]
            for i in range(mapsize + 2)
        ]
        snake_pos, initial_direction = self.generate_snake_position()
        # Original config: 2 green + 1 red
        self.apples.append(("G", self.generate_apples("G")))
        self.apples.append(("G", self.generate_apples("G")))
        self.apples.append(("R", self.generate_apples("R")))
        return snake_pos, initial_direction

    def generate_apples(self, entity="G"):
        occupied = set(self.snake.body if hasattr(self, 'snake') else [])
        occupied.update(pos for _, pos in self.apples)
        
        max_attempts = 100
        for attempt in range(max_attempts):
            x = random.randint(1, self.mapsize)
            y = random.randint(1, self.mapsize)
            pos = (x, y)
            
            if pos not in occupied:
                return pos
        
        # Fallback: brute force search
        for y in range(1, self.mapsize + 1):
            for x in range(1, self.mapsize + 1):
                if (x, y) not in occupied:
                    return (x, y)
        return (1, 1)
    
    def generate_snake_position(self):
        while True:
            x = random.randint(1, len(self.map) - 2)
            y = random.randint(1, len(self.map) - 2)
            direction_idx = random.randint(0, 3)
            
            if direction_idx == 0:
                body = [(x, y), (x - 1, y), (x - 2, y)]
                direction = "RIGHT"
            elif direction_idx == 1:
                body = [(x, y), (x + 1, y), (x + 2, y)]
                direction = "LEFT"
            elif direction_idx == 2:
                body = [(x, y), (x, y - 1), (x, y - 2)]
                direction = "DOWN"
            else:
                body = [(x, y), (x, y + 1), (x, y + 2)]
                direction = "UP"
            
            if all(1 <= seg_x < len(self.map) - 1 and 
                   1 <= seg_y < len(self.map) - 1 and 
                   self.map[seg_y][seg_x] == "0" 
                   for seg_x, seg_y in body):
                for i, (seg_x, seg_y) in enumerate(body):
                    self.map[seg_y][seg_x] = "H" if i == 0 else "s"
                return body, direction

    def compute_vision(self):
        x, y = self.snake.head
        directions = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
        green_positions = set(pos for atype, pos in self.apples if atype == "G")
        red_positions = set(pos for atype, pos in self.apples if atype == "R")
        
        vision = {}
        
        for direction_name, (dx, dy) in directions.items():
            obstacle_dist = self.mapsize + 1
            green_dist = self.mapsize + 1
            red_dist = self.mapsize + 1
            
            for distance in range(1, self.mapsize + 2):
                look_x = x + dx * distance
                look_y = y + dy * distance
                
                if look_x < 1 or look_x > self.mapsize or look_y < 1 or look_y > self.mapsize:
                    if obstacle_dist == self.mapsize + 1:
                        obstacle_dist = distance
                    break
                
                pos = (look_x, look_y)
                if pos in self.snake.body[1:]:
                    if obstacle_dist == self.mapsize + 1:
                        obstacle_dist = distance
                    continue
                
                if pos in green_positions and green_dist == self.mapsize + 1:
                    green_dist = distance
                elif pos in red_positions and red_dist == self.mapsize + 1:
                    red_dist = distance
            
            # Original format: (obstacle_distance_0-9, has_green_bool, has_red_bool)
            bucketized_obstacle = int((min(obstacle_dist, self.mapsize) / self.mapsize) * 9) if obstacle_dist <= self.mapsize else 9
            has_green = green_dist <= self.mapsize
            has_red = red_dist <= self.mapsize
            
            vision[direction_name] = (bucketized_obstacle, has_green, has_red)
        
        return vision

    def print_vision_debug(self, direction_chosen=None):
        """Display a perfect cross vision centered on snake head H"""
        snake_head = self.snake.head
        snake_body = set(self.snake.body[1:])
        green_apples = {pos for atype, pos in self.apples if atype == "G"}
        red_apples = {pos for atype, pos in self.apples if atype == "R"}
        
        head_x, head_y = snake_head
        output = []
        
        # Display the cross (vertical line with horizontal line through head)
        for y in range(len(self.map)):
            if y == head_y:
                # Horizontal line at snake's Y position
                row = ""
                for x in range(len(self.map[0])):
                    pos = (x, head_y)
                    if pos == snake_head:
                        row += "H"
                    elif pos in snake_body:
                        row += "S"
                    elif pos in green_apples:
                        row += "G"
                    elif pos in red_apples:
                        row += "R"
                    elif self.map[head_y][x] == "W":
                        row += "W"
                    else:
                        row += "0"
                output.append(row)
            else:
                # Vertical line parts (other rows), perfectly aligned
                pos = (head_x, y)
                if pos == snake_head:
                    col_char = "H"
                elif pos in snake_body:
                    col_char = "S"
                elif pos in green_apples:
                    col_char = "G"
                elif pos in red_apples:
                    col_char = "R"
                elif self.map[y][head_x] == "W":
                    col_char = "W"
                else:
                    col_char = "0"
                
                # Align vertically with spaces
                output.append(" " * head_x + col_char)
        
        # Add decision if provided
        if direction_chosen:
            output.append("")
            output.append(f"Decision: {direction_chosen}")
        
        return "\n".join(output)
    
    def _has_visible_green_apple(self, vision):
        return any(has_green for _, has_green, _ in vision.values())

    def __init__(self, mapsize=10):
        self.mapsize = mapsize
        self.running = False
        self.apples = []
        self.steps_since_eaten = 0
        self.opposite_directions = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT"
        }
        snake_body, initial_direction = self.initmap(mapsize)
        self.snake = Snake(snake_body)
        self.last_direction = initial_direction


    def step(self, action):
        if action == self.opposite_directions[self.last_direction]:
            action = self.last_direction
        
        self.last_direction = action
        vision_before = self.compute_vision()
        length_before = len(self.snake.body)
        
        self.snake.move(action)
        
        if self.snake.check_collision_wall(self.mapsize):
            return None, -1000, "WALL"

        if self.snake.check_collision_self():
            return None, -1000, "SELF"

        head = self.snake.body[0]
        eaten_apple = None

        for apple in self.apples:
            if head == apple[1]:
                eaten_apple = apple
                break

        if eaten_apple:
            apple_type = eaten_apple[0]
            self.apples.remove(eaten_apple)

            if apple_type == "G":
                self.snake.grow()
            elif apple_type == "R":
                self.snake.shrink()
            # Respawn new apple of same type
            new_pos = self.generate_apples(apple_type)
            self.apples.append((apple_type, new_pos))
            self.steps_since_eaten = 0
        else:
            self.steps_since_eaten += 1

        if len(self.snake.body) == 0:
            return None, -1000, "ZERO_LENGTH"
        if self.steps_since_eaten > 400:
            return None, -500, "STARVED"

        vision_after = self.compute_vision()
        length_after = len(self.snake.body)
        length_change = length_after - length_before
        
        if length_change > 0:
            reward = length_change * 200
        else:
            inactivity_penalty = max(0, (self.steps_since_eaten - 50) * 0.1)
            reward = -0.5 - inactivity_penalty + 0.1
        
            apple_was_visible = self._has_visible_green_apple(vision_before)
            apple_is_visible = self._has_visible_green_apple(vision_after)
            
            if apple_was_visible and not apple_is_visible:
                reward -= 5.0
            elif apple_was_visible and apple_is_visible:
                reward += 10
        
        return vision_after, reward, "OK"

    def render(self):
        print("\n" + "=" * 30)
        print(f"Snake: {len(self.snake.body)} segments | Apples: {len(self.apples)}")
        print("=" * 30)
        
        display_map = [row[:] for row in self.map]
        
        for i, (x, y) in enumerate(self.snake.body):
            display_map[y][x] = "H" if i == 0 else "s"
        
        for apple_type, (x, y) in self.apples:
            display_map[y][x] = apple_type
        
        for row in display_map:
            print(" ".join(row))
        
        print("=" * 30)
