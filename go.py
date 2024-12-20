from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QDockWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from board import Board

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
        self.board = Board(self)
        self.layout  
        self.setCentralWidget(self.board)

        self.setFixedSize(700,700)
        self.setWindowTitle('Go')
        self.show()







