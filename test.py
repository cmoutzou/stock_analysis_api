from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
import plotly.io as pio

class ChartsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Charts Window")
        self.setGeometry(200, 200, 1200, 800)

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and set up QWebEngineView
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        # Generate and display the chart figure
        fig = self.create_figure()
        self.display_chart(fig)

    def create_figure(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode='lines+markers'))
        fig.update_layout(title="Test Chart", xaxis_title="X Axis", yaxis_title="Y Axis")
        return fig

    def display_chart(self, fig):
        chart_html = pio.to_html(fig, full_html=False)
        print(chart_html[:5000])  # Print the first 5000 characters for debugging
        self.browser.setHtml(chart_html)

if __name__ == "__main__":
    app = QApplication([])
    window = ChartsWindow()
    window.show()
    app.exec_()
