from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QDockWidget, QVBoxLayout, QDialog, QLabel, QPushButton, \
    QScrollArea
from PyQt6.QtCore import Qt

from board import Board
from game_logic import GameControlPanel


class Info(QWidget):
    def __init__(self):
        super().__init__()


class Go(QMainWindow):

    def __init__(self):
        super().__init__()
        main_menu = self.menuBar()
        main_menu.setNativeMenuBar(False)
        main_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        # Style the menu bar
        main_menu.setStyleSheet("""
            QMenuBar {
                background-color: #363D42;
                color: white;
                padding: 6px;
                margin-bottom: 4px;
                font-size: 14px;
                font-weight: 300;
                letter-spacing: 2px;
            }
            QMenuBar::item {
                padding: 5px 10px;
                margin-right: 5px;
                background: transparent;
                border-radius: 4px;
            }
            QMenuBar::item:selected { background-color: #3B4B57;}
            QMenu::item { padding: 10px; }
            QMenu::item:selected { background-color: #3B4B57; }
        """)
        help_menu = main_menu.addMenu("Instructions")
        instructions_action = QAction("How to Play", self)
        instructions_action.setShortcut("Ctrl+I")
        instructions_action.triggered.connect(self.show_instructions)
        help_menu.addAction(instructions_action)

        tips_action = QAction("Tips && Tricks", self)
        tips_action.setShortcut("Ctrl+T")
        tips_action.triggered.connect(self.show_tips)
        help_menu.addAction(tips_action)
        self.initUI()

    # Method to display Go instructions in a QDialog with a scrollable area
    def show_instructions(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("How to Play Go")
        dialog.setFixedSize(600, 500)

        # The main layout for the dialog
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)

        # Scroll area to hold the content
        scroll_area = QScrollArea(dialog)
        scroll_area.setWidgetResizable(True)

        # Container for the scroll area content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Add styled labels with the instructions
        instructions = (
            "<style>"
            "ul, ol { margin-bottom: 15px; }"  # Adds spacing after entire lists
            "li { margin-bottom: 10px; }"  # Adds spacing between individual list items
            "</style>"
            "<h3>Overview</h3>"
            "<p>Go is a strategy game for two players where the goal is to control more territory on the board than your opponent.</p>"
            "<h3>The Board</h3>"
            "<ul>"
            "<li>Played on a 7x7 grid.</li>"
            "<li>Stones are placed at intersections.</li>"
            "</ul>"
            "<h3>The Stones</h3>"
            "<ul>"
            "<li>Two types: black and white.</li>"
            "<li>Black always plays first.</li>"
            "<li>Players take turns placing stones on empty intersections.</li>"
            "</ul>"
            "<h3>Gameplay Basics</h3>"
            "<ol>"
            "<li><b>Placing Stones:</b> Stones cannot move but can be captured if surrounded.</li>"
            "<li><b>Liberties:</b> Empty spaces adjacent to a stone are its liberties. Losing all liberties means capture.</li>"
            "<li><b>Groups:</b> Connected stones of the same color share liberties.</li>"
            "<li><b>Capturing Stones:</b> Surround an opponent’s stones to capture them.</li>"
            "</ol>"
            "<h3>The Goal</h3>"
            "<p>Control empty spaces and capture stones to gain points.</p>"
            "<h3>Scoring</h3>"
            "<ul>"
            "<li><b>Territory:</b> Count of spaces surrounded by your stones.</li>"
            "<li><b>Captured Stones:</b> Count of opponent stones you captured.</li>"
            "<li><b>White Bonus:</b> White gets 7.5 points for playing second.</li>"
            "</ul>"
            "<h3>Special Rules</h3>"
            "<ol>"
            "<li><b>Ko Rule:</b> Prevents repeating the same board position in consecutive moves.</li>"
            "<li><b>Suicide Rule:</b> You cannot place a stone with no liberties unless it captures opponent stones.</li>"
            "</ol>"
            "<p><i>Tip:</i> Watch a YouTube tutorial for visual examples!</p>"
        )

        # Add the instructions to a QLabel with rich text formatting
        label = QLabel(instructions, content_widget)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 14px; font-family: Arial;")
        content_layout.addWidget(label)

        # Set the scroll area's widget
        scroll_area.setWidget(content_widget)

        # Add the scroll area to the dialog's layout
        layout.addWidget(scroll_area)

        # Add a close button
        close_button = QPushButton("Close", dialog)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3B4B57; 
                color: white; 
                padding: 10px 20px; 
                font-size: 14px; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4C5D6B;
            }
        """)
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()

    # Method to display Go tips in a QDialog with a scrollable area
    def show_tips(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Go Tips & Tricks")
        dialog.setFixedSize(600, 500)

        # The main layout for the dialog
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)

        # Scroll area to hold the content
        scroll_area = QScrollArea(dialog)
        scroll_area.setWidgetResizable(True)

        # Container for the scroll area content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Tips content
        tips = (
            "<style>"
            "ul { margin-bottom: 15px; }"  # Adds spacing after entire lists
            "li { margin-bottom: 10px; }"  # Adds spacing between individual list items
            "</style>"
            "<h3>Go Tips & Tricks</h3>"
            "<ul>"
            "<li><b>Focus on Corners:</b> Start your moves in the corners as they are easier to defend.</li>"
            "<li><b>Build Strong Groups:</b> Always aim to connect your stones to avoid isolation.</li>"
            "<li><b>Avoid Overextension:</b> Don't place stones too far apart. Keep your groups compact.</li>"
            "<li><b>Use the 'Atari' Move:</b> An 'atari' threatens to capture an opponent's stone. Use it strategically.</li>"
            "<li><b>Control the Center:</b> Securing central territory can be a game-changer in the long run.</li>"
            "<li><b>Know When to Pass:</b> Pass when there are no beneficial moves left. It could end the game when both players pass.</li>"
            "<li><b>Use Ko Rule to Your Advantage:</b> Use Ko rule strategically to force a cycle and gain an advantage.</li>"
            "</ul>"
        )

        # Add the tips to a QLabel with rich text formatting
        label = QLabel(tips, content_widget)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 14px; font-family: Arial;")
        content_layout.addWidget(label)

        # Set the scroll area's widget
        scroll_area.setWidget(content_widget)

        # Add the scroll area to the dialog's layout
        layout.addWidget(scroll_area)

        # Add a close button
        close_button = QPushButton("Close", dialog)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3B4B57; 
                color: white; 
                padding: 10px 20px; 
                font-size: 14px; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4C5D6B;
            }
        """)
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()
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
        self.control_panel.setFixedSize(400,500)
        self.board.control_panel = self.control_panel
        control_dock.setWidget(self.control_panel)

        # Add the dock widget to the right side of the main window
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, control_dock)
        self.show()

