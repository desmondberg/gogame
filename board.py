import math
from PyQt6.QtWidgets import QFrame, QGridLayout,QPushButton,QSizePolicy
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint,QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap,QIcon

class Cell(QPushButton):
    '''represents a cell on the board, upon which a piece can be placed'''
    
    def __init__(self, text, row=None,col=None, parent=None):
        super().__init__(text, parent)
        self.row=row
        self.col=col
        self.board=parent

        self.default_colour = "#e6cd98"
        self.hover_colour= "#dbc086"
        #self.clicked_colour= "#d3b678"

    # events for when the user hovers over a cell
    def enterEvent(self, event):
        # only make the cell darker when hovered on if there isn't a piece on it
        if(self.board.boardState[self.row][self.col]==0):
            self.setStyleSheet(f"background-color: {self.hover_colour}; border: 1px solid black;") 
        super().enterEvent(event) 

    def leaveEvent(self, event):
        self.setStyleSheet(f"background-color: {self.default_colour}; border: 1px solid black;") 
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setStyleSheet(f"background-color: {self.default_colour}; border: 1px solid black;") 
        super().mouseReleaseEvent(event)

class Board(QFrame): 
    '''the game board, which consists of a grid of Cell objects'''

    # SIGNALS
    updateTimerSignal = pyqtSignal(int)  # signal sent when the timer is updated
    clickLocationSignal = pyqtSignal(str)  # signal sent when there is a new click location

    # BOARD PARAMETERS
    boardWidth = 7  
    boardHeight = 7  

    # TIMER PARAMETERS
    timerSpeed = 1000  # the timer updates every 1 second
    counter = 10  # the number the counter will count down from

    # CELL AND PIECE PARAMETERS
    pieceSizeFactor=0.94 # the ratio of the size of the piece to the cell

    def __init__(self, parent):
        super().__init__(parent)

        #calculate the initial cell size 
        self.cell_size = self.getCellSize()

        self.timer = QTimer(self)  # create a timer for the game
        #self.timer.timeout.connect(self.timerEvent)  # connect timeout signal to timerEvent method
        self.isStarted = False  # game is not currently started
        self.start()  # start the game which will start the timer

        # initialise the board's state as a 2D array with width equal to boardWidth and height equal to boardHeight
        # each cell's value will be 0 at the beginning
        self.boardState = [[0 for col in range(self.boardWidth) ] for row in range(self.boardHeight)]
        self.printBoardState() 

        #initialise players, 1=white, 2=black
        self.currentPlayer=1

        #initialise icons for the pieces
        self.blackPiece = QPixmap("./assets/black_piece.png")
        self.whitePiece = QPixmap("./assets/white_piece.png")
        

        # initialise a grid and buttons for each cell, as a physical representation of the board state
        self.grid = QGridLayout()
        self.grid.setSpacing(2)
        self.cells = []
        for row in range(self.boardHeight):
            cell_row=[]
            for col in range(self.boardWidth):
                cell_button = Cell("",row,col,self)

                #placeholder style
                cell_button.setStyleSheet("background-color: #e6cd98; border: 1px solid black;")

                cell_button.clicked.connect(lambda _, r=row, c=col: self.placePiece(r, c))
                self.grid.addWidget(cell_button,row,col)
                cell_row.append(cell_button)
            self.cells.append(cell_row)
            
        self.setLayout(self.grid)

    def getCellSize(self):
        '''gets the cell size. the cell size is calculated using the widget's width and height'''
        width = self.width()
        height = self.height()

        # // is floor division, which means that the fractional part of the result is thrown away so that the result is just the integer part
        return min(width, height) // max(self.boardWidth, self.boardHeight)

    def resizeEvent(self, event):
        '''called whenever the window is resized'''
        new_cell_size = self.getCellSize()

        # only change the cell size if the newly calculated size is different
        if new_cell_size != self.cell_size:
            self.cell_size = new_cell_size
            for row in range(self.boardHeight):
                for col in range(self.boardWidth):
                    self.cells[row][col].setFixedSize(self.cell_size,self.cell_size)
                    self.cells[row][col].setIconSize(QSize(int(self.cell_size * self.pieceSizeFactor), int(self.cell_size * self.pieceSizeFactor)))

        super().resizeEvent(event) 

    

        

    def printBoardState(self):
        '''
        prints the current state of the board:
        0 - unoccupied
        1 - occupied by white
        2 - occupied by black 
        '''
        print("board state:")
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.boardState]))

    def start(self):
        '''starts game'''
        self.isStarted = True  # set the boolean which determines if the game has started to TRUE
        self.resetGame()  # reset the game
        self.timer.start(self.timerSpeed)  # start the timer with the correct speed
        print("start () - timer is started")

    def timerEvent(self):
        '''this event is automatically called when the timer is updated. based on the timerSpeed variable '''
        # TODO adapt this code to handle your timers
        if Board.counter == 0:
            print("Game over")
        self.counter -= 1
        print('timerEvent()', self.counter)
        self.updateTimerSignal.emit(self.counter)

    def togglePlayer(self):
        '''toggles the current player'''
        if self.currentPlayer==1:
            self.currentPlayer=2
        elif self.currentPlayer==2:
            self.currentPlayer=1


    def placePiece(self, row, col):
        '''places a new piece on the board'''

        #check if the cell is empty
        if self.boardState[row][col]==0:
            self.boardState[row][col]=self.currentPlayer

        self.drawBoard()
        self.togglePlayer()




    def movePiece(self, newX, newY):
        '''tries to move a piece'''
        pass  # Implement this method according to your logic


    def resetGame(self):
        '''clears pieces from the board'''
        # TODO write code to reset game

    def drawBoard(self):
        '''checks the board's state and draws pieces where there's a 1 (white) or 2 (black)'''
        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                cell_state = self.boardState[row][col]
                cell_button = self.cells[row][col]

                if cell_state==1:
                    piece = QIcon(self.whitePiece)
                elif cell_state==2:
                    piece = QIcon(self.blackPiece)
                else:
                    piece=QIcon()

                cell_button.setIcon(piece)

        #self.printBoardState()
                
                



