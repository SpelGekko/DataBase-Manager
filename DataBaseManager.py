## Made by Gekko

import sqlite3
from tkinter import Tk, Label, Entry, Button, messagebox, simpledialog, ttk, Toplevel, END, OptionMenu, StringVar, Listbox, SINGLE, IntVar

class DataBaseManager:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        print(f"Connected to database {db_name}")

    def create_table(self, table_name, columns):
        columns_def = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        self.cursor.execute(query)
        self.connection.commit()
        print(f"Table {table_name} created with columns {columns_def}")

    def insert_data(self, table_name, data):
        placeholders = ", ".join(["?" for _ in data])
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        
        # Debugging: Print the query and values
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        print(f"Executing query: {query} with values: {values}")  # Debugging line
        
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Data inserted into {table_name}: {data}")
        except sqlite3.OperationalError as e:
            print(f"Error inserting data: {e}")  # Log the error for debugging
            raise  # Re-raise the error to handle it in the GUI

    def get_table_rows(self, table_name):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchall()
 
    def query_data(self, table_name, columns="*", condition=None):
        query = f"SELECT {columns} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        print(f"Query results from {table_name}: {results}")
        return results
    
    def update_data(self, table_name, updates, condition):
        updates_def = ", ".join([f"{col} = ?" for col in updates.keys()])
        values = tuple(updates.values())
        query = f"UPDATE {table_name} SET {updates_def} WHERE {condition}"
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Data updated in {table_name}: {updates} where {condition}")
        except sqlite3.OperationalError as e:
            print(f"SQL error: {e}")
            raise

    def delete_data(self, table_name, condition, values):
        if not condition:
            raise ValueError("Condition is required for deleting data.")
        
        query = f"DELETE FROM {table_name} WHERE {condition}"
        
        # Debugging: Print the exact SQL query and values
        print(f"Executing query: {query} with values: {values}")

        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Data deleted from {table_name} where {condition} with values {values}")
        except sqlite3.OperationalError as e:
            print(f"SQL error: {e}")
            raise

    def get_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        self.cursor.execute(query)
        tables = [row[0] for row in self.cursor.fetchall()]
        return tables

    def get_table_columns(self, table_name):
        # Clean up the table name to avoid issues
        table_name = table_name.strip()  # Trim whitespace
        if not table_name:  # Check if table name is empty
            raise ValueError("Table name cannot be empty.")

        # Use PRAGMA for SQLite to retrieve column info, ensuring the table name is quoted
        query = f"PRAGMA table_info('{table_name}')"  # Properly quote the table name
        print(f"Executing query: {query}")  # Debugging line to check the query

        try:
            self.cursor.execute(query)
        except sqlite3.OperationalError as e:
            print(f"Failed to execute query: {e}")  # Log the error for debugging
            raise  # Re-raise the error for further handling

        # Fetch all the column info rows
        columns_info = self.cursor.fetchall()

        # Create a list of tuples (column_name, column_type)
        columns = [(row[1], row[2]) for row in columns_info]  # row[1] is name, row[2] is type
        return columns
    
    def remove_column(self, table_name, column_name):
        print(f"Attempting to remove column '{column_name}' from table '{table_name}'")
        
        existing_columns = self.get_table_columns(table_name)
        columns_to_keep = [col[0] for col in existing_columns if col[0] != column_name]

        print(f"Columns to keep: {columns_to_keep}")

        # Ensure there's at least one column left
        if len(columns_to_keep) == 0:
            raise ValueError("Cannot remove the last remaining column in the table.")

        # Create a new temporary table without the column to be deleted
        temp_table_name = f"{table_name}_temp"
        columns_sql = ", ".join([f"{col[0]} {col[1]}" for col in existing_columns if col[0] != column_name])

        print(f"Creating temporary table with query: CREATE TABLE {temp_table_name} ({columns_sql})")
        self.cursor.execute(f"CREATE TABLE {temp_table_name} ({columns_sql})")

        # Insert data from the old table into the new table
        select_columns = ", ".join(columns_to_keep)
        print(f"Inserting data into temp table with query: INSERT INTO {temp_table_name} SELECT {select_columns} FROM {table_name}")
        self.cursor.execute(f"INSERT INTO {temp_table_name} SELECT {select_columns} FROM {table_name}")

        # Drop the original table
        print(f"Dropping original table '{table_name}'")
        self.cursor.execute(f"DROP TABLE {table_name}")

        # Rename the temporary table to the original table name
        print(f"Renaming temporary table '{temp_table_name}' to '{table_name}'")
        self.cursor.execute(f"ALTER TABLE {temp_table_name} RENAME TO {table_name}")

        # Commit changes to the database
        self.connection.commit()
        print("Column deleted successfully.")

    def close_connection(self):
        self.connection.close()
        print("Database connection closed")

    def fetch_data(self, table_name, order_by=None, search_term=None):
        query = f"SELECT * FROM {table_name}"
        if search_term:
            query += f" WHERE {search_term}"
        if order_by:
            query += f" ORDER BY {order_by}"
        print(f"Executing query: {query}")  # Debugging line to print the query
        self.cursor.execute(query)
        return self.cursor.fetchall()

