"""Enhanced GUI for testing with persistent window and results display"""
import tkinter as tk
from tkinter import Canvas, Scale, Button, Frame, HORIZONTAL, Label


class TestingGUI:
    """GUI for testing models with persistent window across episodes"""

    def __init__(self, mapsize=10, cell_size=20):
        """Initialize testing GUI"""
        self.mapsize = mapsize
        self.cell_size = cell_size
        self.running = True
        self.paused = False

        self.WHITE = "#FFFFFF"
        self.BLACK = "#000000"
        self.GRAY = "#C8C8C8"
        self.GREEN = "#2ECC71"
        self.RED = "#E74C3C"
        self.BLUE = "#3498DB"
        self.DARK_BLUE = "#2980B9"
        self.BG = "#ECF0F1"
        self.ACCENT = "#34495E"

        canvas_width = (mapsize + 2) * cell_size
        canvas_height = (mapsize + 2) * cell_size

        self.root = tk.Tk()
        self.root.title("Learn2Slither - Test Mode")
        self.root.geometry(f"{canvas_width + 50}x{canvas_height + 200}")
        self.root.configure(bg=self.BG)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Header
        header = Label(
            self.root,
            text="Testing Mode",
            font=("Arial", 16, "bold"),
            bg=self.ACCENT,
            fg="white"
        )
        header.pack(fill=tk.X, padx=0, pady=0)

        # Canvas
        canvas_frame = Frame(self.root, bg=self.BG)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = Canvas(
            canvas_frame,
            width=canvas_width,
            height=canvas_height,
            bg=self.WHITE,
            highlightthickness=2,
            highlightbackground=self.ACCENT
        )
        self.canvas.pack()

        # Info panel
        info_frame = Frame(self.root, bg=self.ACCENT, height=80)
        info_frame.pack(fill=tk.X, padx=0, pady=0)
        info_frame.pack_propagate(False)

        self.info_label = Label(
            info_frame,
            text="",
            bg=self.ACCENT,
            fg="white",
            font=("Arial", 11),
            justify=tk.LEFT
        )
        self.info_label.pack(anchor=tk.W, padx=15, pady=10)

        # Control panel
        control_frame = Frame(self.root, bg=self.BG)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        speed_frame = Frame(control_frame, bg=self.BG)
        speed_frame.pack(side=tk.LEFT, padx=5)

        Label(speed_frame, text="Speed:", bg=self.BG,
              font=("Arial", 10)).pack(side=tk.LEFT)

        self.speed_slider = Scale(
            speed_frame,
            from_=0,
            to=5,
            orient=HORIZONTAL,
            length=120,
            bg=self.BG,
            command=self._update_speed,
            showvalue=False
        )
        self.speed_slider.set(3)
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        self.speed_label = Label(
            speed_frame,
            text="40ms",
            bg=self.BG,
            width=6,
            font=("Arial", 9)
        )
        self.speed_label.pack(side=tk.LEFT)

        # Action buttons
        button_frame = Frame(control_frame, bg=self.BG)
        button_frame.pack(side=tk.RIGHT, padx=5)

        self.pause_button = Button(
            button_frame,
            text="Pause",
            command=self.toggle_pause,
            bg="#F39C12",
            fg="white",
            font=("Arial", 9),
            width=10
        )
        self.pause_button.pack(side=tk.LEFT, padx=3)

        stop_button = Button(
            button_frame,
            text="Stop",
            command=self.on_closing,
            bg="#E74C3C",
            fg="white",
            font=("Arial", 9),
            width=10
        )
        stop_button.pack(side=tk.LEFT, padx=3)

        self.speed_map = {0: 0, 1: 80, 2: 60, 3: 40, 4: 20, 5: 0}
        self.delay_ms = 40

    def _update_speed(self, value):
        """Update speed setting"""
        val = int(value)
        self.delay_ms = self.speed_map[val]
        labels = ["Instant", "80ms", "60ms", "40ms", "20ms", "Instant"]
        self.speed_label.config(text=labels[val])

    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        self.pause_button.config(
            text="Resume" if self.paused else "Pause",
            bg="#2ECC71" if self.paused else "#F39C12"
        )

    def render(self, game, episode=0, step=0, reward=0, status=""):
        """Render game state"""
        if not self.running:
            return

        self.canvas.delete("all")

        # Draw grid
        for y, row in enumerate(game.map):
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

        # Draw apples
        for apple_type, (x, y) in game.apples:
            x1 = x * self.cell_size + 3
            y1 = y * self.cell_size + 3
            x2 = x1 + self.cell_size - 6
            y2 = y1 + self.cell_size - 6
            color = self.GREEN if apple_type == "G" else self.RED
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline=color)

        # Draw snake
        for i, (x, y) in enumerate(game.snake.body):
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

        # Update info
        info_text = (
            f"Episode: {episode:3d}  |  "
            f"Length: {game.snake.length:2d}  |  "
            f"Step: {step:3d}  |  "
            f"Reward: {reward:+6.1f}  |  "
            f"Status: {status}"
        )
        self.info_label.config(text=info_text)

        self.root.update_idletasks()

        # Handle pause
        if self.paused:
            while self.paused and self.running:
                try:
                    self.root.update()
                    self.root.after(100)
                except BaseException:
                    break
        else:
            if self.delay_ms > 0:
                self.root.after(self.delay_ms)
            try:
                self.root.update()
            except BaseException:
                pass

    def show_results(self, episodes_data):
        """Display results summary before closing"""
        if not episodes_data:
            return

        # Check if window still exists
        try:
            self.root.winfo_exists()
        except BaseException:
            return

        total_episodes = len(episodes_data)
        lengths = [e['length'] for e in episodes_data]
        rewards = [e['reward'] for e in episodes_data]

        avg_length = sum(lengths) / total_episodes
        max_length = max(lengths)
        avg_reward = sum(rewards) / total_episodes
        max_reward = max(rewards)

        # Clear canvas and show results
        try:
            self.canvas.delete("all")

            results_text = (
                f"RESULTS SUMMARY\n\n"
                f"Episodes Completed: {total_episodes}\n"
                f"Average Length: {avg_length:.1f}\n"
                f"Best Length: {max_length}\n"
                f"Average Reward: {avg_reward:.1f}\n"
                f"Best Reward: {max_reward:.1f}"
            )

            self.canvas.create_text(
                self.canvas.winfo_width() / 2,
                self.canvas.winfo_height() / 2,
                text=results_text,
                font=("Arial", 14, "bold"),
                fill=self.ACCENT,
                justify=tk.CENTER
            )

            self.info_label.config(text="Testing Complete!")

            self.root.update()
            self.root.after(3000)
        except BaseException:
            pass

    def handle_events(self):
        """Handle tkinter events"""
        try:
            self.root.update_idletasks()
            return self.running
        except BaseException:
            return False

    def on_closing(self):
        """Close window"""
        self.running = False
        try:
            self.root.destroy()
        except BaseException:
            pass

    def close(self):
        """Close GUI"""
        self.on_closing()
