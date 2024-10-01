## Made By Gekko

import tkinter as tk
from tkinter import messagebox
from DataBaseManager import DataBaseManagerGUI

# Function to handle settings button click
def open_settings():
    messagebox.showinfo("Settings", "Settings window")

# Function to handle different parts of the application
def open_part(part_name):
    if part_name == "Database Manager":
        db_manager_window = tk.Toplevel(root)
        DataBaseManagerGUI(db_manager_window)
    else:
        messagebox.showinfo(part_name, f"Opening {part_name}")

# Create the main application window
root = tk.Tk()
root.title("Home Screen")
root.geometry("400x300")

# Create a settings button in the top-left corner
settings_button = tk.Button(root, text="Settings", command=open_settings)
settings_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Create buttons for different parts of the application
db_manager_button = tk.Button(root, text="DataBase Manager", command=lambda: open_part("Database Manager"))
db_manager_button.grid(row=1, column=0, padx=10, pady=10)

part2_button = tk.Button(root, text="Part 2", command=lambda: open_part("Part 2"))
part2_button.grid(row=1, column=1, padx=10, pady=10)

part3_button = tk.Button(root, text="Part 3", command=lambda: open_part("Part 3"))
part3_button.grid(row=1, column=2, padx=10, pady=10)

# Run the Tkinter main loop
root.mainloop()