import board
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLCDNumber, QMessageBox)
from PyQt6.QtCore import Qt, QTimer


class GameLogic:
    def __init__(self, board):
        self.board = board  # reference to the Board class instance
        self.board_size = board.boardWidth
        # tracking captured stones for each player (1 for white, 2 for black)
        self.captured_stones = {1: 0, 2: 0}
        self.last_move_pass = False  # to track 2 consecutive passes
        self.game_over = True
        self.last_board_state = None  # For ko rule checking

    # Count liberties (empty adjacent spaces) for a stone/group at row,col
    def get_group_liberties(self, row, col):
        color = self.board.boardState[row][col]
        if color == 0:  # Empty space has no liberties
            return 0

        # using set to ensure no duplicate (row,col)
        visited = set()  # stones we've checked
        liberties = set()  # empty spaces next to group
        stack = [(row, col)]  # Starting with initial stone

        # Find all connected stones and their liberties
        while stack:  # while stack is not empy
            row, col = stack.pop()  # remove last row,col each iteration
            if (row, col) not in visited:
                visited.add((row, col))

                # Check all four adjacent positions
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # up, down, left, right
                    new_row, new_col = row + dr, col + dc
                    # If position is on board, (so we don't go outside the bord when checking)
                    if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
                        if self.board.boardState[new_row][new_col] == 0:  # Empty = liberty
                            liberties.add((new_row, new_col))
                        # If same color stone and not visited, add to stack
                        elif (self.board.boardState[new_row][new_col] == color and
                              (new_row, new_col) not in visited):
                            stack.append((new_row, new_col))

        return len(liberties)

    # Get all connected stones of the same color starting from row,col
    def get_group(self, row, col):

        color = self.board.boardState[row][col]
        if color == 0:  # Empty space has no group
            return set()

        visited = set()  # tracking visited stones
        stack = [(row, col)]  # Start with initial stone

        # Find all connected stones of same color
        while stack:
            row, col = stack.pop()
            if (row, col) not in visited:
                visited.add((row, col))
                # Check adjacent positions
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # up, down, left, right
                    new_row, new_col = row + dr, col + dc
                    # If position is on board, adjacent, and same color
                    if (0 <= new_row < self.board_size and
                            0 <= new_col < self.board_size and
                            self.board.boardState[new_row][new_col] == color and
                            (new_row, new_col) not in visited):
                        stack.append((new_row, new_col))
        return visited  # return all visited (Stones belonging to same group)

    # Find all opponent groups that have no liberties (are captured)
    def find_captured_groups(self):

        captured = []
        opponent = 1 if self.board.currentPlayer == 2 else 2

        for row in range(self.board_size):
            for col in range(self.board_size):
                # If we find opponent's stone
                if self.board.boardState[row][col] == opponent:
                    # Check if this stone/group has no liberties
                    if self.get_group_liberties(row, col) == 0:
                        group = self.get_group(row, col)
                        if group not in captured:
                            captured.append(group)
        return captured

    # Check if placing a stone at row,col is valid according to Go rules
    def is_valid_move(self, row, col):
        """ Checks:
        Position is on board
        Position is empty
        Move doesn't break ko rule
        Also don't break suicide rule """
        # Basic checks
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):  # within board
            return False
        if self.board.boardState[row][col] != 0:  # if position is not empty
            return False
        if self.game_over:
            return False

        # Store current board state before trying move
        previous_state = [row[:] for row in self.board.boardState]

        # Try move temporarily to see if it breaks rule
        self.board.boardState[row][col] = self.board.currentPlayer

        # Suicide rule, must either capture or create liberty otherwise its suicide
        # Check if move captures any opponent groups
        captured_groups = self.find_captured_groups()
        # Check if move creates a group with liberties
        has_liberties = self.get_group_liberties(row, col) > 0

        # checking for ko rule violation
        # Ko rule: Cannot recreate the board position from the previous move
        ko = False
        if self.last_board_state is not None:  # it's not first move in game
            # Compare current board state with the last board state
            current_matches_last = True
            for i in range(self.board_size):  # loop through all row, col
                for j in range(self.board_size):
                    if self.board.boardState[i][j] != self.last_board_state[i][j]:
                        current_matches_last = False  # if any current don't match prev, return false
                        break
                if not current_matches_last:  # break, since its false
                    break
            ko = current_matches_last  # save the boolean

        # Restore the original board state
        self.board.boardState = previous_state

        # returns true if:
        # The placed stone/group has liberties or captures something, AND
        # It doesn't violate the suicide + ko rule
        return (has_liberties or captured_groups) and not ko  # follows go rules, true or false

    # if board is full, terminate game
    def is_board_full(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board.boardState[row][col] == 0:
                    return False  # if we find an empty space, return false, meaning board not full
        return True  # else return true

    # Remove captured stones from board and update capture count for player
    def handle_captures(self):

        captured = self.find_captured_groups()  # get amount of captures
        for group in captured:
            # Add to current player's capture count
            self.captured_stones[self.board.currentPlayer] += len(group)
            # Remove captured stones from board, since captured
            for row, col in group:
                self.board.boardState[row][col] = 0

    # Handle when a player passes their turn, 2 passes = end game
    def handle_pass(self):
        if self.last_move_pass:  # prev player passed, and current player passed, end game
            self.game_over = True
            self.calculate_score()  # Calculate final score
            self.board.control_panel.show_gameOver(*self.calculate_score())
        else:
            # First pass, set flag and continue game
            self.last_move_pass = True

        if not self.game_over:
            self.board.togglePlayer()  # Switch to next player



    # Method to determine and count if an area of empty spaces is territory for a player.
    def count_territory(self, row, col):
        if self.board.boardState[row][col] != 0:  # If not empty space
            return 0, 0
        if sum(row.count(0) for row in self.board.boardState) >= (self.board_size * self.board_size - 1):
            return 0, 0  # Return no territory if only one stone on board

        empty_spaces = set()  # Track connected empty spaces
        surrounding_colors = set()  # Colors of stones surrounding the empty area
        stack = [(row, col)]

        # Find all connected empty spaces and their surrounding stones
        while stack:
            curr_row, curr_col = stack.pop()
            if (curr_row, curr_col) not in empty_spaces:
                empty_spaces.add((curr_row, curr_col))

                # Check all four adjacent positions
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_row, new_col = curr_row + dr, curr_col + dc

                    # Skip if outside board
                    if not (0 <= new_row < self.board_size and 0 <= new_col < self.board_size):
                        continue

                    stone = self.board.boardState[new_row][new_col]
                    if stone == 0:  # Empty space
                        if (new_row, new_col) not in empty_spaces:
                            stack.append((new_row, new_col))
                    else:  # Stone found
                        surrounding_colors.add(stone)

        # If area is surrounded by exactly one color, it's territory for that color
        if len(surrounding_colors) == 1:
            owner = surrounding_colors.pop()
            return len(empty_spaces), owner

        return 0, 0  # Else not territory (neutral)

    # Method to calculate final game score for both players.
    def calculate_score(self):
        territory = {1: 0, 2: 0}  # Territory count for each player
        counted = set()  # Already counted empty spaces

        # Count territory
        for row in range(self.board_size):
            for col in range(self.board_size):
                if (row, col) not in counted and self.board.boardState[row][col] == 0:
                    territory_points, owner = self.count_territory(row, col)
                    if owner > 0:  # If territory belongs to a player
                        territory[owner] += territory_points
                        # Mark these spaces as counted
                        empty_group = self.get_empty_group(row, col)
                        counted.update(empty_group)

        # Calculate final scores
        white_score = territory[1] + self.captured_stones[1] + 7.5  # Add komi
        black_score = territory[2] + self.captured_stones[2]

        return black_score, white_score

    # Method to get all connected empty spaces starting from a position
    def get_empty_group(self, row, col):
        if self.board.boardState[row][col] != 0:  # If it's not empty return empty set
            return set()

        visited = set()
        stack = [(row, col)]

        # Continue while we have positions to check
        while stack:
            curr_row, curr_col = stack.pop()
            if (curr_row, curr_col) not in visited:
                visited.add((curr_row, curr_col)) # Mark current position as visited

                # Check adjacent positions
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_row, new_col = curr_row + dr, curr_col + dc
                    # Add position to stack if it's within board, is empty, not visited
                    if (0 <= new_row < self.board_size and
                            0 <= new_col < self.board_size and
                            self.board.boardState[new_row][new_col] == 0 and
                            (new_row, new_col) not in visited):
                        stack.append((new_row, new_col))

        return visited # Return all connected empty spaces found


# This class will be responsible for the UI elements, game control elements
class GameControlPanel(QWidget):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.player_timers = {1: 120, 2: 120}
        self.current_timer = QTimer()
        self.current_timer.timeout.connect(self.update_timer)
        self.initUI()

    def initUI(self):

        # Setting some styles variables
        lcd_style = """
            QLCDNumber {
                border: 1px solid gray;
                border-radius: 5px;
                background-color: black;
                padding: 2px;
            }
        """

        start_style = """
        QPushButton {
            background-color: #4CAF50; /* Green color */
            color: white; 
            font-size: 15px;
            letter-spacing: 1px;
            padding: 10px;
            border-radius: 10px;
            border: 1px solid #3E8E41; /* border for contrast */
        }

        QPushButton:hover {
            background-color: #45A049;
        }
        QPushButton:disabled {
            background-color: #BDBDBD; /* Gray color when disabled */
            color: #808080;
            border: 0.5px solid #9E9E9E;
        }
        """

        pass_style = """
        QPushButton {
            background-color: #2196F3; /* blue color */
            color: white; 
            width: 150px;
            font-size: 12px;
            letter-spacing: 1px;
            padding: 8px;
            border-radius: 10px;
            border: 0.5px solid #1976D2; /* border for contrast */
        }

        QPushButton:hover {
            background-color: #1E88E5;
        }
        QPushButton:disabled {
            background-color: #BDBDBD; /* Gray color when disabled */
            color: #808080;
            border: 1px solid #9E9E9E;
        }
        """
        score_label_style = """
            QLabel {
                font-size: 15px;
                
                letter-spacing: 0.5px;
            }
        """

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Start button
        self.start_button = QPushButton('Start Game')
        self.start_button.clicked.connect(self.start_game)
        self.start_button.setStyleSheet(start_style)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.start_button)

        # Current player display and pass button elements
        player_control = QHBoxLayout()
        self.player_label = QLabel('Current Player: ')
        self.player_label.setStyleSheet("color:white; font-weight: 500; letter-spacing: 0.5px; font-size: 15px")
        self.current_player_layout = QVBoxLayout()
        self.current_player = QLabel('')
        self.current_player_label = QLabel('')
        self.pass_button = QPushButton('Pass Turn')
        self.pass_button.clicked.connect(self.board.game_logic.handle_pass)
        self.pass_button.setStyleSheet(pass_style)
        self.pass_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pass_button.setEnabled(False)  # Initially disabled

        # current player indicator
        self.current_player_layout.addWidget(self.current_player)
        self.current_player_layout.addWidget(self.current_player_label)
        self.current_player_widget = QWidget()
        self.current_player_widget.setLayout(self.current_player_layout)

        player_control.addWidget(self.player_label,alignment=Qt.AlignmentFlag.AlignCenter)
        player_control.addWidget(self.current_player_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        player_control.addStretch(1)
        player_control.addWidget(self.pass_button)

        layout.addLayout(player_control)

        # Timer display setup
        timer_layout = QHBoxLayout()
        self.timer_display = QLCDNumber()
        self.timer_display.setDigitCount(4)  # will be mm:ss so 4 digits
        self.timer_display.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.timer_display.setStyleSheet("""
            QLCDNumber {
                border: 2px solid #2C3E50;
                border-radius: 5px;
                background-color: #34495E;
                color: #ECF0F1;
                padding: 5px;
                min-width: 100px;
            }
        """)
        self.timer_display.setFixedSize(120, 60)
        # Timer label UI
        timer_label = QLabel('Time Remaining:')
        timer_label.setStyleSheet("font-size: 15px; font-weight: 500; letter-spacing: 0.5px;")
        timer_layout.addWidget(timer_label)
        timer_layout.addWidget(self.timer_display)
        layout.addLayout(timer_layout)  # Below current player but above captures
        layout.addSpacing(30)

        # Score display elements
        score_layout = QHBoxLayout()
        # Black score lcd
        self.black_captures = QLCDNumber()
        self.black_captures.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.black_captures.setFixedSize(60, 60)  # Set fixed size for the LCD
        self.black_captures.setDigitCount(2)  # Set to 2 since captures not exceeding 99
        self.black_captures.setStyleSheet(lcd_style)
        # White score lcd
        self.white_captures = QLCDNumber()
        self.white_captures.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.white_captures.setFixedSize(60, 60)  # Set fixed size for the LCD
        self.white_captures.setDigitCount(2)  # Set to 2 since captures not exceeding 99
        self.white_captures.setStyleSheet(lcd_style)

        # Labels for black and white captures
        black_score_label = QLabel('Black Prisoners:')
        black_score_label.setStyleSheet(score_label_style)
        score_layout.addWidget(black_score_label)
        score_layout.addWidget(self.black_captures)

        white_score_label = QLabel('White Prisoners:')
        white_score_label.setStyleSheet(score_label_style)
        score_layout.addWidget(white_score_label)
        score_layout.addWidget(self.white_captures)

        # Territory row
        territory_layout = QHBoxLayout()

        # Black territory lcd
        self.black_territory = QLCDNumber()
        self.black_territory.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.black_territory.setFixedSize(60, 60)
        self.black_territory.setDigitCount(2)
        self.black_territory.setStyleSheet(lcd_style)

        # White territory lcd
        self.white_territory = QLCDNumber()
        self.white_territory.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.white_territory.setFixedSize(60, 60)
        self.white_territory.setDigitCount(2)
        self.white_territory.setStyleSheet(lcd_style)

        black_territory_label = QLabel('Black Territory:')
        black_territory_label.setStyleSheet(score_label_style)
        territory_layout.addWidget(black_territory_label)
        territory_layout.addWidget(self.black_territory)

        white_territory_label = QLabel('White Territory:')
        white_territory_label.setStyleSheet(score_label_style)
        territory_layout.addWidget(white_territory_label)
        territory_layout.addWidget(self.white_territory)

        layout.addLayout(score_layout)
        layout.addLayout(territory_layout)
        self.setLayout(layout)

    # Method to run when pressing start button
    def start_game(self):
        self.board.resetGame()
        self.board.game_logic.game_over = False
        self.board.currentPlayer = 2
        self.update_player(player=2)
        self.start_button.setEnabled(False)
        self.pass_button.setEnabled(True)
        self.player_timers = {1: 120, 2: 120}
        self.current_timer.start(1000)
        self.update_timer_display()

    # Method to update current player element
    def update_player(self, player):
        # Update the current player label to player's color, using circles
        color = "white" if player == 1 else "black"

        size = 40  # Diameter of the circle
        self.current_player.setFixedSize(size, size)
        self.current_player.setStyleSheet(f"background-color: {color}; border-radius: {size // 2}px;")
        self.current_player_label.setText(color.capitalize())

    # Method to update captures shown in lcd (prisoners)
    def update_captures(self):
        self.black_captures.display(self.board.game_logic.captured_stones[2])
        self.white_captures.display(self.board.game_logic.captured_stones[1])

    # Method to update territory shown in lcd
    def update_territory(self):
        # Territory counts from game logic's calculate_score method
        territory = self.board.game_logic.calculate_score()
        # Subtract captures and komi to get just territory
        black_territory = territory[0] - self.board.game_logic.captured_stones[2]
        white_territory = territory[1] - self.board.game_logic.captured_stones[1] - 7.5

        self.black_territory.display(black_territory)
        self.white_territory.display(white_territory)

    def show_gameOver(self, black_score, white_score):
        winner = "Black" if black_score > white_score else "White"
        self.current_timer.stop()  # Stop the time since game is over
        self.timer_display.display(0)
        self.white_territory.display(0)
        self.black_territory.display(0)
        msg = QMessageBox()
        msg.setWindowTitle("Game Over")
        msg.setText(f"Game Over!\n\nBlack Score: {black_score}\nWhite Score: {white_score}\n\nWinner: {winner}")
        response = msg.exec()

        if response == QMessageBox.StandardButton.Ok:  # OK button clicked
            # Resetting everything
            self.board.resetGame()
            self.board.game_logic.game_over = True
            self.board.game_logic.last_move_pass = False
            self.board.game_logic.last_board_state = None
            self.board.game_logic.captured_stones = {1: 0, 2: 0}
            self.start_button.setEnabled(True)
            self.pass_button.setEnabled(False)
            self.black_captures.display(0)
            self.white_captures.display(0)
            self.current_player.setStyleSheet("")

            # Redraw board
            self.board.drawBoard()

    # Handles timer reset when turn changes
    def handle_turn_change(self):
        current_player = self.board.currentPlayer
        self.player_timers[current_player] = 120  # Reset to 2 minutes
        self.update_timer_display()

    def update_timer(self):
        current_player = self.board.currentPlayer
        self.player_timers[current_player] -= 1  # Seconds will decrease by 1

        if self.player_timers[current_player] <= 0:  # If time is out, stop and determine winner
            self.current_timer.stop()
            self.handle_game_over(f"{'Black' if current_player == 1 else 'White'} wins by Timeout!")
        else:
            self.update_timer_display()  # Else just call display time function

    def update_timer_display(self):
        time = self.player_timers[self.board.currentPlayer]  # Current decreased time
        self.timer_display.display(f"{time // 60:02d}:{time % 60:02d}")  # Format time MM:SS

    def handle_game_over(self, message):  # This game over is for when time runs out
        self.timer_display.display(0)
        self.white_territory.display(0)
        self.black_territory.display(0)
        msg = QMessageBox()
        msg.setWindowTitle("Game Over - Time is out!")
        msg.setText(message)
        response = msg.exec()

        if response == QMessageBox.StandardButton.Ok:  # OK button clicked
            # Reset everything
            self.board.resetGame()
            self.board.game_logic.game_over = True
            self.start_button.setEnabled(True)
            self.pass_button.setEnabled(False)
            self.black_captures.display(0)
            self.white_captures.display(0)
            self.current_player.setStyleSheet("")
            self.board.drawBoard()
