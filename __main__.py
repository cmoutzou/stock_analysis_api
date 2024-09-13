import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Get the current working directory and dynamically construct the path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(base_dir, "resources", "styles", "dark_theme.qss")

    # Load and apply the dark theme
    with open(style_path, "r") as style_file:
        app.setStyleSheet(style_file.read())

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())