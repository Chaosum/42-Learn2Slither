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
        """
        Generate a random position for an entity on the map
        Does NOT modify the map - self.apples is the source of truth
        
        Returns:
            Tuple (x, y) of the generated position
        """
        # Occupied positions: snake body + existing apples
        occupied = set(self.snake.body if hasattr(self, 'snake') else [])
        occupied.update(pos for _, pos in self.apples)
        
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            x = random.randint(1, self.mapsize)
            y = random.randint(1, self.mapsize)
            pos = (x, y)
            
            if pos not in occupied:
                return pos
            attempts += 1
        
        # Fallback: find first available position (shouldn't happen)
        for y in range(1, self.mapsize + 1):
            for x in range(1, self.mapsize + 1):
                if (x, y) not in occupied:
                    return (x, y)
        
        # Emergency fallback
        return (1, 1)
    
    def generate_snake_position(self):
        """
        Generate initial snake body with 3 contiguous segments
        Places randomly and places segments on the map
        
        Returns:
            Tuple (body, direction) where:
            - body: List of 3 (x, y) tuples: [head, segment2, segment3]
            - direction: str - "UP", "DOWN", "LEFT", or "RIGHT"
        """
        while True:
            # Random starting position anywhere on the map
            x = random.randint(1, len(self.map) - 2)
            y = random.randint(1, len(self.map) - 2)
            
            # Random direction: 0=RIGHT, 1=LEFT, 2=DOWN, 3=UP
            direction_idx = random.randint(0, 3)
            
            if direction_idx == 0:  # Horizontal RIGHT
                body = [(x, y), (x - 1, y), (x - 2, y)]
                direction = "RIGHT"
            elif direction_idx == 1:  # Horizontal LEFT
                body = [(x, y), (x + 1, y), (x + 2, y)]
                direction = "LEFT"
            elif direction_idx == 2:  # Vertical DOWN
                body = [(x, y), (x, y - 1), (x, y - 2)]
                direction = "DOWN"
            else:  # Vertical UP
                body = [(x, y), (x, y + 1), (x, y + 2)]
                direction = "UP"
            
            # Check if all positions are valid (empty and within bounds)
            if all(1 <= seg_x < len(self.map) - 1 and 
                   1 <= seg_y < len(self.map) - 1 and 
                   self.map[seg_y][seg_x] == "0" 
                   for seg_x, seg_y in body):
                # Place snake on map
                for i, (seg_x, seg_y) in enumerate(body):
                    self.map[seg_y][seg_x] = "H" if i == 0 else "s"
                return body, direction

    def compute_vision(self):
        """
        Compute snake's vision - ONLY what the snake can see
        Returns only visible apples and obstacles in each direction
        
        Returns:
            dict with keys 'UP', 'DOWN', 'LEFT', 'RIGHT'
            Each value is a tuple: (obstacle_dist, has_green, has_red)
        """
        x, y = self.snake.head
        directions = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
        
        # Extract apple positions by type
        green_positions = set(pos for atype, pos in self.apples if atype == "G")
        red_positions = set(pos for atype, pos in self.apples if atype == "R")
        
        vision = {}
        
        for direction_name, (dx, dy) in directions.items():
            obstacle_dist = 10
            has_green = False
            has_red = False
            
            # Look ahead in this direction
            for distance in range(1, 11):
                look_x = x + dx * distance
                look_y = y + dy * distance
                
                # Check for wall (boundary)
                if look_x < 1 or look_x > self.mapsize or look_y < 1 or look_y > self.mapsize:
                    if obstacle_dist == 10:
                        obstacle_dist = distance
                    break
                
                # Check for snake body collision
                pos = (look_x, look_y)
                if pos in self.snake.body[1:]:
                    if obstacle_dist == 10:
                        obstacle_dist = distance
                    continue
                
                # Check for apples ONLY in vision
                if pos in green_positions:
                    has_green = True
                elif pos in red_positions:
                    has_red = True
            
            # Cap at 9
            obstacle_dist = min(obstacle_dist, 9)
            vision[direction_name] = (obstacle_dist, has_green, has_red)
        
        return vision

    def _has_visible_green_apple(self, vision):
        """
        Check if any green apple is visible in the snake's vision
        
        Args:
            vision: Dict from compute_vision()
            
        Returns:
            True if at least one green apple is visible
        """
        return any(has_green for _, has_green, _ in vision.values())

    def __init__(self, mapsize=10):
        """Initialize the game"""
        self.mapsize = mapsize
        self.running = False
        self.apples = []
        self.steps_since_eaten = 0
        
        # Opposite directions mapping
        self.opposite_directions = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT"
        }

        # Initialize map (creates map, places snake, creates apples)
        snake_body, initial_direction = self.initmap(mapsize)
        self.snake = Snake(snake_body)
        self.last_direction = initial_direction  # Track the initial direction


    def step(self, action):
        """
        Execute one game step
        Args:
            action: str - "UP", "DOWN", "LEFT", "RIGHT"
        Returns:
            vision: dict or None - Snake's vision if alive
            reward: float - Reward based on snake length change
            status: str - "OK", "WALL", "SELF", "ZERO_LENGTH"
        """
        # Prevent opposite direction (demi-tour) - ignore the action
        if action == self.opposite_directions[self.last_direction]:
            # Keep moving in last direction instead
            action = self.last_direction
        
        self.last_direction = action
        
        # Get vision BEFORE moving (compute in game, not expose full map to snake)
        vision_before = self.compute_vision()
        
        # Track snake length before action
        length_before = len(self.snake.body)
        
        self.snake.move(action)
        
        if self.snake.check_collision_wall(self.mapsize):
            return None, -10000, "WALL"

        if self.snake.check_collision_self():
            return None, -10000, "SELF"

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
            # Reset inactivity counter
            self.steps_since_eaten = 0
        else:
            # Increment inactivity counter
            self.steps_since_eaten += 1

        if len(self.snake.body) == 0:
            return None, -10000, "ZERO_LENGTH"
        # If snake hasn't eaten for 200 steps, it's likely stuck in a loop
        if self.steps_since_eaten > 200:
            return None, -10000, "STARVED"

        # Get vision AFTER moving
        vision_after = self.compute_vision()

        length_after = len(self.snake.body)
        length_change = length_after - length_before
        
        if length_change > 0:
            # Snake grew: +100 per segment gained
            reward = length_change * 100
        else:
            inactivity_penalty = max(0, (self.steps_since_eaten - 20) * 0.5)
            reward = -1 - inactivity_penalty
        
            apple_was_visible = self._has_visible_green_apple(vision_before)
            apple_is_visible = self._has_visible_green_apple(vision_after)
            
            if apple_was_visible and not apple_is_visible:
                reward -= 10.0
            elif apple_was_visible and apple_is_visible:
                reward += 5
        
        return vision_after, reward, "OK"

    def render(self):
        """
        Display the current game state to console
        """
        print("\n" + "=" * 30)
        print(f"Snake: {len(self.snake.body)} segments | Apples: {len(self.apples)}")
        print("=" * 30)
        
        # Copy map for display
        display_map = [row[:] for row in self.map]
        
        # Place snake on map
        for i, (x, y) in enumerate(self.snake.body):
            if i == 0:
                display_map[y][x] = "H"  # Snake head
            else:
                display_map[y][x] = "s"  # Snake body
        
        # Place apples on map
        for apple_type, (x, y) in self.apples:
            display_map[y][x] = apple_type
        
        # Print map
        for row in display_map:
            print(" ".join(row))
        
        print("=" * 30)


