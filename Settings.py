## Made by Gekko

from ttkthemes import ThemedStyle
import tkinter as tk
from tkinter import ttk

class Settings:
    def __init__(self, master, main_app):
        self.master = master
        self.main_app = main_app
        self.window = tk.Toplevel(master)
        self.window.title("Settings")
        self.window.geometry("300x200")

        # Example setting: Theme selection
        self.theme_var = tk.StringVar(value="Light")
        ttk.Label(self.window, text="Select Theme:").pack(pady=10)
        ttk.Radiobutton(self.window, text="Light", variable=self.theme_var, value="Light").pack(anchor=tk.W)
        ttk.Radiobutton(self.window, text="Dark", variable=self.theme_var, value="Dark").pack(anchor=tk.W)

        # Save button
        ttk.Button(self.window, text="Save", command=self.save_settings).pack(pady=20)

        # Apply the initial theme
        self.apply_theme(self.theme_var.get())

    def save_settings(self):
        # Save the settings (for now, just print them)
        selected_theme = self.theme_var.get()
        print(f"Selected theme: {selected_theme}")
        self.apply_theme(selected_theme)
        self.main_app.apply_theme(self.map_theme_name(selected_theme))  # Apply the theme to the main window
        self.window.destroy()

    def apply_theme(self, theme):
        style = ThemedStyle(self.master)
        style.set_theme(self.map_theme_name(theme))

        # Get the background color from the current theme
        bg_color = style.lookup("TFrame", "background")

        # Set the background color of the settings window
        self.window.configure(bg=bg_color)

        # Update the background color of all child widgets
        for child in self.window.winfo_children():
            if isinstance(child, tk.Label) or isinstance(child, tk.Radiobutton) or isinstance(child, tk.Button):
                child.configure(bg=bg_color)
            elif isinstance(child, ttk.Combobox) or isinstance(child, ttk.Button):
                child.configure(style="TCombobox" if isinstance(child, ttk.Combobox) else "TButton")

        self.master.update_idletasks()

    def map_theme_name(self, theme_name):
        """Map user-friendly theme names to actual theme names."""
        theme_map = {
            "Light": "alt",
            "Dark": "equilux"
        }
        return theme_map.get(theme_name, "alt")