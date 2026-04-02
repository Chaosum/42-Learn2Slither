"""Graphical dialogs for user input - simplified version"""
import tkinter as tk
from tkinter import simpledialog, messagebox


class InputDialogs:
    """Collection of graphical input dialogs"""

    @staticmethod
    def ask_integer(title, message, default=10, min_val=1, max_val=10000):
        """Ask for integer input"""
        root = tk.Tk()
        root.withdraw()
        root.title(title)

        value = simpledialog.askinteger(
            title,
            message,
            initialvalue=default,
            minvalue=min_val,
            maxvalue=max_val
        )
        root.destroy()
        return value

    @staticmethod
    def ask_choice(title, choices):
        """Ask user to choose from list using simple dialog"""
        root = tk.Tk()
        root.withdraw()
        root.title(title)

        choice_text = "Select an option:\n\n"
        for i, (text, _) in enumerate(choices, 1):
            choice_text += f"{i}. {text}\n"

        while True:
            result = simpledialog.askinteger(
                title,
                choice_text + f"\nEnter number (1-{len(choices)}):",
                minvalue=1,
                maxvalue=len(choices)
            )

            if result is None:
                root.destroy()
                return ""

            if 1 <= result <= len(choices):
                root.destroy()
                return choices[result - 1][1]

    @staticmethod
    def ask_string(title, message, default=""):
        """Ask for string input"""
        root = tk.Tk()
        root.withdraw()
        root.title(title)

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
