import random
from src.snake import Snake


class Game:
    """Game class for Learn2Slither"""

    def initmap(self, mapsize=1):
        """Initialize a square map of size n x n"""
        self.map = [
            ["W" if (i == 0 or i == mapsize + 1 or
                     j == 0 or j == mapsize + 1) else "0"
             for j in range(mapsize + 2)]
            for i in range(mapsize + 2)
        ]
        snake_pos = self.generate_snake_position()
        # Original config: 2 green + 1 red
        self.apples.append(("G", self.generate_apples("G")))
        self.apples.append(("G", self.generate_apples("G")))
        self.apples.append(("R", self.generate_apples("R")))
        return snake_pos

    def generate_apples(self, entity="G"):
        """
        Generate a random position for an entity on the map
        
        Returns:
            Tuple (x, y) of the placed entity
        """
        while True:
            x = random.randint(1, len(self.map) - 2)
            y = random.randint(1, len(self.map) - 2)
            if self.map[y][x] == "0":
                self.map[y][x] = entity
                return (x, y)
    
    def generate_snake_position(self):
        """
        Generate a random position for the snake (at least 3 cells from walls)
        
        Returns:
            Tuple (x, y) of the placed snake
        """
        while True:
            x = random.randint(3, len(self.map) - 4)
            y = random.randint(3, len(self.map) - 4)
            if self.map[y][x] == "0":
                self.map[y][x] = "H"
                return (x, y)

    def _min_distance_to_green_apple(self):
        """Calculate Manhattan distance to closest green apple"""
        head_x, head_y = self.snake.head
        min_dist = float('inf')
        
        for apple_type, (apple_x, apple_y) in self.apples:
            if apple_type == "G":
                dist = abs(head_x - apple_x) + abs(head_y - apple_y)
                min_dist = min(min_dist, dist)
        
        return min_dist if min_dist != float('inf') else 20  # Max distance

    def __init__(self, mapsize=10):
        """Initialize the game"""
        self.mapsize = mapsize
        self.running = False
        self.apples = []
        self.steps_since_eaten = 0  # Track inactivity
        self.last_apple_distance = 20  # Track distance to apple

        # Create the map (also places all entities and populates apple list)
        snake_pos = self.initmap(mapsize)
        # Create Snake object
        self.snake = Snake(snake_pos[0], snake_pos[1])
        # Initialize apple distance after snake is created
        self.last_apple_distance = self._min_distance_to_green_apple()

    def update(self):
        """Update game state"""
        pass

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
        # Track snake length and apple distance before action
        length_before = len(self.snake.body)
        apple_distance_before = self.last_apple_distance
        
        # 1. Move snake
        self.snake.move(action)
        
        # 2. Check wall collision
        if self.snake.check_collision_wall(self.mapsize):
            return None, -10000, "WALL"

        # 3. Check self collision
        if self.snake.check_collision_self():
            return None, -10000, "SELF"

        # 4. Check apple collision and grow/shrink
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

        # 5. Check if snake died (length 0)
        if len(self.snake.body) == 0:
            return None, -10000, "ZERO_LENGTH"
        
        # 5b. Check starvation (too much inactivity = infinite loop behavior)
        # If snake hasn't eaten for 200 steps, it's likely stuck in a loop
        if self.steps_since_eaten > 200:
            return None, -10000, "STARVED"

        # 6. Update apple distance for next calculation
        self.last_apple_distance = self._min_distance_to_green_apple()
        
        # 7. Get vision FIRST (needed for reward calculation)
        vision = self.snake.get_vision(self.map, self.apples, self.mapsize)
        
        # 8. Calculate reward based on snake length change
        length_after = len(self.snake.body)
        length_change = length_after - length_before
        
        if length_change > 0:
            # Snake grew: +100 per segment gained
            reward = length_change * 100
        else:
            # No growth: movement cost + inactivity penalty
            inactivity_penalty = max(0, (self.steps_since_eaten - 20) * 0.5)
            reward = -1 - inactivity_penalty
            
            # Proximity bonus: reward for getting closer to green apple
            # BUT ONLY IF APPLE IS VISIBLE (in vision range 1-9)
            apple_visible = any(has_green for _, has_green, _ in vision.values())
            
            if apple_visible:
                apple_distance = self._min_distance_to_green_apple()
                if apple_distance < self.last_apple_distance:
                    # Got closer! Reward inversely proportional to distance
                    # Distance 1: +3.0, Distance 2: +2.0, Distance 3: +1.5
                    proximity_bonus = max(0.5, 3.5 - (apple_distance * 0.5))
                    reward += proximity_bonus
                elif apple_distance > self.last_apple_distance:
                    # Got further: small penalty
                    reward -= 0.3

        # 9. Return
        return vision, reward, "OK"

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
                display_map[y][x] = "S"  # Snake head
            else:
                display_map[y][x] = "s"  # Snake body
        
        # Place apples on map
        for apple_type, (x, y) in self.apples:
            display_map[y][x] = apple_type
        
        # Print map
        for row in display_map:
            print(" ".join(row))
        
        print("=" * 30)

    def handle_input(self):
        """Handle user input"""
        pass

    def run(self):
        """Main game loop"""
        self.running = True
        while self.running:
            self.handle_input()
            self.update()
            self.render()


def display_vision_2d(vision):
    """
    Display snake vision in 2D crosshair format
    Args:
        vision: Dict from snake.get_vision() with keys
            'up', 'down', 'left', 'right'
    Returns:
        String with 2D visualization
    Example:
           W
           0
           0
    W000000H0W
           S
           0
           0
    """
    up_line = vision['up']
    down_line = vision['down']
    left_line = vision['left']
    right_line = vision['right']
    
    lines = []
    
    # UP direction (vertical)
    for char in up_line[1:]:
        lines.append(f"       {char}")
    
    # MIDDLE line: LEFT + HEAD + RIGHT
    left_part = left_line[1:][::-1]  # Reverse to show left-to-right
    right_part = right_line[1:]
    middle = f"{left_part}H{right_part}"
    lines.append(middle)
    
    # DOWN direction (vertical)
    for char in down_line[1:]:
        lines.append(f"       {char}")
    
    return "\n".join(lines)
