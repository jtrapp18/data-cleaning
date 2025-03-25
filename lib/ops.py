from .cleaning import CleanData
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout, QPushButton, QLayout, QComboBox,
    QWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QTabWidget, QLineEdit, QLabel
)
import pandas as pd
import os

def display_after_operation(func):
    """Decorator to refresh DataFrame display after an operation."""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)

        self.display_dataframe()
        return result
    return wrapper

class DataCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Cleaning App")
        self.setGeometry(100, 100, 800, 600)
        
        self.cleaner = None
        self.savepoints_dir = "savepoints"
        self.sections = {}
        self.buttons = {}

        self.initUI()

    def create_button(self, label, operation):
        """Reusable function to add a button."""
        new_button = QPushButton(label)
        new_button.clicked.connect(operation)
        self.buttons[label] = new_button  # Store button reference

        return new_button
    
    def create_button_container(self, buttons):
        button_container = QHBoxLayout()
        for button in buttons:
            button_container.addWidget(button)

        return button_container

    def initUI(self):
        """Initialize the UI layout and components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Dropdown for selecting an existing client
        self.client_label = QLabel("Select Client:")
        layout.addWidget(self.client_label)

        self.client_dropdown = QComboBox()
        self.load_clients()
        self.client_dropdown.currentIndexChanged.connect(self.update_years)
        layout.addWidget(self.client_dropdown)

        # Input box for new client (hidden by default)
        self.new_client_input = QLineEdit()
        self.new_client_input.setPlaceholderText("Enter new client name...")
        self.new_client_input.setVisible(False)
        self.new_client_input.returnPressed.connect(self.add_new_client)
        layout.addWidget(self.new_client_input)

        # # Button for adding a new client
        # new_button = self.create_button('Add New Client', self.add_new_client)
        # layout.addWidget(new_button)

        # Dropdown for selecting a year
        self.year_label = QLabel("Select Year:")
        layout.addWidget(self.year_label)

        self.year_dropdown = QComboBox()
        self.year_dropdown.currentIndexChanged.connect(self.load_selected_data)
        layout.addWidget(self.year_dropdown)

        # # Button for adding a new year
        # new_button = self.create_button('Add New Year', self.add_new_year)
        # layout.addWidget(new_button)

        # Button to Load Data
        self.load_button = QPushButton("Load Data")
        self.load_button.clicked.connect(self.load_selected_data)
        layout.addWidget(self.load_button)

        # Placeholder for additional UI elements
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def load_clients(self):
        """Loads client names from the savepoints folder."""
        self.client_dropdown.clear()
        self.client_dropdown.addItem("Select Client")
        if os.path.exists(self.savepoints_dir):
            clients = [d for d in os.listdir(self.savepoints_dir) if os.path.isdir(os.path.join(self.savepoints_dir, d))]
            self.client_dropdown.addItems(clients)
        self.client_dropdown.addItem("Add New...")

    def update_years(self):
        """Updates year dropdown when a client is selected."""
        self.year_dropdown.clear()
        selected_client = self.client_dropdown.currentText()

        if selected_client == "Add New...":
            self.new_client_input.setVisible(True)
            self.new_client_input.setFocus()
            self.year_dropdown.setEnabled(False)
            return
        else:
            self.new_client_input.setVisible(False)

        if selected_client == "Select Client":
            self.year_dropdown.setEnabled(False)
            return
        
        self.year_dropdown.setEnabled(True)
        self.year_dropdown.addItem("Select Year")
        
        client_path = os.path.join(self.savepoints_dir, selected_client)
        if os.path.exists(client_path):
            years = [d for d in os.listdir(client_path) if os.path.isdir(os.path.join(client_path, d))]
            self.year_dropdown.addItems(years)
        
        self.year_dropdown.addItem("Add New...")

    def add_new_client(self):
        """Adds a new client based on user input."""
        new_client = self.new_client_input.text().strip()
        if new_client:
            os.makedirs(os.path.join(self.savepoints_dir, new_client), exist_ok=True)
            self.load_clients()  # Refresh dropdown
            self.client_dropdown.setCurrentText(new_client)
            self.new_client_input.clear()
            self.new_client_input.setVisible(False)

    def add_new_year(self):
        """Adds a new year based on user input."""
        selected_client = self.client_dropdown.currentText()
        if selected_client in ["Select Client", "Add New..."]:
            self.status_label.setText("⚠️ Please select a valid client first.")
            return
        
        new_year, ok = QLineEdit().text(), True  # Simulated input dialog
        if ok and new_year:
            os.makedirs(os.path.join(self.savepoints_dir, selected_client, new_year), exist_ok=True)
            self.update_years()  # Refresh dropdown
            self.year_dropdown.setCurrentText(new_year)

    def load_selected_data(self):
        """Loads saved data when both client and year are selected."""
        selected_client = self.client_dropdown.currentText()
        selected_year = self.year_dropdown.currentText()

        if selected_client in ["Select Client", "Add New..."] or selected_year in ["Select Year", "Add New..."]:
            self.status_label.setText("⚠️ Please select a valid client and year.")
            return
        
        self.cleaner = CleanData(client=selected_client, year=selected_year)
        self.status_label.setText(f"✅ Loaded data for {selected_client} - {selected_year}")

    def add_tab(self, label, parent, children):
        """Create and add a new tab to the tab widget."""
        new_tab = QWidget()
        layout = QVBoxLayout()
        new_tab.setLayout(layout)

        parent.addTab(new_tab, label)
        self.sections[label] = layout  # Store layout for later use

        for child in children:
            if isinstance(child, QLayout):
                layout.addLayout(child)
            elif isinstance(child, QWidget):
                layout.addWidget(child)
            else:
                print(f"Warning: Unexpected type {type(child)} in add_tab()")

        return layout
            
    def populate_csv_tab(self):
        """Populate the File Operations tab with buttons."""
        parent = self.sections['main_navigation']
        buttons = [
            self.create_button('Load CSV', self.select_and_load_csv),
            self.create_button('Export Cleaned Data', self.export_csv),
        ]
        button_container = self.create_button_container(buttons)
        self.add_tab('File Operations', parent, children=[button_container])

    def populate_data_tab(self):
        """Populate the Data Manipulation tab with buttons."""
        parent = self.sections['main_navigation']
        buttons = [
            self.create_button('Remove Duplicates', self.remove_duplicates),
            self.create_button('Merge Another CSV', self.merge_csv),
            self.create_button('Add Column', lambda: self.sections['Add Column'].setVisible(True))
        ]
        children = [
            self.create_button_container(buttons),
            self.add_add_column_tab()
        ]
        self.add_tab('Data Manipulation', parent, children)

    def add_add_column_tab(self):
        """Create and hide the Add Column section initially."""
        # dataLayout = self.sections['Data Manipulation']

        addColumnSection = QWidget()
        addColumnLayout = QVBoxLayout()

        # Column Name Input
        self.columnNameInput = QLineEdit()
        self.columnNameInput.setPlaceholderText("Column Name")
        addColumnLayout.addWidget(QLabel("Column Name"))
        addColumnLayout.addWidget(self.columnNameInput)

        # Formula Input
        self.formulaInput = QLineEdit()
        self.formulaInput.setPlaceholderText("Formula (Python expression)")
        addColumnLayout.addWidget(QLabel("Formula"))
        addColumnLayout.addWidget(self.formulaInput)

        new_button = self.create_button('Submit New Column', self.add_column)
        addColumnLayout.addWidget(new_button)  # Fixed issue

        addColumnSection.setLayout(addColumnLayout)
        addColumnSection.setVisible(False)

        self.sections['Add Column'] = addColumnSection

        # dataLayout.addWidget(self.addColumnSection)
        return addColumnSection

    def display_dataframe(self):
        """Display the loaded DataFrame in the table widget."""
        if self.cleaner.df is not None and not self.cleaner.df.empty:
            df = self.cleaner.df
            self.tableWidget.setRowCount(df.shape[0])
            self.tableWidget.setColumnCount(df.shape[1])
            self.tableWidget.setHorizontalHeaderLabels(df.columns)

            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        else:
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
    
    def select_and_load_csv(self):
        """Load CSV file into the cleaner."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            print('path', file_path)
            self.cleaner.load_csv(file_path)
            self.display_dataframe()

    def remove_duplicates(self):
        """Remove duplicate rows from the DataFrame."""
        self.cleaner.remove_duplicates()
        self.display_dataframe()

    def merge_csv(self):
        """Merge another CSV into the existing DataFrame."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV to Merge", "", "CSV Files (*.csv)")
        if file_path:
            merge_df = pd.read_csv(file_path)
            if self.cleaner.df is not None:
                self.cleaner.df = pd.concat([self.cleaner.df, merge_df], ignore_index=True)
            else:
                self.cleaner.df = merge_df
            self.display_dataframe()

    def export_csv(self):
        """Export the cleaned DataFrame to a CSV file."""
        if self.cleaner.df is not None and not self.cleaner.df.empty:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if file_path:
                self.cleaner.df.to_csv(file_path, index=False)

    def show_hide_section(self, section, show=True):
        """Show a hidden section dynamically."""
        if hasattr(self, section):
            getattr(self, section).setVisible(show)

    def add_column(self):
        """Add a new column to the DataFrame based on user input."""
        column_name = self.columnNameInput.text()
        formula = self.formulaInput.text()

        if column_name and formula:
            try:
                self.cleaner.add_col(column_name, formula)
            except Exception as e:
                print(f"Error applying formula: {e}")
        self.display_dataframe()