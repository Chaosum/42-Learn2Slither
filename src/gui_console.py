"""Graphical console output window"""
import tkinter as tk
from tkinter import scrolledtext, Button, Frame
import sys


class ConsoleWindow:
    """Graphical console that captures stdout"""

    def __init__(self):
        """Initialize console window"""
        self.root = tk.Tk()
        self.root.title("Learn2Slither - Console Output")
        self.root.geometry("800x600")
        self.root.configure(bg="#2C3E50")

        # Header
        header = tk.Label(
            self.root,
            text="📝 Console Output",
            font=("Arial", 14, "bold"),
            bg="#34495E",
            fg="white"
        )
        header.pack(fill=tk.X, padx=0, pady=0)

        # Console frame
        frame = Frame(self.root, bg="#2C3E50")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Text widget
        self.text_widget = scrolledtext.ScrolledText(
            frame,
            bg="#1E1E1E",
            fg="#00FF00",
            font=("Courier New", 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Configure tags for different message types
        self.text_widget.tag_config("info", foreground="#1ABC9C")
        self.text_widget.tag_config("success", foreground="#2ECC71")
        self.text_widget.tag_config("error", foreground="#E74C3C")
        self.text_widget.tag_config("warning", foreground="#F39C12")
        self.text_widget.tag_config("normal", foreground="#00FF00")

        # Button frame
        button_frame = Frame(self.root, bg="#2C3E50")
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        clear_btn = Button(
            button_frame,
            text="Clear",
            command=self.clear,
            bg="#3498DB",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        close_btn = Button(
            button_frame,
            text="Close",
            command=self.close,
            bg="#E74C3C",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15
        )
        close_btn.pack(side=tk.LEFT, padx=5)

        # Redirect stdout
        self.old_stdout = sys.stdout
        sys.stdout = self

    def write(self, message):
        """Write message to console"""
        if message.strip():
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)
            self.root.update()

    def flush(self):
        """Flush stdout"""
        pass

    def log(self, message, tag="normal"):
        """Log a message with specific tag"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, f"{message}\n", tag)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
        self.root.update()

    def log_info(self, message):
        """Log info message"""
        self.log(message, "info")

    def log_success(self, message):
        """Log success message"""
        self.log(message, "success")

    def log_error(self, message):
        """Log error message"""
        self.log(message, "error")

    def log_warning(self, message):
        """Log warning message"""
        self.log(message, "warning")

    def clear(self):
        """Clear console"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def close(self):
        """Close console and restore stdout"""
        sys.stdout = self.old_stdout
        try:
            self.root.destroy()
        except BaseException:
            pass

    def show(self):
        """Show console window"""
        self.root.deiconify()
        self.root.mainloop()

    def update_ui(self):
        """Update UI"""
        try:
            self.root.update()
        except BaseException:
            pass
