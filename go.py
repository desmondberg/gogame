from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QDockWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from board import Board
from game_logic import GameControlPanel


class Info(QWidget):
    def __init__(self):
        super().__init__()


class Go(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def getBoard(self):
        return self.board

    def getScoreBoard(self):
        return self.scoreBoard

    def initUI(self):
        '''Initiates application UI'''
        self.setWindowTitle('Go')
        # Create the central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)  # Create a layout for the central widget

        self.board = Board(self)
        self.board.setFixedSize(700, 700)
        layout.addWidget(self.board, alignment=Qt.AlignmentFlag.AlignCenter)  # Center the board in the layout

        # Set the central widget with the layout
        self.setCentralWidget(central_widget)

        # Create control panel dock widget
        control_dock = QDockWidget("Score Board", self)
        # remove close and extract window options
        control_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        # Enhance Qdock for better visual
        control_dock.setStyleSheet("""
            QDockWidget::title {
                text-align: center;
                padding: 10px 0px 10px 0px;
            }
            QDockWidget {
                font-size: 30px;
                font-weight: 800;
                letter-spacing: 2px;
                text-transform: uppercase;
                color: #2C3E50;
            }
        """)

        # Create the control panel
        self.control_panel = GameControlPanel(self.board)
        self.control_panel.setFixedSize(400,350)
        self.board.control_panel = self.control_panel
        control_dock.setWidget(self.control_panel)

        # Add the dock widget to the right side of the main window
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, control_dock)
        self.show()
