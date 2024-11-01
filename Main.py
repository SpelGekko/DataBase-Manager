## Made by Gekko

import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedStyle
from DataBaseManager import DataBaseManagerGUI
from Settings import Settings
from Converter import ConverterApp  # Import the ConverterApp
from FileManager import FileManager  # Import the LogViewer

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Screen")
        self.root.geometry("400x300")

        # Initialize the theme directly in the constructor
        self.current_theme = "alt"
        self.apply_theme(self.current_theme)

        # Create a settings button in the top-left corner
        settings_button = ttk.Button(self.root, text="Settings", command=self.open_settings)
        settings_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Create buttons for different parts of the application
        db_manager_button = ttk.Button(self.root, text="DataBase Manager", command=lambda: self.open_part("Database Manager"))
        db_manager_button.grid(row=1, column=0, padx=10, pady=10)

        converter_button = ttk.Button(self.root, text="Converter", command=lambda: self.open_part("Converter"))
        converter_button.grid(row=1, column=1, padx=10, pady=10)

        file_manager_button = ttk.Button(self.root, text="File Manager", command=lambda: self.open_part("File Manager"))
        file_manager_button.grid(row=1, column=2, padx=10, pady=10)

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        style = ThemedStyle(self.root)
        style.set_theme(theme_name)  # Set the theme

        # Get the background color from the current theme
        bg_color = style.lookup("TFrame", "background")

        # Set the background color of the main window
        self.root.configure(bg=bg_color)

    def open_settings(self):
        Settings(self.root, self)

    def open_part(self, part_name):
        if part_name == "Database Manager":
            db_manager_window = tk.Toplevel(self.root)
            DataBaseManagerGUI(db_manager_window, self.current_theme)
        elif part_name == "Converter":
            converter_window = tk.Toplevel(self.root)
            ConverterApp(converter_window, self.current_theme)
        elif part_name == "File Manager":
            FileManager_window = tk.Toplevel(self.root)
            FileManager(FileManager_window, self.current_theme)
        else:
            messagebox.showinfo(part_name, f"Opening {part_name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()