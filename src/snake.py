"""Snake class for Learn2Slither"""


class Snake:
    """Represents the snake in the game"""

    directions = { "LEFT": (-1, 0), "RIGHT": (1, 0), "UP": (0, -1), "DOWN": (0, 1) }

    def __init__(self, body=None):
        """
        Initialize snake with body segments
        
        Args:
            body: list of (x, y) tuples starting with head
                  If None, starts with single head at (0, 0)
        
        body[0] = head
        body[1:] = other segments
        """
        self.body = body if body is not None else [(0, 0)]
        self._last_tail = None  # Used for grow()

    @property
    def head(self):
        """Get head position (x, y)"""
        return self.body[0]

    @property
    def length(self):
        """Get snake length"""
        return len(self.body)

    def move(self, moveDirection):
        """
        Move snake in direction
        
        Args:
            moveDirection: String "UP", "DOWN", "LEFT", or "RIGHT"
        """
        direction = self.directions[moveDirection]
        
        x, y = self.head
        new_head = (x + direction[0], y + direction[1])
        # Add new head
        self.body.insert(0, new_head)
        self._last_tail = self.body.pop()

    def grow(self):
        """
        Grow snake by 1 segment
        After move(), the tail was removed and saved in _last_tail.
        We add it back to increase length.
        """
        if self._last_tail is not None:
            self.body.append(self._last_tail)

    def shrink(self):
        """Shrink snake by 1 segment"""
        if len(self.body) > 0:
            self.body.pop()

    def check_collision_wall(self, mapsize):
        """Check if head hits a wall (outside boundaries)"""
        x, y = self.head
        # Map goes from 0 to mapsize+1 (walls at boundaries)
        # Valid space: 1 to mapsize
        return x < 1 or x > mapsize or y < 1 or y > mapsize

    def check_collision_self(self):
        """Check if head collides with body"""
        head = self.head
        # Check if head is in body (excluding head itself)
        return head in self.body[1:]

    def get_vision(self, map_grid, apples, mapsize=10):
        """
        Get what the snake sees in 4 directions
        Compact representation: for each direction, return distance to obstacle
        and whether there are apples nearby
        
        Args:
            map_grid: The game map (with walls)
            apples: List of apple tuples (type, (x, y))
            mapsize: Size of play area (without walls)
        
        Returns:
            dict with keys 'UP', 'DOWN', 'LEFT', 'RIGHT'
            Each value is a tuple: (obstacle_dist, has_green, has_red)
            obstacle_dist: 1-9 (closer is worse), 10 = far away
        """
        x, y = self.head
        
        # Extract apple positions by type
        green_positions = set(pos for atype, pos in apples if atype == "G")
        red_positions = set(pos for atype, pos in apples if atype == "R")
        
        vision = {}
        
        for direction_name, (dx, dy) in self.directions.items():
            obstacle_dist = 10  # Default: no obstacle detected
            has_green = False
            has_red = False
            
            # Look ahead in this direction
            for distance in range(1, 11):  # Look up to 10 cells ahead
                look_x = x + dx * distance
                look_y = y + dy * distance
                
                # Check for wall (boundary) - walls at positions 0 and mapsize+1
                if look_x < 1 or look_x > mapsize or look_y < 1 or look_y > mapsize:
                    if obstacle_dist == 10:  # First obstacle found
                        obstacle_dist = distance
                    break
                
                # Check what's at this position
                pos = (look_x, look_y)
                
                # Check for body collision
                if pos in self.body[1:]:
                    if obstacle_dist == 10:
                        obstacle_dist = distance
                    continue
                
                # Check for apples
                if pos in green_positions:
                    has_green = True
                elif pos in red_positions:
                    has_red = True
            
            # Cap obstacle distance at 9 for consistency
            obstacle_dist = min(obstacle_dist, 9)
            vision[direction_name] = (obstacle_dist, has_green, has_red)
        
        return vision
