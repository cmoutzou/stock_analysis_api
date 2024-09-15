import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication
from gui.charts_window import *

def main():
    app = QApplication(sys.argv)
    
    # Replace 'AAPL' with any valid stock symbol you'd like to test with
    stock_symbol = 'AAPL'

    # Create an instance of ChartsWindow
    window = ChartsWindow(stock_symbol)

    # Show the window
    window.show()

    # Execute the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
