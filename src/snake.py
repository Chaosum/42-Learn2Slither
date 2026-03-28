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


