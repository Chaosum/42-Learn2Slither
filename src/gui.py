import tkinter as tk
from tkinter import Canvas, Scale, Button, Frame, HORIZONTAL
import json
import os


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
        self.paused = False
        self.step_requested = False

        self.last_speed = self.load_speed()
        self.delay_ms = self._speed_to_ms(self.last_speed)

        self.WHITE = "#FFFFFF"
        self.BLACK = "#000000"
        self.GRAY = "#C8C8C8"
        self.GREEN = "#00FF00"
        self.RED = "#FF0000"
        self.BLUE = "#0000FF"
        self.DARK_BLUE = "#00008B"

        map_width = len(game.map[0])
        map_height = len(game.map)
        canvas_width = map_width * cell_size
        canvas_height = map_height * cell_size

        self.root = tk.Tk()
        self.root.title("Learn2Slither - Snake Game")

        window_width = canvas_width + 300
        self.root.geometry(f"{window_width}x{canvas_height + 150}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.canvas = Canvas(
            self.root,
            width=canvas_width,
            height=canvas_height,
            bg=self.WHITE
        )
        self.canvas.pack()

        self.info_frame = tk.Frame(self.root, height=60, bg="#F0F0F0")
        self.info_frame.pack(fill=tk.X)

        self.info_label = tk.Label(
            self.info_frame,
            text="",
            bg="#F0F0F0",
            font=("Arial", 12)
        )
        self.info_label.pack(anchor=tk.W, padx=10, pady=5)

        self.control_frame = tk.Frame(self.root, bg="#E0E0E0")
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)

        speed_frame = Frame(self.control_frame)
        speed_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(speed_frame, text="Speed:", bg="#E0E0E0").pack(side=tk.LEFT)

        self.speed_slider = Scale(
            speed_frame,
            from_=1,
            to=5,
            orient=HORIZONTAL,
            length=150,
            bg="#E0E0E0",
            command=self.update_speed,
            showvalue=True
        )
        self.speed_slider.set(self.last_speed)
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        self.speed_label = tk.Label(
            speed_frame,
            text=f"{self.delay_ms}ms",
            bg="#E0E0E0",
            width=6,
            font=("Arial", 10)
        )
        self.speed_label.pack(side=tk.LEFT)

        button_frame = Frame(self.control_frame)
        button_frame.pack(side=tk.LEFT, padx=10)

        self.pause_button = Button(
            button_frame,
            text="Pause",
            command=self.toggle_pause,
            width=10,
            bg="#FFA500"
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.step_button = Button(
            button_frame,
            text="Step",
            command=self.step_once,
            width=10,
            bg="#87CEEB",
            state=tk.DISABLED
        )
        self.step_button.pack(side=tk.LEFT, padx=5)

    def load_speed(self):
        """Load last speed preference from config file"""
        config_file = "gui_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('speed', 5)
            except BaseException:
                return 5
        return 5

    def save_speed(self):
        """Save current speed preference to config file"""
        config_file = "gui_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump({'speed': self.last_speed}, f)
        except BaseException:
            pass

    def _speed_to_ms(self, speed_value):
        """Convert speed scale (1-5) to milliseconds"""
        speeds = {1: 80, 2: 60, 3: 40, 4: 20, 5: 0}
        return speeds.get(speed_value, 40)

    def update_speed(self, value):
        """Update the delay based on slider value"""
        scale_value = int(value)
        self.last_speed = scale_value
        self.save_speed()
        self.delay_ms = self._speed_to_ms(scale_value)
        self.speed_label.config(text=f"{self.delay_ms}ms")

    def toggle_pause(self):
        """Toggle pause/resume"""
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Resume", bg="#90EE90")
            self.step_button.config(state=tk.NORMAL)
        else:
            self.pause_button.config(text="Pause", bg="#FFA500")
            self.step_button.config(state=tk.DISABLED)

    def step_once(self):
        """Signal to do one step in pause mode"""
        self.step_requested = True

    def render(self, step=0, reward=0, status=""):
        """
        Render the game state

        Args:
            step: Current step number
            reward: Current reward
            status: Game status message
        """
        self.canvas.delete("all")

        map_grid = self.game.map
        for y, row in enumerate(map_grid):
            for x, cell in enumerate(row):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.GRAY)

                if cell == "W":
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self.BLACK,
                        outline=self.BLACK
                    )

        for apple_type, (x, y) in self.game.apples:
            x1 = x * self.cell_size + 3
            y1 = y * self.cell_size + 3
            x2 = x1 + self.cell_size - 6
            y2 = y1 + self.cell_size - 6
            color = self.GREEN if apple_type == "G" else self.RED
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline=color)

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

        status_text = status if status else "Running"
        if self.paused:
            status_text += " [PAUSED]"

        info_text = (
            f"Length: {self.game.snake.length} | "
            f"Step: {step} | "
            f"Reward: {reward:+.1f} | "
            f"Status: {status_text}"
        )
        self.info_label.config(text=info_text)

        self.root.update()

        self.wait_with_controls()

    def wait_with_controls(self):
        """Wait for the specified delay while handling pause/step controls"""
        if self.paused:

            self.step_requested = False
            while not self.step_requested and self.running and self.paused:
                try:
                    self.root.update()
                    self.root.after(50)
                except BaseException:
                    break
        else:

            if self.delay_ms > 0:
                try:
                    self.root.after(self.delay_ms)
                    self.root.update()
                except BaseException:
                    pass
            else:

                try:
                    self.root.update()
                except BaseException:
                    pass

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
        except BaseException:
            return False

    def close(self):
        """Close GUI window"""
        try:
            self.root.destroy()
        except BaseException:
            pass
