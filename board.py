import math
from PyQt6.QtWidgets import QFrame, QGridLayout,QPushButton,QSizePolicy
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint,QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap,QIcon

from game_logic import GameLogic, GameControlPanel


class Tile(QPushButton):
    '''represents a Tile on the board, upon which a piece can be placed'''

    def __init__(self, text=None, row=None,col=None, parent=None):
        super().__init__(text, parent)
        self.row=row
        self.col=col
        self.board=parent
        self.gridUrl = './assets/grid/Grid Normal.png'

        # assign a grid texture to each Tile depending on its position in the grid

        #left edge
        if self.col == 0:
            if self.row == 0:
                self.gridUrl = './assets/grid/Grid Top Left Corner.png'
            else:
                 self.gridUrl = './assets/grid/Grid Left Edge.png'
        
        #top edge
        elif self.row == 0:
            self.gridUrl = './assets/grid/Grid Top Edge.png'
        
        #right edge
        if self.col == self.board.boardWidth-1:
            if self.row == self.board.boardHeight-1:
                self.gridUrl = './assets/grid/Grid Bottom Right Corner.png'
            elif self.row == 0:
                self.gridUrl = './assets/grid/Grid Top Right Corner.png'
            else:
                self.gridUrl = './assets/grid/Grid Right Edge.png'

        #bottom edge
        elif self.row == self.board.boardHeight-1:
            if self.col == 0:
                self.gridUrl = './assets/grid/Grid Bottom Left Corner.png'
            else:
                self.gridUrl = './assets/grid/Grid Bottom Edge.png'
    
        # stylesheet
        self.style = """
        QPushButton {
            border: none;  /* remove border */
            background-color: #eec58a; 

            /* grid texture */
            background-image: url(%s);  /* path to the texture */
            background-repeat: no-repeat; 
            background-position: center; 
        }
        QPushButton:hover {
            background-color:rgb(230, 183, 116);  
        }
        QPushButton:pressed {
            background-color:rgb(230, 183, 116);  
        }
        """ % (self.gridUrl)
        self.setStyleSheet(self.style)

class Board(QFrame): 
    '''the game board, which consists of a grid of Tile objects'''

    # SIGNALS
    updateTimerSignal = pyqtSignal(int)  # signal sent when the timer is updated
    clickLocationSignal = pyqtSignal(str)  # signal sent when there is a new click location

    # BOARD PARAMETERS
    boardWidth = 7  
    boardHeight = 7

    # Tile AND PIECE PARAMETERS
    pieceSizeFactor=0.9 # the ratio of the size of the piece to the Tile
    

    def __init__(self, parent):
        super().__init__(parent)

        #calculate the initial Tile size 
        self.tile_size = self.getTileSize()

        # the board state is a 2D array with a width of boardWidth and height of boardHeight, initially filled with 0s
        # 0 - unoccupied
        # 1 - occupied by white
        # 2 - occupied by black
        self.boardState = [[0 for col in range(self.boardWidth) ] for row in range(self.boardHeight)]
        self.printBoardState() 

        # 1 for white, 2 for black
        self.currentPlayer=2

        #icons for the pieces
        self.blackPiece = QPixmap("./assets/black_piece.png")
        self.whitePiece = QPixmap("./assets/white_piece.png")
        

        #initialise a grid layout as a physical representation of the board state
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        
        #a 2D array containing all the tiles on the board
        self.tiles = []

        for row in range(self.boardHeight):
            tile_row=[]
            for col in range(self.boardWidth):
                #initialise Tile object, passing the current row and column, as well as the board as parameters
                tile_button = Tile(row=row,col=col,parent=self)

                #connect the Tile to the placePiece function whenever its clicked
                tile_button.clicked.connect(lambda _, r=row, c=col: self.placePiece(r, c))

                #add tile to grid
                self.grid.addWidget(tile_button,row,col)

                #append tile to tile_row
                tile_row.append(tile_button)

            #append tile_row to tiles
            self.tiles.append(tile_row)
            
        self.setLayout(self.grid)
        self.game_logic = GameLogic(self)

    def getTileSize(self):
        '''gets the Tile size. the Tile size is calculated using the widget's width and height'''
        width = self.width()
        height = self.height()

        # // is floor division, which means that the fractional part of the result is thrown away so that the result is just the integer part
        return min(width, height) // max(self.boardWidth, self.boardHeight)

    def resizeEvent(self, event):
        '''called whenever the window is resized'''
        new_tile_size = self.getTileSize()

        # only change the Tile size if the newly calculated size is different
        if new_tile_size != self.tile_size:
            self.tile_size = new_tile_size
            for row in range(self.boardHeight):
                for col in range(self.boardWidth):
                    self.tiles[row][col].setFixedSize(self.tile_size,self.tile_size)
                    self.tiles[row][col].setIconSize(QSize(int(self.tile_size * self.pieceSizeFactor), int(self.tile_size * self.pieceSizeFactor)))

        super().resizeEvent(event)
        

    def printBoardState(self):
        '''
        prints the current state of the board:
        0 - unoccupied
        1 - occupied by white
        2 - occupied by black 
        '''
        print("board state:")
        print('\n'.join(['\t'.join([str(Tile) for Tile in row]) for row in self.boardState]))


    def togglePlayer(self):
        '''toggles the current player'''
        if self.currentPlayer==1:
            self.currentPlayer=2
        elif self.currentPlayer==2:
            self.currentPlayer=1

        self.control_panel.update_player(self.currentPlayer)
        self.control_panel.handle_turn_change()


    def placePiece(self, row, col):
        '''places a new piece on the board'''
        # Store current state before validating move, needed for ko rule
        self.game_logic.last_board_state = [row[:] for row in self.boardState]
        if self.game_logic.is_valid_move(row, col):
            self.boardState[row][col] = self.currentPlayer
            self.game_logic.handle_captures()
            self.control_panel.update_captures()
            self.control_panel.update_territory()
            self.game_logic.last_move_pass = False # Reset pass flag on regular move

            # Check if board is full after valid move
            if self.game_logic.is_board_full():
                self.game_logic.game_over = True
                self.control_panel.show_gameOve(*self.game_logic.calculate_score())
                return

            self.drawBoard()
            self.togglePlayer()



    def resetGame(self):
        '''sets the entire state to 0, therefore erasing all pieces from the board'''
        self.boardState = [[0 for col in range(self.boardWidth) ] for row in range(self.boardHeight)]

    def drawBoard(self):
        '''checks the board's state and draws pieces where there's a 1 (white) or 2 (black)'''
        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                tile_state = self.boardState[row][col]
                tile_button = self.tiles[row][col]

                if tile_state==1:
                    piece = QIcon(self.whitePiece)
                elif tile_state==2:
                    piece = QIcon(self.blackPiece)
                else:
                    piece=QIcon()

                tile_button.setIcon(piece)
                



