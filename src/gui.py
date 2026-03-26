import tkinter as tk
from tkinter import Canvas


class GUI:
    """Graphical User Interface for Learn2Slither using tkinter"""

    def __init__(self, game, cell_size=30):
        """
        Initialize tkinter GUI
        
        Args:
            game: Game instance
            cell_size: Size of each grid cell in pixels
        """
        self.game = game
        self.cell_size = cell_size
        self.running = True
        
        # Colors
        self.WHITE = "#FFFFFF"
        self.BLACK = "#000000"
        self.GRAY = "#C8C8C8"
        self.GREEN = "#00FF00"
        self.RED = "#FF0000"
        self.BLUE = "#0000FF"
        self.DARK_BLUE = "#00008B"
        
        # Calculate window size
        map_width = len(game.map[0])
        map_height = len(game.map)
        canvas_width = map_width * cell_size
        canvas_height = map_height * cell_size
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Learn2Slither - Snake Game")
        self.root.geometry(f"{canvas_width}x{canvas_height + 60}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create canvas
        self.canvas = Canvas(
            self.root,
            width=canvas_width,
            height=canvas_height,
            bg=self.WHITE
        )
        self.canvas.pack()
        
        # Create info frame
        self.info_frame = tk.Frame(self.root, height=60, bg="#F0F0F0")
        self.info_frame.pack(fill=tk.X)
        
        # Info label
        self.info_label = tk.Label(
            self.info_frame,
            text="",
            bg="#F0F0F0",
            font=("Arial", 12)
        )
        self.info_label.pack(anchor=tk.W, padx=10, pady=10)
    
    def render(self, step=0, reward=0, status=""):
        """
        Render the game state
        
        Args:
            step: Current step number
            reward: Current reward
            status: Game status message
        """
        self.canvas.delete("all")
        
        # Draw grid
        map_grid = self.game.map
        for y, row in enumerate(map_grid):
            for x, cell in enumerate(row):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Draw cell border
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.GRAY)
                
                # Draw wall
                if cell == "W":
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self.BLACK,
                        outline=self.BLACK
                    )
        
        # Draw apples
        for apple_type, (x, y) in self.game.apples:
            x1 = x * self.cell_size + 3
            y1 = y * self.cell_size + 3
            x2 = x1 + self.cell_size - 6
            y2 = y1 + self.cell_size - 6
            color = self.GREEN if apple_type == "G" else self.RED
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline=color)
        
        # Draw snake
        for i, (x, y) in enumerate(self.game.snake.body):
            x1 = x * self.cell_size + 1
            y1 = y * self.cell_size + 1
            x2 = x1 + self.cell_size - 2
            y2 = y1 + self.cell_size - 2
            color = self.DARK_BLUE if i == 0 else self.BLUE
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline=color
            )
        
        # Update info label
        info_text = (
            f"Length: {self.game.snake.length} | "
            f"Step: {step} | "
            f"Reward: {reward:+.1f} | "
            f"Status: {status}"
        )
        self.info_label.config(text=info_text)
        
        # Update display
        self.root.update()
    
    def on_closing(self):
        """Called when user closes the window"""
        self.running = False
        self.root.destroy()
    
    def handle_events(self):
        """
        Handle tkinter events
        
        Returns:
            bool - False if user closes window, True otherwise
        """
        try:
            self.root.update_idletasks()
            return self.running
        except:
            return False
    
    def close(self):
        """Close GUI window"""
        try:
            self.root.destroy()
        except:
            pass