def display_vision_2d(vision):
    """
    Display snake vision in 2D crosshair format
    Args:
        vision: Dict from compute_vision() with keys 'UP', 'DOWN', 'LEFT', 'RIGHT'
                Each value is a tuple: (obstacle_dist, has_green, has_red)
    Returns:
        String with 2D visualization
    Example:
           W
           0
           G
    W000000H0W
           0
           0
    """
    lines = []
    
    # UP direction (vertical)
    up_dist, up_green, up_red = vision['UP']
    for i in range(1, up_dist):
        char = "G" if up_green else "0"
        lines.append(f"       {char}")
    lines.append(f"       W" if up_dist <= 9 else "       0")
    
    # MIDDLE line: LEFT + HEAD + RIGHT
    left_dist, left_green, left_red = vision['LEFT']
    right_dist, right_green, right_red = vision['RIGHT']
    
    left_str = "".join(["G" if left_green else "0" for _ in range(1, left_dist)])
    left_str = left_str[::-1]  # Reverse to show left-to-right
    left_str += "W" if left_dist <= 9 else "0"
    
    right_str = "W" if right_dist <= 9 else "0"
    right_str += "".join(["G" if right_green else "0" for _ in range(1, right_dist)])
    
    middle = f"{left_str}H{right_str}"
    lines.append(middle)
    
    # DOWN direction (vertical)
    down_dist, down_green, down_red = vision['DOWN']
    lines.append(f"       W" if down_dist <= 9 else "       0")
    for i in range(1, down_dist):
        char = "G" if down_green else "0"
        lines.append(f"       {char}")
    
    return "\n".join(lines)
