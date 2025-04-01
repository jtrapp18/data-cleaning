import json
import os
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QPushButton, QLabel, QDialog, QFileDialog,
    QRadioButton, QCheckBox, QHBoxLayout, QTextEdit, QWidget, QTabWidget, QFormLayout, QLineEdit
)
import pandas as pd
from .config import ClientPath

class DataImport(QDialog):
    def __init__(self, path: str, name=None, spec_file=None):
        super().__init__()

        self.path = path
        if self.name:
            self.name = name
        else:
            self.name = os.path.splitext(os.path.basename(path))[0]

        self.setWindowTitle("Import Manager")
        self.setFixedSize(500, 400)

        self.layout = QVBoxLayout()
        self.dataframe = None

        self.spec_widgets = {
            'delimited': QRadioButton("Delimited (CSV, TSV, etc.)"),
            'fixed_width': QRadioButton("Fixed Width"),
            'contains_headers': QCheckBox("File contains headers"),
            'trim_spaces': QCheckBox("Trim leading/trailing spaces"),
            'utf8_encoding': QCheckBox("Use UTF-8 encoding"),
            'columns': {}
        }
        if spec_file:
            self.default_specs = self.load_specs(spec_file)
        else:
            self.default_specs = self.get_default_specs()

        navigation = self.create_navigation_buttons()

        # Create QTabWidget
        self.tabs = QTabWidget()
        self.tab_count = 0

        self.layout.addWidget(self.tabs)
        self.layout.addLayout(navigation)

        # self.create_step_tabs()
        self.step_1_import_options()

        self.setLayout(self.layout)

    def create_navigation_buttons(self):
        """Creates navigation buttons (Next, Previous, Cancel)."""
        navigation = QHBoxLayout()

        prev_button = QPushButton("Previous")
        next_button = QPushButton("Next")
        cancel_button = QPushButton("Cancel")

        prev_button.clicked.connect(self.prev_step)
        next_button.clicked.connect(self.next_step)
        cancel_button.clicked.connect(self.reject)

        navigation.addWidget(prev_button)
        navigation.addWidget(next_button)
        navigation.addWidget(cancel_button)

        return navigation

    def step_1_import_options(self):
        """Step 1: Import Options."""
        tab = QWidget()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Importing: {self.path}"))

        curr_step_widgets = ['delimited', 'fixed_width', 'contains_headers', 'trim_spaces', 'utf8_encoding']

        for widget in curr_step_widgets:
            layout.addWidget(self.spec_widgets[widget])

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Step 1: Import Options")

        self.tab_count += 1

        self.apply_defaults()

    def apply_defaults(self):
        self.spec_widgets['delimited'].setChecked(self.default_specs['delimited'])
        self.spec_widgets['fixed_width'].setChecked(self.default_specs['fixed_width'])
        self.spec_widgets['contains_headers'].setChecked(self.default_specs['contains_headers'])
        self.spec_widgets['trim_spaces'].setChecked(self.default_specs['trim_spaces'])
        self.spec_widgets['utf8_encoding'].setChecked(self.default_specs['utf8_encoding'])
        
    def import_data(self):
        """Reads file based on user selections and returns a DataFrame."""
        specs = self.get_current_specs()

        import_type = "Delimited" if specs['delimited'] else "Fixed Width"
        use_headers = 0 if specs['contains_headers'] else None
        encoding = "utf-8" if specs['utf8_encoding'] else None

        try:
            if import_type == "Delimited":
                df = pd.read_csv(self.path, delimiter=None, header=use_headers, encoding=encoding)
            else:
                df = pd.read_fwf(self.path, header=use_headers, encoding=encoding)

            if specs['trim_spaces']:
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            self.dataframe = df
            print(df.head())
        except Exception as e:
            print(f"Error importing file: {e}")

    def step_2_data_preview(self):
        """Step 2: Data Preview."""
        if self.tab_count < 2:

            tab = QWidget()

            layout = QVBoxLayout()

            self.data_preview = QTextEdit()
            self.data_preview.setReadOnly(True)

            if self.dataframe is not None:
                preview_text = self.dataframe.head().to_string(index=False)
                self.data_preview.setText(preview_text)
            else:
                self.data_preview.setText("No data loaded.")

            layout.addWidget(QLabel("Data Preview:"))
            layout.addWidget(self.data_preview)

            tab.setLayout(layout)

            self.tabs.addTab(tab, "Step 2: Data Preview")

            self.tab_count += 1

    def step_3_column_selection(self):
        """Step 3: Column Selection & Renaming."""

        if self.tab_count < 3:
            tab = QWidget()

            layout = QVBoxLayout()
            column_widgets = {}

            if self.dataframe is None:
                layout.addWidget(QLabel("No data available."))
                tab.setLayout(layout)
                return

            layout.addWidget(QLabel("Select columns to import & rename:"))
            form_layout = QFormLayout()
            
            for col in self.dataframe.columns:
                # Create checkbox for whether the column is needed
                checkbox = QCheckBox(col)
                checkbox.setChecked(True)  # By default, the column is selected (checked)

                # Create line edit for renaming
                rename_input = QLineEdit(str(col))  # Default to the same name as the column

                # Add the checkbox and rename input to the form layout
                form_layout.addRow(checkbox, rename_input)

                # Store both widgets (checkbox and rename input) in a dictionary
                column_widgets[col] = (checkbox, rename_input)

            self.spec_widgets['columns'] = column_widgets

            layout.addLayout(form_layout)
            tab.setLayout(layout)

            self.tabs.addTab(tab, "Step 3: Column Selection & Renaming")

            self.tab_count += 1

    def apply_column_selection(self):
        """Applies column selection and renaming based on user input."""
        selected_columns = []
        renamed_columns = {}

        # Loop through the column widgets to check selected columns and their new names
        for col, (checkbox, rename_input) in self.spec_widgets['columns'].items():
            if checkbox.isChecked():  # If the column is selected
                selected_columns.append(col)
                renamed_columns[col] = rename_input.text()  # Rename column if input is provided

        # Apply selection and renaming
        self.dataframe = self.dataframe[selected_columns].rename(columns=renamed_columns)

    def next_step(self):
        """Handles Next button click."""

        tab_ops = {
            1: [self.import_data,
                self.step_2_data_preview],
            2: [self.step_3_column_selection],
            3: [self.apply_column_selection,
                self.save_specs,
                self.save_data,
                self.accept]
        }

        next_page = self.tabs.currentIndex() + 1

        for op in tab_ops[next_page]:
            op()
        
        self.tabs.setCurrentIndex(next_page)  # Move to Step 2

    def prev_step(self):
        """Handles Previous button click."""
        current_index = self.tabs.currentIndex()
        if current_index > 0:
            self.tabs.setCurrentIndex(current_index - 1)  # Switch to the previous tab

    def get_dataframe(self):
        """Returns the imported DataFrame."""
        return self.dataframe

    def save_specs(self):
        """Save user specifications to a JSON file."""
        if self.dataframe is None:
            print("No data available to save.")
            return

        specs = self.get_current_specs()

        path = get_path('database', 'specs', create=True, db_name=self.name)

        if path:
            try:
                with open(path, 'w') as f:
                    json.dump(specs, f, indent=4)
                print(f"Specs saved to {path}")
            except Exception as e:
                print(f"Error saving specs: {e}")

    def save_data(self):
        """Save the current dataframe to a Parquet file."""
        if self.dataframe is None or self.dataframe.empty:
            print("No data available to save.")
            return

        path = get_path('database', 'data', create=True, db_name=self.name)

        if path:
            try:
                self.dataframe.to_parquet(path, index=False)
                print(f"Data saved to {path}")
            except Exception as e:
                print(f"Error saving data: {e}")

    def get_default_specs(self):
        return {
            'delimited': True,
            'fixed_width': False,
            'contains_headers': True,
            'trim_spaces': False,
            'utf8_encoding': False
        }
    
    def get_current_specs(self):

        col_dict = {}

        # Loop through the column widgets to check selected columns and their new names
        for col, (checkbox, rename_input) in self.spec_widgets['columns'].items():
            include = checkbox.isChecked()
            mapping = rename_input.text()

            col_dict[col] = (include, mapping)

        return {
            'delimited': self.spec_widgets['delimited'].isChecked(),
            'fixed_width': self.spec_widgets['fixed_width'].isChecked(),
            'contains_headers': self.spec_widgets['contains_headers'].isChecked(),
            'trim_spaces': self.spec_widgets['trim_spaces'].isChecked(),
            'utf8_encoding': self.spec_widgets['utf8_encoding'].isChecked(),
            'columns': col_dict
        }
    
    def load_specs(self, spec_file):
        """Load previously saved specifications."""
        # file_name, _ = QFileDialog.getOpenFileName(self, "Load Specs", "", "JSON Files (*.json)")

        if spec_file:
            try:
                with open(spec_file, 'r') as f:
                    specs = json.load(f)

                print(f"Specs loaded from {spec_file}")
                return specs
            except Exception as e:
                print(f"Error loading specs: {e}")

# Test the Import Manager
if __name__ == "__main__":
    app = QApplication([])
    importer = DataImport("example.csv")
    if importer.exec():  # If dialog is accepted
        df = importer.get_dataframe()
        if df is not None:
            print("Final Imported Data:")
            print(df.head())