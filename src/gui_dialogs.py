"""Graphical dialogs for user input"""
import tkinter as tk
from tkinter import simpledialog, messagebox


class InputDialogs:
    """Collection of graphical input dialogs"""

    @staticmethod
    def ask_integer(title, message, default=10, min_val=1, max_val=10000):
        """Ask for integer input"""
        root = tk.Tk()
        root.geometry("800x550")
        root.title(title)
        root.configure(bg="#2C3E50")

        result = [None]

        frame = tk.Frame(root, bg="#2C3E50")
        frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        label = tk.Label(
            frame,
            text=message,
            font=("Arial", 24, "bold"),
            bg="#2C3E50",
            fg="#1ABC9C"
        )
        label.pack(pady=30)

        # Input frame
        input_frame = tk.Frame(frame, bg="#2C3E50")
        input_frame.pack(pady=20)

        input_label = tk.Label(
            input_frame,
            text="Value:",
            font=("Arial", 20),
            bg="#2C3E50",
            fg="white"
        )
        input_label.pack(side=tk.LEFT, padx=10)

        entry = tk.Entry(
            input_frame,
            font=("Arial", 20),
            width=15,
            bg="#34495E",
            fg="white",
            insertbackground="white"
        )
        entry.pack(side=tk.LEFT, padx=10)
        entry.insert(0, str(default))
        entry.focus()

        def on_ok():
            try:
                val = int(entry.get())
                if min_val <= val <= max_val:
                    result[0] = val
                    root.quit()
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(default))
            except ValueError:
                entry.delete(0, tk.END)
                entry.insert(0, str(default))

        def on_cancel():
            root.quit()

        button_frame = tk.Frame(frame, bg="#2C3E50")
        button_frame.pack(pady=30)

        ok_button = tk.Button(
            button_frame,
            text="OK",
            command=on_ok,
            bg="#2ECC71",
            fg="white",
            font=("Arial", 16, "bold"),
            width=15,
            height=2
        )
        ok_button.pack(side=tk.LEFT, padx=15)

        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=on_cancel,
            bg="#E74C3C",
            fg="white",
            font=("Arial", 16, "bold"),
            width=15,
            height=2
        )
        cancel_button.pack(side=tk.LEFT, padx=15)

        root.bind('<Return>', lambda e: on_ok())
        root.bind('<Escape>', lambda e: on_cancel())

        root.mainloop()
        root.destroy()
        return result[0]

    @staticmethod
    def ask_choice(title, choices):
        """Ask user to choose from list"""
        root = tk.Tk()
        root.title(title)
        root.configure(bg="#2C3E50")

        # Get screen dimensions and use 80% of screen size
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.85)

        root.geometry(f"{window_width}x{window_height}")

        # Scrolled frame for many options
        canvas_frame = tk.Frame(root, bg="#2C3E50")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        canvas = tk.Canvas(
            canvas_frame,
            bg="#2C3E50",
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas, bg="#2C3E50")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        label = tk.Label(
            scrollable_frame,
            text=title,
            font=("Arial", 32, "bold"),
            bg="#2C3E50",
            fg="#1ABC9C"
        )
        label.pack(pady=40)

        selection = tk.StringVar(value="")
        radiobuttons = []

        for choice_text, choice_value in choices:
            rb = tk.Radiobutton(
                scrollable_frame,
                text=choice_text,
                variable=selection,
                value=choice_value,
                font=("Arial", 28, "bold"),
                bg="#34495E",
                fg="white",
                selectcolor="#1ABC9C",
                activebackground="#1ABC9C",
                activeforeground="black",
                highlightthickness=0,
                bd=0,
                padx=60,
                pady=40,
                wraplength=600,
                justify=tk.LEFT
            )
            rb.pack(anchor=tk.W, pady=20, fill=tk.X, padx=60)
            radiobuttons.append((rb, choice_value))

        # Fonction pour updater tous les styles
        def on_selection_change(*args):
            selected_val = selection.get()
            for rb, val in radiobuttons:
                if val == selected_val:
                    rb.config(bg="#1ABC9C", fg="black")
                else:
                    rb.config(bg="#34495E", fg="white")

        # Bind pour updater quand sélection change
        selection.trace("w", on_selection_change)

        # Rendu initial
        on_selection_change()

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = tk.Frame(root, bg="#2C3E50")
        button_frame.pack(pady=30)

        ok_button = tk.Button(
            button_frame,
            text="OK",
            command=root.quit,
            bg="#2ECC71",
            fg="white",
            font=("Arial", 18, "bold"),
            width=20,
            height=3
        )
        ok_button.pack(side=tk.LEFT, padx=20)

        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=lambda: (selection.set(""), root.quit()),
            bg="#E74C3C",
            fg="white",
            font=("Arial", 18, "bold"),
            width=20,
            height=3
        )
        cancel_button.pack(side=tk.LEFT, padx=20)

        root.mainloop()
        root.destroy()

        return selection.get()

    @staticmethod
    def ask_string(title, message, default=""):
        """Ask for string input"""
        root = tk.Tk()
        root.geometry("600x250")
        root.title(title)
        root.configure(bg="#2C3E50")

        frame = tk.Frame(root, bg="#2C3E50")
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        label = tk.Label(
            frame,
            text=message,
            font=("Arial", 16, "bold"),
            bg="#2C3E50",
            fg="#1ABC9C"
        )
        label.pack(pady=20)

        result = simpledialog.askstring(
            title,
            message,
            initialvalue=default
        )
        root.destroy()
        return result if result else default

    @staticmethod
    def ask_yes_no(title, message):
        """Ask yes/no question"""
        root = tk.Tk()
        root.withdraw()
        root.title(title)

        result = messagebox.askyesno(title, message)
        root.destroy()
        return result

    @staticmethod
    def show_info(title, message):
        """Show info message"""
        root = tk.Tk()
        root.withdraw()
        root.title(title)

        messagebox.showinfo(title, message)
        root.destroy()

    @staticmethod
    def show_error(title, message):
        """Show error message"""
        root = tk.Tk()
        root.withdraw()
        root.title(title)

        messagebox.showerror(title, message)
        root.destroy()
