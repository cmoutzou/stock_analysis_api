import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd

class ChartsWindow(QMainWindow):
    def __init__(self, stock_data=None, predictions=None):
        super().__init__()
        self.setWindowTitle("Charts")
        self.setGeometry(200, 200, 900, 700)

        # Create the main widget and layout
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)

        # Test Plotly rendering with sample data
        self.test_plotly(layout, stock_data, predictions)

    def test_plotly(self, layout, stock_data, predictions):
        """
        Test Plotly chart rendering.
        """
        # Create a sample Plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode='lines+markers', name='Test Line'))
        fig.update_layout(title='Sample Chart', template='plotly_dark')

        # Convert the chart figure to HTML
        chart_html = pio.to_html(fig, full_html=False)
        print("Chart HTML content:")
        print(chart_html)

        # Create QWebEngineView to display Plotly chart
        chart_view = QWebEngineView()
        chart_view.setHtml(chart_html)
        layout.addWidget(chart_view)

        # If stock_data and predictions are provided, attempt to create and display charts
        if stock_data is not None and not stock_data.empty:
            fig = self.create_figure(stock_data, predictions)
            chart_html = pio.to_html(fig, full_html=False)
            chart_view = QWebEngineView()
            chart_view.setHtml(chart_html)
            layout.addWidget(chart_view)

    def create_figure(self, stock_data, predictions):
        """
        Creates a Plotly figure for stock data and predictions.
        """
        fig = go.Figure()

        # Add stock data trace
        fig.add_trace(go.Scatter(x=stock_data['timestamp'], y=stock_data['close'], mode='lines', name='Close'))

        # Add predictions trace if available
        if predictions is not None:
            fig.add_trace(go.Scatter(x=predictions['Date'], y=predictions['Prediction'], mode='lines', name='Prediction'))

        # Customize layout
        fig.update_layout(
            title='Stock Data and Predictions',
            xaxis_title='Date',
            yaxis_title='Value',
            template='plotly_dark'
        )

        return fig

# Sample data
stock_data = pd.DataFrame({
    'timestamp': pd.date_range(start='2023-01-01', periods=10),
    'close': [100 + i for i in range(10)]
})

predictions = pd.DataFrame({
    'Date': pd.date_range(start='2023-01-01', periods=10),
    'Prediction': [100 + i + 5 for i in range(10)]
})

def main():
    app = QApplication(sys.argv)  # Create a QApplication instance
    window = ChartsWindow(stock_data, predictions)
    window.show()
    sys.exit(app.exec_())  # Start the event loop

if __name__ == "__main__":
    main()
