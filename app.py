import sys
import pandas as pd
from lib.ops import DataCleanerApp
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataCleanerApp()
    window.show()
    sys.exit(app.exec())
