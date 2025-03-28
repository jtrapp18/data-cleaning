import json

from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QPushButton, QLabel, QDialog, QFileDialog,
    QRadioButton, QCheckBox, QHBoxLayout, QTextEdit, QWidget, QTabWidget, QFormLayout, QLineEdit
)
import pandas as pd

class DataImport(QDialog):
    def __init__(self, path: str):
        super().__init__()

        self.path = path
        self.setWindowTitle("Import Manager")
        self.setFixedSize(500, 400)

        self.layout = QVBoxLayout()
        self.dataframe = None
        self.column_mappings = {}

        navigation = self.create_navigation_buttons()

        # Create QTabWidget
        self.tabs = QTabWidget()
        self.tab_count = 0

        self.layout.addWidget(self.tabs)
        self.layout.addLayout(navigation)

        # self.create_step_tabs()
        self.step_1_import_options()

        self.column_widgets = {}

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

        self.delimited_radio = QRadioButton("Delimited (CSV, TSV, etc.)")
        self.fixed_width_radio = QRadioButton("Fixed Width")
        self.delimited_radio.setChecked(True)

        layout.addWidget(self.delimited_radio)
        layout.addWidget(self.fixed_width_radio)

        self.header_checkbox = QCheckBox("File contains headers")
        self.trim_spaces_checkbox = QCheckBox("Trim leading/trailing spaces")
        self.encoding_checkbox = QCheckBox("Use UTF-8 encoding")

        layout.addWidget(self.header_checkbox)
        layout.addWidget(self.trim_spaces_checkbox)
        layout.addWidget(self.encoding_checkbox)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Step 1: Import Options")

        self.tab_count += 1

    def import_data(self):
        """Reads file based on user selections and returns a DataFrame."""

        import_type = "Delimited" if self.delimited_radio.isChecked() else "Fixed Width"
        use_headers = 0 if self.header_checkbox.isChecked() else None
        self.header_checkbox.setChecked(True)
        encoding = "utf-8" if self.encoding_checkbox.isChecked() else None

        try:
            if import_type == "Delimited":
                df = pd.read_csv(self.path, delimiter=None, header=use_headers, encoding=encoding)
            else:
                df = pd.read_fwf(self.path, header=use_headers, encoding=encoding)

            if self.trim_spaces_checkbox.isChecked():
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
                self.column_widgets[col] = (checkbox, rename_input)

            layout.addLayout(form_layout)
            tab.setLayout(layout)

            self.tabs.addTab(tab, "Step 3: Column Selection & Renaming")

            self.tab_count += 1

    def apply_column_selection(self):
        """Applies column selection and renaming based on user input."""
        selected_columns = []
        renamed_columns = {}

        # Loop through the column widgets to check selected columns and their new names
        for col, (checkbox, rename_input) in self.column_widgets.items():
            if checkbox.isChecked():  # If the column is selected
                selected_columns.append(col)
                renamed_columns[col] = rename_input.text()  # Rename column if input is provided

        # Apply selection and renaming
        self.dataframe = self.dataframe[selected_columns].rename(columns=renamed_columns)

    def next_step(self):
        """Handles Next button click."""

        tab_ops = {
            1: [lambda: print("something happened"),
                self.import_data,
                self.step_2_data_preview],
            2: [self.step_3_column_selection],
            3: [self.apply_column_selection,
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

        # Collect column selection and renaming data
        specs = {}
        for col, (checkbox, rename_input) in self.column_widgets.items():
            specs[col] = {
                "selected": checkbox.isChecked(),
                "new_name": rename_input.text()
            }

        # Open a file dialog to let the user choose where to save the spec
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Specs", "", "JSON Files (*.json)")

        if file_name:
            try:
                with open(file_name, 'w') as f:
                    json.dump(specs, f, indent=4)
                print(f"Specs saved to {file_name}")
            except Exception as e:
                print(f"Error saving specs: {e}")

    def load_specs(self):
        """Load previously saved specifications."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Specs", "", "JSON Files (*.json)")

        if file_name:
            try:
                with open(file_name, 'r') as f:
                    specs = json.load(f)

                # Apply loaded specs (column selection & renaming)
                for col, spec in specs.items():
                    if col in self.column_widgets:
                        checkbox, rename_input = self.column_widgets[col]
                        checkbox.setChecked(spec['selected'])
                        rename_input.setText(spec['new_name'])

                print(f"Specs loaded from {file_name}")
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