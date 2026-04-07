"""Main lobby GUI for Learn2Slither"""
import tkinter as tk


class Lobby:
    """Main menu lobby with graphical interface"""

    def __init__(self):
        """Initialize the lobby"""
        self.root = tk.Tk()
        self.root.title("Learn2Slither - Main Menu")
        self.root.geometry("750x850")
        self.root.configure(bg="#2C3E50")

        self.choice = None

        # Handle window close button (X)
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the lobby UI"""
        # Title
        title_frame = tk.Frame(self.root, bg="#34495E", height=140)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)

        title = tk.Label(
            title_frame,
            text="Learn2Slither",
            font=("Arial", 36, "bold"),
            bg="#34495E",
            fg="#1ABC9C"
        )
        title.pack(pady=15, expand=True)

        subtitle = tk.Label(
            title_frame,
            text="Q-Learning Snake Game",
            font=("Arial", 12),
            bg="#34495E",
            fg="#ECF0F1"
        )
        subtitle.pack(pady=8)

        # Main menu frame
        menu_frame = tk.Frame(self.root, bg="#2C3E50")
        menu_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Buttons
        button_style = {
            "font": ("Arial", 13, "bold"),
            "width": 30,
            "height": 3,
            "cursor": "hand2"
        }

        # Train button
        train_btn = tk.Button(
            menu_frame,
            text="1. Train New Model",
            command=self._on_train,
            bg="#3498DB",
            fg="white",
            activebackground="#2980B9",
            **button_style
        )
        train_btn.pack(pady=12, fill=tk.X)

        # Continue training button
        continue_btn = tk.Button(
            menu_frame,
            text="2. Continue Training",
            command=self._on_continue,
            bg="#9B59B6",
            fg="white",
            activebackground="#8E44AD",
            **button_style
        )
        continue_btn.pack(pady=12, fill=tk.X)

        # Test button
        test_btn = tk.Button(
            menu_frame,
            text="3. Test Saved Model",
            command=self._on_test,
            bg="#2ECC71",
            fg="white",
            activebackground="#27AE60",
            **button_style
        )
        test_btn.pack(pady=12, fill=tk.X)

        # Exit button
        exit_btn = tk.Button(
            menu_frame,
            text="4. Exit",
            command=self._on_exit,
            bg="#E74C3C",
            fg="white",
            activebackground="#C0392B",
            **button_style
        )
        exit_btn.pack(pady=12, fill=tk.X)

        # Footer
        footer_frame = tk.Frame(self.root, bg="#34495E", height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)
        footer_frame.pack_propagate(False)

        footer = tk.Label(
            footer_frame,
            text="Use Q-Learning to train an agent to play Snake!",
            font=("Arial", 12),
            bg="#34495E",
            fg="#BDC3C7"
        )
        footer.pack(pady=20, expand=True)

    def _on_train(self):
        """Handle train button"""
        self.choice = "1"
        self.root.quit()

    def _on_continue(self):
        """Handle continue training button"""
        self.choice = "2"
        self.root.quit()

    def _on_test(self):
        """Handle test button"""
        self.choice = "3"
        self.root.quit()

    def _on_exit(self):
        """Handle exit button"""
        self.choice = "4"
        self.root.quit()

    def show(self):
        """Show the lobby and return the selected choice"""
        self.root.mainloop()
        try:
            self.root.destroy()
        except tk.TclError:
            pass
        return self.choice
