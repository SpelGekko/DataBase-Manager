## Made by Gekko

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedStyle
import os
import logging

class FileManager:
    def __init__(self, root, theme_name="alt"):
        self.root = root
        self.root.title("File Manager")
        self.apply_theme(theme_name)

        # Add widgets for file management
        ttk.Label(self.root, text="File Manager").pack(padx=10, pady=10)

        # Add a treeview to display files
        self.file_treeview = ttk.Treeview(self.root, columns=("Name", "Size", "Type"), show="headings")
        self.file_treeview.heading("Name", text="Name")
        self.file_treeview.heading("Size", text="Size")
        self.file_treeview.heading("Type", text="Type")
        self.file_treeview.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Add buttons to open and delete files
        ttk.Button(self.root, text="Open File", command=self.open_file).pack(padx=10, pady=5)
        ttk.Button(self.root, text="Delete File", command=self.delete_file).pack(padx=10, pady=5)

        # Load files
        self.load_files()

    def apply_theme(self, theme_name):
        style = ThemedStyle(self.root)
        style.set_theme(theme_name)

    def load_files(self):
        # Clear the treeview
        for item in self.file_treeview.get_children():
            self.file_treeview.delete(item)

        # Load files from the current directory
        current_directory = os.getcwd()
        for filename in os.listdir(current_directory):
            filepath = os.path.join(current_directory, filename)
            if os.path.isfile(filepath):
                file_size = os.path.getsize(filepath)
                file_type = os.path.splitext(filename)[1]
                self.file_treeview.insert("", "end", values=(filename, file_size, file_type))
        logging.info("Files loaded")

    def open_file(self):
        selected_item = self.file_treeview.selection()
        if selected_item:
            filename = self.file_treeview.item(selected_item, "values")[0]
            filepath = os.path.join(os.getcwd(), filename)
            os.startfile(filepath)
            logging.info(f"File opened: {filename}")

    def delete_file(self):
        selected_item = self.file_treeview.selection()
        if selected_item:
            filename = self.file_treeview.item(selected_item, "values")[0]
            filepath = os.path.join(os.getcwd(), filename)
            os.remove(filepath)
            self.load_files()
            messagebox.showinfo("Success", f"File deleted: {filename}")
            logging.info(f"File deleted: {filename}")