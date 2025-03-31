from .clean_data import CleanData
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout, QPushButton, QLayout, QComboBox,
    QWidget, QTableWidget, QDialog, QTableWidgetItem, QHBoxLayout, QTabWidget, QLineEdit, QLabel
)
import pandas as pd
import os
from .config import CONFIG
from .data_import import DataImport
        
class DataCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Cleaning App")
        self.setGeometry(100, 100, 800, 600)
        self.status_label = QLabel("")
        
        self.cleaner = None
        self.savepoints_dir = CONFIG['paths']['data']
        self.sections = {}
        self.buttons = {}

        self.client_dropdown = None
        self.new_client_input = None
        self.year_dropdown = None
        self.new_year_input = None

        self.table_widget = None
        self.dbWidget = None

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

        mainLayout = QVBoxLayout()

        selection_container = self.create_client_year_selections()
        mainLayout.addLayout(selection_container)

        navigation = QTabWidget()
        mainLayout.addWidget(navigation)

        # Populate tabs with buttons and content
        csvTab = self.create_csv_tab()
        navigation.addTab(csvTab, 'Database')

        dataTab = self.create_data_tab()
        navigation.addTab(dataTab, 'Data Manipulation')

        # Set the main layout as central widget
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def create_table_widget(self):
         # Table Widget for displaying the DataFrame
         table_widget = QTableWidget()
         table_widget.setRowCount(0)
         table_widget.setColumnCount(0)
         
         return table_widget

    def create_client_year_selections(self):
        widgets = []

        # Dropdown for selecting an existing client
        client_label = QLabel("Select Client:")
        widgets.append(client_label)

        self.client_dropdown = QComboBox()
        self.load_clients()
        self.client_dropdown.currentIndexChanged.connect(self.update_years)
        widgets.append(self.client_dropdown)

        # Input box for new client (hidden by default)
        self.new_client_input = QLineEdit()
        self.new_client_input.setPlaceholderText("Enter new client name...")
        self.new_client_input.setVisible(False)
        self.new_client_input.returnPressed.connect(self.add_new_client)
        widgets.append(self.new_client_input)

        # Dropdown for selecting a year
        year_label = QLabel("Select Year:")
        widgets.append(year_label)

        self.year_dropdown = QComboBox()
        self.year_dropdown.currentIndexChanged.connect(self.load_selected_data)
        widgets.append(self.year_dropdown)

        # Input box for new client (hidden by default)
        self.new_year_input = QLineEdit()
        self.new_year_input.setPlaceholderText("Enter new year...")
        self.new_year_input.setVisible(False)
        self.new_year_input.returnPressed.connect(self.add_new_year)
        widgets.append(self.new_year_input)

        # Button to Load Data
        load_button = QPushButton("Load Data")
        load_button.clicked.connect(self.load_selected_data)
        widgets.append(load_button)

        selection_container = QHBoxLayout()
        for widget in widgets:
            selection_container.addWidget(widget)

        return selection_container
    
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

        new_year = self.new_year_input.text().strip()
        if new_year:
            client_path = os.path.join(self.savepoints_dir, selected_client)
            new_year_path = os.path.join(client_path, new_year)
            
            # Create new year directory if it doesn't exist
            if not os.path.exists(new_year_path):
                os.makedirs(new_year_path)
                self.update_years()  # Refresh year dropdown
                self.year_dropdown.setCurrentText(new_year)

            # Clear and hide the new year input
            self.new_year_input.clear()
            self.new_year_input.setVisible(False)

    def load_selected_data(self):
        """Loads saved data when both client and year are selected."""

        if self.year_dropdown.currentText() == "Add New...":
            self.new_year_input.setVisible(True)
            self.new_year_input.setFocus()
            return
        else:
            self.new_year_input.setVisible(False)

        selected_client = self.client_dropdown.currentText()
        selected_year = self.year_dropdown.currentText()

        if selected_client in ["Select Client", "Add New..."] or selected_year in ["Select Year", "Add New..."]:
            self.status_label.setText("⚠️ Please select a valid client and year.")
            return
        
        self.cleaner = CleanData(client=selected_client, year=selected_year)
        self.status_label.setText(f"✅ Loaded data for {selected_client} - {selected_year}")

    def create_tab(self, label, children):
        """Create and add a new tab to the tab widget."""
        new_tab = QWidget()
        layout = QVBoxLayout()
        new_tab.setLayout(layout)

        self.sections[label] = layout

        for child in children:
            if isinstance(child, QLayout):
                layout.addLayout(child)
            elif isinstance(child, QWidget):
                layout.addWidget(child)
            else:
                print(f"Warning: Unexpected type {type(child)} in add_tab()")

        return new_tab
            
    def create_csv_tab(self):
        """Populate the File Operations tab with buttons."""
        buttons = [
            self.create_button('Load CSV', self.select_and_load_csv),
            self.create_button('Export Cleaned Data', self.export_csv),
        ]

        button_container = self.create_button_container(buttons)
        self.db_widget = self.create_table_widget()

        children = [
            button_container,
            self.db_widget
        ]

        new_tab = self.create_tab('File Operations', children=children)

        return new_tab

    def create_data_tab(self):
        """Populate the Data Manipulation tab with buttons."""
        buttons = [
            self.create_button('Remove Duplicates', self.remove_duplicates),
            self.create_button('Merge Another CSV', self.merge_csv),
            self.create_button('Add Column', lambda: self.sections['Add Column'].setVisible(True))
        ]

        self.table_widget = self.create_table_widget()

        children = [
            self.create_button_container(buttons),
            self.create_add_column_section(),
            self.table_widget
        ]
        
        new_tab = self.create_tab('Data Manipulation', children)

        return new_tab

    def create_add_column_section(self):
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
            self.table_widget.setRowCount(df.shape[0])
            self.table_widget.setColumnCount(df.shape[1])
            self.table_widget.setHorizontalHeaderLabels(df.columns)

            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    self.table_widget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        else:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
    
    def select_and_load_csv(self):
        """Load CSV file into the cleaner."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            importer = DataImport(file_path)

        if importer.exec():  # If dialog is accepted
            df = importer.get_dataframe()
            if df is not None:  
                self.cleaner.load_df(file_path, df)
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