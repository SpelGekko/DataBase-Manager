## Made By Gekko

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from ttkthemes import ThemedStyle
import pandas as pd
import sqlite3
import os
from Settings import Settings  # Import the Settings class
from DataBaseManager import DataBaseManagerGUI  # Import the DataBaseManagerGUI class

class ConverterApp:
    def __init__(self, root, theme_name="alt"):
        self.root = root
        self.root.title("Database to Excel Converter")

        self.create_widgets()
        self.apply_theme(theme_name)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Add the Settings button
        settings_button = ttk.Button(self.main_frame, text="Settings", command=self.open_settings)
        settings_button.pack(side="left", padx=10, pady=10)

        # Add a button to open the database selector
        ttk.Button(self.main_frame, text="Open Manager", command=self.open_database_manager_window).pack(side="left", padx=10, pady=10)

        # Add a button to export to Excel
        ttk.Button(self.main_frame, text="Export to Excel", command=self.open_export_window).pack(padx=10, pady=10)

        # Add a button to import from Excel
        ttk.Button(self.main_frame, text="Import from Excel", command=self.open_import_window).pack(padx=10, pady=10)

    def open_settings(self):
        Settings(self.root, self)

    def open_database_manager_window(self):
        db_manager_window = tk.Toplevel(self.root)
        db_manager_window.title("Database Manager")
        DataBaseManagerGUI(db_manager_window, self.current_theme)  # Pass the current theme

    def open_export_window(self):
        self.open_selection_window("export")

    def open_import_window(self):
        self.open_selection_window("import")

    def open_selection_window(self, action):
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Database and Table")

        ttk.Label(selection_window, text="Select Database:").pack(pady=5)
        db_combobox = ttk.Combobox(selection_window)
        db_combobox.pack(pady=5)

        if action == "export":
            ttk.Label(selection_window, text="Select Table:").pack(pady=5)
            table_combobox = ttk.Combobox(selection_window)
            table_combobox.pack(pady=5)

            def load_tables(event):
                db_name = db_combobox.get()
                if db_name:
                    conn = sqlite3.connect(db_name)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]
                    table_combobox['values'] = tables
                    conn.close()

            db_combobox.bind("<<ComboboxSelected>>", load_tables)

        def proceed():
            db_name = db_combobox.get()
            if not db_name:
                messagebox.showerror("Error", "Please select a database.")
                return

            if action == "export":
                table_name = table_combobox.get()
                if not table_name:
                    messagebox.showerror("Error", "Please select a table.")
                    return
                self.export_to_excel(db_name, table_name)
            elif action == "import":
                self.import_from_excel(db_name)
            selection_window.destroy()

        ttk.Button(selection_window, text="Proceed", command=proceed).pack(pady=10)

        # Load available databases
        db_combobox['values'] = self.get_databases()

    def get_databases(self):
        # List all .db files in the current directory
        return [f for f in os.listdir('.') if f.endswith('.db')]

    def export_to_excel(self, db_name, table_name):
        output_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not output_file:
            return

        try:
            conn = sqlite3.connect(db_name)
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            df.to_excel(output_file, index=False)
            conn.close()
            messagebox.showinfo("Success", f"Table {table_name} exported to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def import_from_excel(self, db_name):
        input_file = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx")])
        if not input_file:
            return

        # Extract the table name from the Excel file name
        table_name = os.path.splitext(os.path.basename(input_file))[0]

        try:
            df = pd.read_excel(input_file)
            conn = sqlite3.connect(db_name)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.close()
            messagebox.showinfo("Success", f"Excel file {input_file} imported into table {table_name}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def apply_theme(self, theme_name):
        self.current_theme = theme_name  # Store the current theme
        style = ThemedStyle(self.root)
        style.set_theme(theme_name)

        # Get the background color from the current theme
        bg_color = style.lookup("TFrame", "background")

        # Set the background color of the main window and main frame
        self.root.configure(bg=bg_color)
        self.main_frame.configure(style="TFrame")

        # Update the background color of all child widgets
        for child in self.main_frame.winfo_children():
            if isinstance(child, tk.Label) or isinstance(child, tk.Radiobutton) or isinstance(child, tk.Button):
                child.configure(bg=bg_color)
            elif isinstance(child, ttk.Combobox) or isinstance(child, ttk.Button):
                child.configure(style="TCombobox" if isinstance(child, ttk.Combobox) else "TButton")

        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()