class DataBaseManagerGUI:
    def __init__(self, root):
        self.db_manager = DataBaseManager("test.db")
        self.root = root
        self.root.title("Database Manager")

        self.column_entries = []
        self.data_entries = []

        self.create_widgets()
        self.populate_treeview()
        self.create_column_selection_listbox()

        # Variable to hold the selected column for deletion
        self.selected_column_index = IntVar(value=-1)  # Default to no selection

    def create_widgets(self):
        # Set the window to fullscreen
        self.root.state("zoomed")

        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # PanedWindow to split the main frame into three sections horizontally
        paned_window = ttk.PanedWindow(main_frame, orient="horizontal")
        paned_window.pack(fill="both", expand=True)

        # Left frame for table and column management
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)

        Label(left_frame, text="Table Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.table_name_entry = Entry(left_frame)
        self.table_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        Button(left_frame, text="Create Table", command=self.create_table).grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        Button(left_frame, text="Update Table", command=self.update_table).grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.columns_frame = ttk.Frame(left_frame)
        self.columns_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Add headers for column entries
        Label(self.columns_frame, text="Column Name").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Label(self.columns_frame, text="Column Type").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.add_column_entry()  # Method to add a column entry row

        Button(left_frame, text="Add Column", command=self.add_column_entry).grid(row=4, column=0, columnspan=1, padx=10, pady=10, sticky="ew")
        Button(left_frame, text="Remove Column", command=self.open_remove_column_dialog).grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Treeview to display tables
        self.treeview = ttk.Treeview(left_frame, columns=("Columns"), show="headings")
        self.treeview.heading("#0", text="Table Name")
        self.treeview.heading("Columns", text="Tables")
        self.treeview.column("#0", width=150, minwidth=150, stretch=True)
        self.treeview.column("Columns", width=150, minwidth=150, stretch=True)
        self.treeview.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.treeview.bind("<Double-1>", self.load_table_for_editing)

        Button(left_frame, text="Delete Table", command=self.delete_table).grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Middle frame for data adding, sorting, and searching
        middle_frame = ttk.Frame(paned_window)
        paned_window.add(middle_frame, weight=1)

        self.data_frame = ttk.Frame(middle_frame)
        self.data_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Add headers for data entries
        Label(self.data_frame, text="Column Name").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Label(self.data_frame, text="Value").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        if not self.treeview.selection():
            self.add_data_entry()

        Button(middle_frame, text="Add Data", command=self.add_data_entry).grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        Button(middle_frame, text="Insert Data", command=self.insert_data).grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Add search functionality
        Label(middle_frame, text="Search:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.search_entry = Entry(middle_frame)
        self.search_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        Button(middle_frame, text="Search", command=self.search_data).grid(row=3, column=2, padx=10, pady=10, sticky="ew")

        Button(middle_frame, text="Update Data", command=self.update_data).grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        Button(middle_frame, text="Delete Data", command=self.delete_data).grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        Button(middle_frame, text="Sort Data", command=self.open_sort_menu).grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Right frame for data display
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)

        # Add scrollbars to the data treeview
        data_treeview_frame = ttk.Frame(right_frame)
        data_treeview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.data_treeview = ttk.Treeview(data_treeview_frame, show="headings")
        self.data_treeview.pack(side="left", fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(data_treeview_frame, orient="vertical", command=self.data_treeview.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.data_treeview.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(data_treeview_frame, orient="horizontal", command=self.data_treeview.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        self.data_treeview.configure(xscrollcommand=scrollbar_x.set)

        Button(right_frame, text="Load Data", command=self.load_data).pack(padx=10, pady=10)

        self.data_treeview.bind("<Double-1>", self.on_double_click)

        # Populate the treeview with tables from the database
        self.populate_treeview()
    
    def show_condition_help(self):
        messagebox.showinfo("Condition Help", "Use SQL syntax for conditions.\n\nExamples:\n- id = 1\n- name = 'John'\n- age > 30\n- salary BETWEEN 50000 AND 100000")

    def add_column_entry(self, column_name=None, column_type=None):
        row = len(self.column_entries)  # Determine the row index for new entries

        # Create a column name entry widget
        column_name_entry = Entry(self.columns_frame)
        if column_name:  # Insert existing column name if provided
            column_name_entry.insert(0, column_name)
        column_name_entry.grid(row=row + 1, column=0, padx=5, pady=5, sticky="ew")

        # Create a StringVar for the column type OptionMenu
        column_type_var = StringVar(self.columns_frame)
        column_type_var.set(column_type if column_type else "TEXT")  # Set default type to TEXT

        # Create the OptionMenu for column types
        column_type_menu = OptionMenu(self.columns_frame, column_type_var, "TEXT", "INTEGER", "REAL", "BLOB")
        column_type_menu.grid(row=row + 1, column=1, padx=5, pady=5, sticky="ew")

        # Append the column entry widgets to the list (name entry and type menu)
        self.column_entries.append((column_name_entry, column_type_menu, column_type_var))  # Store all relevant references
   
    def populate_treeview(self):
        # Clear existing items in the treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for table in self.db_manager.get_tables():
            parent_id = self.treeview.insert("", "end", text=table, values=(table,))  # Table as parent

    def delete_row(self):
        selected_item = self.data_treeview.selection()
        if selected_item:
            item = selected_item[0]
            row_id = self.data_treeview.item(item, "values")[0]  # Assuming the first column is the primary key
            table_name = self.table_name_entry.get()
            
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete row with ID {row_id}?")
            if confirm:
                self.db_manager.delete_data(table_name, f"id = {row_id}")
                self.data_treeview.delete(item)
                messagebox.showinfo("Success", f"Row with ID {row_id} deleted.")
        else:
            messagebox.showerror("Error", "Please select a row to delete.")

    def load_table_for_editing(self, event):
        selected_item = self.treeview.selection()
        if not selected_item:
            return

        # Get the name of the selected table
        table_name = self.treeview.item(selected_item, "text")
        self.table_name_entry.delete(0, END)
        self.table_name_entry.insert(0, table_name)

        # Clear existing column entries from the GUI
        for entry in self.column_entries:
            entry[0].grid_forget()  # Hide the column name entry widget
            entry[1].grid_forget()  # Hide the column type OptionMenu widget
        self.column_entries.clear()  # Clear the list for new entries

        # Load columns for the selected table
        columns = self.db_manager.get_table_columns(table_name)
        for column in columns:
            if isinstance(column, tuple) and len(column) == 2:  # Ensure each column is a tuple with name and type
                self.add_column_entry(column_name=column[0], column_type=column[1])  # Pass name and type
            else:
                print(f"Unexpected column format: {column}")  # Debugging output for unexpected formats

    def load_data(self, order_by=None, search_term=None):
        selected_item = self.treeview.selection()
        if selected_item:
            table_name = self.treeview.item(selected_item, "text")
            self.table_name_entry.delete(0, END)
            self.table_name_entry.insert(0, table_name)
            
            columns = self.db_manager.get_table_columns(table_name)
            self.data_treeview["columns"] = columns
            for col in columns:
                self.data_treeview.heading(col, text=col)
                self.data_treeview.column(col, width=100)
            
            for item in self.data_treeview.get_children():
                self.data_treeview.delete(item)
            
            data = self.db_manager.fetch_data(table_name, order_by=order_by, search_term=search_term)
            for row in data:
                self.data_treeview.insert("", "end", values=row)
        else:
            messagebox.showerror("Error", "Please select a table to load data.")
    
    def on_double_click(self, event):
        # Identify the row and column
        row_id = self.data_treeview.identify_row(event.y)
        column = self.data_treeview.identify_column(event.x)
        
        # Get the column index and name
        col_index = int(column.replace('#', '')) - 1
        col_name = self.data_treeview["columns"][col_index]
        
        # Get the current value of the cell
        current_value = self.data_treeview.item(row_id, "values")[col_index]
        
        # Open the edit window
        self.open_edit_window(row_id, col_name, col_index, current_value)

    def open_edit_window(self, row_id, col_name, col_index, current_value):
        self.edit_window = Toplevel(self.root)
        self.edit_window.title("Edit Cell")
        
        Label(self.edit_window, text=f"Editing {col_name}").grid(row=0, column=0, padx=10, pady=10)
        self.edit_entry = Entry(self.edit_window)
        self.edit_entry.grid(row=0, column=1, padx=10, pady=10)
        self.edit_entry.insert(0, current_value)
        
        Button(self.edit_window, text="Save", command=lambda: self.save_edit(row_id, col_name, col_index)).grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    def save_edit(self, row_id, col_name, col_index):
        new_value = self.edit_entry.get()
        table_name = self.table_name_entry.get()

        # Debug prints
        print(f"Saving new value: {new_value}")
        print(f"Table name: {table_name}")
        print(f"Column name: {col_name}")

        # Get the primary key column for the specified table
        primary_key_column = self.get_primary_key_column(table_name)
        if primary_key_column is None:
            print(f"Could not find primary key for table: {table_name}")
            return

        # Get the primary key value from the selected row
        primary_key = self.data_treeview.item(row_id, "values")[0]  # Assuming the primary key is the first column
        print(f"Primary key: {primary_key}")

        # Update the database
        try:
            # Update data in the specified table
            self.db_manager.update_data(table_name, {col_name: new_value}, f"{primary_key_column} = '{primary_key}'")
            # Update the Treeview
            self.data_treeview.set(row_id, column=col_name, value=new_value)
            # Close the edit window
            self.edit_window.destroy()
        except sqlite3.OperationalError as e:
            print(f"SQL error: {e}")
            messagebox.showerror("Error", f"SQL error: {e}")

    def get_primary_key_column(self, table_name):
        """Retrieve the primary key column name for the given table."""
        query = f"PRAGMA table_info({table_name})"
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute(query)
            columns_info = cursor.fetchall()
            
            # Debugging: print out columns_info
            print(f"Columns info for {table_name}: {columns_info}")
            
            # Assuming the primary key is always the first column
            return columns_info[0][1] if columns_info else None  # Return the first column name

        except sqlite3.OperationalError as e:
            print(f"Could not retrieve schema for table {table_name}: {e}")
        
        return None  # Return None if no columns found

    def create_column_selection_listbox(self):
        """Create a listbox for selecting columns."""
        self.column_listbox = Listbox(self.data_frame, selectmode=SINGLE)
        self.column_listbox.grid(row=5, column=2, padx=10, pady=10, sticky="nsew")
        self.refresh_column_listbox()  # Initially populate the listbox

    def refresh_column_listbox(self):
        """Refresh the column listbox with columns from the database."""
        table_name = self.table_name_entry.get().strip()
        if table_name:
            existing_columns = self.db_manager.get_table_columns(table_name)
            self.column_listbox.delete(0,END)  # Clear existing entries
            for column in existing_columns:
                self.column_listbox.insert(END, column[0])  # Insert column names

    def update_table(self):
        table_name = self.table_name_entry.get().strip()
        columns_to_add = {}
        
        # Get existing columns from the database
        existing_columns = self.db_manager.get_table_columns(table_name)

        # Print existing columns for debugging
        print(f"Existing columns in {table_name}: {existing_columns}")

        # Gather new column information from the entries
        for name_entry, _, type_var in self.column_entries:
            col_name = name_entry.get().strip()
            col_type = type_var.get()
            if col_name and col_type:
                if col_name not in dict(existing_columns):
                    columns_to_add[col_name] = col_type
                    print(f"Column {col_name} marked for addition with type {col_type}.")
                else:
                    print(f"Column {col_name} already exists. Skipping...")

        # Determine which column to remove based on selection
        selected_column_index = self.column_listbox.curselection()
        columns_to_remove = []
        if selected_column_index:
            selected_column = self.column_listbox.get(selected_column_index)
            if selected_column in dict(existing_columns):
                columns_to_remove.append(selected_column)
                print(f"Column {selected_column} marked for removal.")

        # Print columns to add and remove for debugging
        print(f"Columns to add: {list(columns_to_add.keys())}")
        print(f"Columns to remove: {columns_to_remove}")

        # Begin transaction
        try:
            self.db_manager.connection.execute("BEGIN")

            # Add new columns that do not already exist
            for col_name, col_type in columns_to_add.items():
                try:
                    self.db_manager.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                    print(f"Added column {col_name} of type {col_type}.")
                except sqlite3.OperationalError as e:
                    print(f"Error adding column {col_name}: {e}")

            # Remove selected column if any
            if columns_to_remove:
                temp_table_name = f"{table_name}_temp"

                # Construct the new columns SQL for the temporary table, excluding removed columns
                columns_sql = ", ".join([f"{col[0]} {col[1]}" for col in existing_columns if col[0] not in columns_to_remove])

                if not columns_sql:
                    messagebox.showerror("Error", "Cannot remove all columns from the table.")
                    return  # Exit if all columns are being removed

                # Create a new table without the removed columns
                try:
                    self.db_manager.cursor.execute(f"CREATE TABLE {temp_table_name} ({columns_sql})")
                    print(f"Created temporary table {temp_table_name} with columns: {columns_sql}.")
                except sqlite3.OperationalError as e:
                    print(f"Error creating table {temp_table_name}: {e}")
                    return  # Exit if there was an error creating the new table

                # Prepare the SQL for inserting data into the new table
                select_columns = ", ".join([col[0] for col in existing_columns if col[0] not in columns_to_remove])
                
                insert_sql = f"INSERT INTO {temp_table_name} SELECT {select_columns} FROM {table_name}"
                
                # Insert data into the new table, excluding removed columns
                try:
                    self.db_manager.cursor.execute(insert_sql)
                    print(f"Data transferred to {temp_table_name}.")
                except sqlite3.OperationalError as e:
                    print(f"Error inserting data into {temp_table_name}: {e}")
                    return  # Exit if there was an error inserting data

                # Drop the original table
                try:
                    self.db_manager.cursor.execute(f"DROP TABLE {table_name}")
                    print(f"Dropped original table {table_name}.")
                except sqlite3.OperationalError as e:
                    print(f"Error dropping table {table_name}: {e}")
                    return  # Exit if there was an error dropping the original table

                # Rename the new table to the original name
                try:
                    self.db_manager.cursor.execute(f"ALTER TABLE {temp_table_name} RENAME TO {table_name}")
                    print(f"Renamed {temp_table_name} to {table_name}.")
                except sqlite3.OperationalError as e:
                    print(f"Error renaming table: {e}")
                    return  # Exit if there was an error renaming

            # Commit changes and notify the user
            self.db_manager.connection.commit()
            print(f"Changes committed to {table_name}.")
            messagebox.showinfo("Success", f"Table {table_name} updated.")
            self.populate_treeview()  # Refresh the treeview to reflect changes

        except Exception as e:
            # Rollback on error
            self.db_manager.connection.rollback()
            print(f"Transaction rolled back due to error: {e}")
            messagebox.showerror("Error", f"Failed to update table: {str(e)}")

    def delete_table(self):
        selected_item = self.treeview.selection()
        if selected_item:
            table_name = self.treeview.item(selected_item, "text")
            self.db_manager.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.db_manager.connection.commit()
            self.treeview.delete(selected_item)
            messagebox.showinfo("Success", f"Table {table_name} deleted.")
        else:
            messagebox.showerror("Error", "Please select a table to delete.")

    def show_column_type_help(self):
        messagebox.showinfo("Column Type Help", "Common column types:\n\nINTEGER: For integer values\nTEXT: For text values\nREAL: For floating point values\nBLOB: For binary data\nNUMERIC: For numeric values")
        
    def open_remove_column_dialog(self):
        # Create a new window for selecting a column to remove
        self.remove_column_window = Toplevel(self.root)
        self.remove_column_window.title("Remove Column")
        
        # Frame to hold the radio buttons
        self.radio_buttons_frame = ttk.Frame(self.remove_column_window)
        self.radio_buttons_frame.pack(padx=10, pady=10)

        # Variable to store the selected column index
        self.selected_column_index = IntVar(value=-1)  # Default to -1 (no selection)

        # Refresh the radio buttons with current columns
        self.refresh_column_radio_buttons()

        # Button to confirm removal
        Button(self.remove_column_window, text="Delete Column", command=self.remove_column_entry).pack(pady=10)

    def refresh_column_radio_buttons(self):
        # Clear existing radio buttons
        for widget in self.radio_buttons_frame.winfo_children():
            widget.destroy()

        # Get existing columns from the database
        existing_columns = self.db_manager.get_table_columns(self.table_name_entry.get().strip())

        # Populate the radio buttons with column names
        for index, column in enumerate(existing_columns):
            radio_button = ttk.Radiobutton(self.radio_buttons_frame, text=column[0], variable=self.selected_column_index, value=index)
            radio_button.pack(anchor='w')  # Add the radio button to the frame

    def remove_column_entry(self):
        selected_index = self.selected_column_index.get()
        if selected_index != -1:
            existing_columns = self.db_manager.get_table_columns(self.table_name_entry.get().strip())
            selected_column = existing_columns[selected_index][0]
            
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the column '{selected_column}'? This action cannot be undone."):
                print(f"Deleting column: {selected_column}")
                try:
                    self.db_manager.remove_column(self.table_name_entry.get().strip(), selected_column)
                    messagebox.showinfo("Success", f"Column '{selected_column}' deleted successfully.")
                    self.refresh_column_radio_buttons()  # Refresh radio buttons
                except Exception as e:
                    print(f"Error occurred: {str(e)}")  # Added for debugging
                    messagebox.showerror("Error", f"Failed to delete column '{selected_column}': {str(e)}")
        else:
            messagebox.showerror("Error", "Please select a column to delete.")

    def add_data_entry(self):
        row = len(self.data_entries)
        selected_item = self.treeview.selection()
        if not selected_item:
            return

        table_name = self.treeview.item(selected_item, "text")
        columns = self.db_manager.get_table_columns(table_name)

        column_name_var = StringVar(self.data_frame)
        column_name_var.set(columns[0])  # Default value
        column_name_menu = OptionMenu(self.data_frame, column_name_var, *columns)
        column_name_menu.grid(row=row + 1, column=0, padx=5, pady=5, sticky="ew")

        value_entry = Entry(self.data_frame)
        value_entry.grid(row=row + 1, column=1, padx=5, pady=5, sticky="ew")

        self.data_entries.append((column_name_menu, value_entry))

    def create_table(self):
        table_name = self.table_name_entry.get().strip()
        columns = {}

        for name_entry, type_entry, type_var in self.column_entries:
            col_name = name_entry.get().strip()  # Get the column name
            col_type = type_var.get().strip()  # Get the selected column type from StringVar
            
            if col_name and col_type:
                columns[col_name] = col_type
        
        if columns:
            self.db_manager.create_table(table_name, columns)
            messagebox.showinfo("Success", f"Table {table_name} created.")
            self.populate_treeview()
        else:
            messagebox.showerror("Error", "Please add at least one column.")

    def insert_data(self):
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a table to insert data.")
            return

        table_name = self.treeview.item(selected_item, "text")
        columns = self.db_manager.get_table_columns(table_name)

        data = {}
        for entry in self.data_entries:
            column_name = entry[0].cget("text")  # This should just be the column name
            value = entry[1].get()
            data[column_name.split()[0]] = value  # Split to get only the name

        # Debugging: Print the data being inserted
        print(f"Data to insert into {table_name}: {data}")  # Debugging line

        if not data:
            messagebox.showerror("Error", "Please enter data to insert.")
            return

        try:
            self.db_manager.insert_data(table_name, data)
            messagebox.showinfo("Success", "Data inserted successfully.")
            
            # Clear the input fields after successful insertion
            for entry in self.data_entries:
                entry[1].delete(0, END)  # Clear the entry field

            self.load_data()  # Reload data to reflect the new addition
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert data: {e}")

    def update_data(self, table_name, updates, condition):
        updates_def = ", ".join([f"{col} = ?" for col in updates.keys()])
        values = tuple(updates.values())
        query = f"UPDATE {table_name} SET {updates_def} WHERE {condition}"
        
        # Debug prints
        print(f"Generated query: {query}")
        print(f"Values: {values}")
        
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Data updated in {table_name}: {updates} where {condition}")
        except sqlite3.OperationalError as e:
            print(f"SQL error: {e}")
            raise

    def delete_data(self):
        # Select the row from the data treeview (where the actual data is displayed)
        selected_item = self.data_treeview.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select a row to delete.")
            return

        # Get the selected row's values from the data treeview
        item_values = self.data_treeview.item(selected_item, "values")
        if not item_values:
            messagebox.showerror("Error", "No values found for the selected row.")
            return

        # Debugging: Print the selected row values
        print(f"Selected row values: {item_values}")

        # Check the correct index for the ID column (assuming it's not in the first column)
        unique_id_index = 0  # Set this to the correct column index for ID
        unique_id = item_values[unique_id_index]

        # If unique_id is None, display an error
        if not unique_id:
            messagebox.showerror("Error", "Could not find a valid ID for deletion.")
            return

        # Debugging: Print the unique ID
        print(f"Unique ID for deletion: {unique_id}")

        # Now get the table name from the table treeview (left side)
        selected_table_item = self.treeview.selection()

        if not selected_table_item:
            messagebox.showerror("Error", "Please select a table from the left panel.")
            return

        table_name = self.treeview.item(selected_table_item, "text")

        # Debugging: Print the table name
        print(f"Deleting from table: {table_name}")

        # Prepare the condition for deletion
        condition = "ID = ?"

        try:
            # Debugging: Print the query and values being executed
            print(f"Attempting to delete from {table_name} where {condition} with ID {unique_id}")

            # Call the delete_data method from db_manager with the table name, condition, and ID value
            self.db_manager.delete_data(table_name, condition, (unique_id,))
            messagebox.showinfo("Success", f"Row with ID {unique_id} deleted successfully.")
            
            # Reload data to reflect the deletion
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete data: {str(e)}")
            print(f"Error occurred: {e}")

    def open_sort_menu(self):
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a table to sort data.")
            return

        table_name = self.treeview.item(selected_item, "text")
        columns = self.db_manager.get_table_columns(table_name)

        sort_window = Toplevel(self.root)
        sort_window.title("Sort Data")

        # Sorting options

        Label(sort_window, text="Sort Type:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.sort_type_var = StringVar(value="Alphabetical")
        sort_type_menu = OptionMenu(sort_window, self.sort_type_var, "Alphabetical", "Numerical")
        sort_type_menu.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        Label(sort_window, text="Select Column to Sort By:").grid(row=0, column=0, padx=10, pady=10)
        column_var = StringVar(sort_window)
        column_var.set(columns[0])  # Default value
        OptionMenu(sort_window, column_var, *columns).grid(row=0, column=1, padx=10, pady=10)

        Label(sort_window, text="Select Sorting Order:").grid(row=1, column=0, padx=10, pady=10)
        order_var = StringVar(sort_window)
        order_var.set("Ascending")  # Default value
        OptionMenu(sort_window, order_var, "Ascending", "Descending").grid(row=1, column=1, padx=10, pady=10)

        Button(sort_window, text="Sort", command=lambda: self.sort_data(table_name, column_var.get(), order_var.get())).grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    
    def sort_data(self, table_name, column, order):
        if not table_name or not column or not order:
            messagebox.showerror("Error", "Invalid sorting parameters.")
            return

        # Map user-friendly sorting order to SQL keywords
        order_sql = "ASC" if order == "Ascending" else "DESC"

        order_by = f"{column} {order_sql}"
        self.load_data(order_by=order_by)

    def search_data(self):
        search_term = self.search_entry.get()
        if not search_term:
            self.load_data(order_by=None)

        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a table to search data.")
            return

        table_name = self.treeview.item(selected_item, "text")
        columns = self.db_manager.get_table_columns(table_name)
        search_condition = " OR ".join([f"{col} LIKE '%{search_term}%'" for col in columns])
        self.load_data(search_term=search_condition)

if __name__ == "__main__":
    root = Tk()
    app = DataBaseManagerGUI(root)
    root.mainloop()