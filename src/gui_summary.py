"""Summary window for training/test results"""
import tkinter as tk


class SummaryWindow:
    """Displays a styled summary of training/test results"""

    def __init__(self, title, results):
        """Initialize and show summary window
        results should be a dict with keys like:
        - avg_length, max_length, min_length
        - avg_reward, episodes
        """
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("700x600")
        self.root.configure(bg="#2C3E50")

        # Title
        title_frame = tk.Frame(self.root, bg="#34495E", height=120)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="Results Summary",
            font=("Arial", 32, "bold"),
            bg="#34495E",
            fg="#1ABC9C"
        )
        title_label.pack(pady=30)

        # Content frame
        content = tk.Frame(self.root, bg="#2C3E50")
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # Display results
        row = 0
        for key, value in results.items():
            label = tk.Label(
                content,
                text=f"{key}:",
                font=("Arial", 14, "bold"),
                bg="#2C3E50",
                fg="#1ABC9C",
                anchor=tk.W
            )
            label.grid(row=row, column=0, sticky="w", pady=10)

            value_label = tk.Label(
                content,
                text=str(value),
                font=("Arial", 14),
                bg="#2C3E50",
                fg="#2ECC71",
                anchor=tk.W
            )
            value_label.grid(row=row, column=1, sticky="w", padx=20, pady=10)

            row += 1

        # Close button
        close_btn = tk.Button(
            self.root,
            text="Close",
            command=self.root.quit,
            bg="#3498DB",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=2
        )
        close_btn.pack(pady=20)

    def show(self):
        """Show the window"""
        self.root.mainloop()
        self.root.destroy()
