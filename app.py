import sys
import pandas as pd
from lib.ops import DataCleanerApp
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load QSS file
    with open("style.qss", "r") as file:
        app.setStyleSheet(file.read())
        
    window = DataCleanerApp()
    window.show()
    sys.exit(app.exec())
