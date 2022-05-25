"""
The Game state engine is the backbone of the entire program which controls all board functions such as
initializing the pieces onto the board, making moves, undoing moves, calculating all legal moves, and keeping track of
end game conditions
"""

from Pieces import Pawn
from Pieces import Rook
from Pieces import Knight
from Pieces import King
from Pieces import Bishop
from Pieces import Queen
from Pieces import Pieces
from CastleRights import CastleRights


class GameState:
    """
    Initializes the board with all the pieces in their starting positions for both black and white. Also sets all flags
    for ending conditions to false, initializes the move log, keeps track of king's positions, keeps track of
    enpassant and castling, and for checks and pieces that are pinned.
    """

    def __init__(self) -> None:
        # Board looks like the following (rows x cols):
        # xx 00 01 02 03 04 05 06 07
        # 00 bR bN bB bQ bK bB bK bR
        # 10 bP bP bP bP bP bP bP bP
        # 20 -- -- -- -- -- -- -- --
        # 30 -- -- -- -- -- -- -- --
        # 40 -- -- -- -- -- -- -- --
        # 50 -- -- -- -- -- -- -- --
        # 60 wP wP wP wP wP wP wP wP
        # 70 wR wN wB wQ wK wB wK wR

        # Creates a 2d list that represents the board
        self.board = [[Pieces(r, c, "-") for r in range(8)] for c in range(8)]

        # Creates black and white pawns in rows 1 and 6
        for i in range(8):
            self.board[1][i] = Pawn(1, i, 'b')
            self.board[6][i] = Pawn(6, i, 'w')

        # Black pieces in row 0
        self.board[0][0] = Rook(0, 0, 'b')
        self.board[0][1] = Knight(0, 1, 'b')
        self.board[0][2] = Bishop(0, 2, 'b', "Light")
        self.board[0][3] = Queen(0, 3, 'b')
        self.board[0][4] = King(0, 4, 'b')
        self.board[0][5] = Bishop(0, 5, 'b', "Dark")
        self.board[0][6] = Knight(0, 6, 'b')
        self.board[0][7] = Rook(0, 7, 'b')

        # white pieces in row 7
        self.board[7][0] = Rook(7, 0, 'w')
        self.board[7][1] = Knight(7, 1, 'w')
        self.board[7][2] = Bishop(7, 2, 'w', "Dark")
        self.board[7][3] = Queen(7, 3, 'w')
        self.board[7][4] = King(7, 4, 'w')
        self.board[7][5] = Bishop(7, 5, 'w', "Light")
        self.board[7][6] = Knight(7, 6, 'w')
        self.board[7][7] = Rook(7, 7, 'w')

        # Move log
        self.move_log = []

        # player turn counter
        # 1 = White
        # 0 = black
        self.white_turn = True

        # King locations
        self.black_king_loc = (0, 4)
        self.white_king_loc = (7, 4)

        # Checking variables
        self.in_check = False
        self.pins = []
        self.checks = []

        # These might not be used
        self.stalemate = False
        self.checkmate = False
        self.draw = False

        # enpassant
        self.enpassant_square = ()
        self.enpassant_possible_log = [self.enpassant_square]

        # Castling
        self.current_castle_rights = CastleRights(True, True, True, True)
        self.castle_logs = [CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks,
                                         self.current_castle_rights.wqs, self.current_castle_rights.bqs)]

        # Controls game mode
        self.game_mode = "HVH"

    """
    Function that moves the piece from its starting square to the ending square. The move is then saved into the move 
    log so that it can later be undone if the player chooses to. Also saves information to determine if the move 
    was castling, pawn promotion, or en-passant.
    """

    def make_move(self, move, human_turn) -> None:
        # Sets starting position to empty piece because the moving piece will no longer be at that location
        self.board[move.start_row][move.start_col] = Pieces(move.start_row, move.start_col, "-")

        # Sets ending location to the piece that was located at the starting position
        self.board[move.end_row][move.end_col] = move.piece_moved

        # Appends the move into the move log
        self.move_log.append(move)

        # Changes player turn
        self.white_turn = not self.white_turn

        # Updates king positions if they've moved
        if move.piece_moved.piece_color_type == "bK":
            self.black_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved.piece_color_type == "wK":
            self.white_king_loc = (move.end_row, move.end_col)

        # Pawn promotion
        if move.is_pawn_promotion:
            # Humans choose which pawn promotion they'd like
            if human_turn:
                while True:
                    try:
                        piece_promotion = input("Pawn Promotion. Which piece would you like: Q, N, R?").upper()
                        if piece_promotion == 'Q' or piece_promotion == 'B' or \
                                piece_promotion == 'N' or piece_promotion == 'R':
                            break
                        else:
                            raise ValueError
                    except ValueError:
                        print("Invalid input. Try again.")

                # Replaces the pawn into either Q, B, R, or N once it has reach the enemies back row
                match piece_promotion:
                    case 'Q':
                        self.board[move.end_row][move.end_col] = Queen(move.end_row, move.end_col,
                                                                       move.piece_moved.team)
                    case 'B':
                        if self.white_turn:
                            if (move.end_row == 0 and move.end_col == 0) or ((move.end_row + move.end_col) % 2 == 0):
                                bishop_square_color = "Light"
                            else:
                                bishop_square_color = "Dark"
                        else:
                            if (move.end_row == 7 and move.end_col == 0) or ((move.end_row + move.end_col) % 2 == 1):
                                bishop_square_color = "Dark"
                            else:
                                bishop_square_color = "Light"

                        self.board[move.end_row][move.end_col] = Bishop(move.end_row, move.end_col,
                                                                        move.piece_moved.team, bishop_square_color)
                    case 'R':
                        self.board[move.end_row][move.end_col] = Rook(move.end_row, move.end_col, move.piece_moved.team)
                    case 'N':
                        self.board[move.end_row][move.end_col] = Knight(move.end_row, move.end_col,
                                                                        move.piece_moved.team)
            else:  # AI's automatically choose Queen as their pawn promotion
                self.board[move.end_row][move.end_col] = Queen(move.end_row, move.end_col, move.piece_moved.team)

        # Enpassant
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = Pieces(move.start_row, move.end_col, "-")

        if move.piece_moved.piece_type == 'P' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_square = (((move.end_row + move.start_row) // 2), move.end_col)
        else:
            self.enpassant_square = ()

        self.enpassant_possible_log.append(self.enpassant_square)

        # Castling
        self.update_castle_rights(move)

        # Moving rooks for castling
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king
                if 0 <= move.end_col - 1 < 8 and 0 <= move.end_col + 1 < 8:
                    self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = Pieces(move.end_row, move.end_col + 1, "-")
            else:  # Queen
                if 0 <= move.end_col + 1 < 8 and 0 <= move.end_col - 2 < 8:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                    self.board[move.end_row][move.end_col - 2] = Pieces(move.end_row, move.end_col - 2, "-")

    """
    Updates the castling rights to signify if castling is possible for queen or king side
    """

    def update_castle_rights(self, move) -> None:

        # If either w/b king has moved
        if move.piece_captured.piece_color_type == 'wK':
            self.current_castle_rights.wks = False
            self.current_castle_rights.wqs = False

        elif move.piece_captured.piece_color_type == 'bK':
            self.current_castle_rights.bks = False
            self.current_castle_rights.bqs = False

        # If either w/b rook has moved
        elif move.piece_captured.piece_color_type == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castle_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castle_rights.wks = False

            # Checks to see if a white rook was captured, unable to castle
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castle_rights.wqs = False
                elif move.end_col == 7:
                    self.current_castle_rights.wks = False

        elif move.piece_captured.piece_color_type == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castle_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castle_rights.bks = False

            # Checks to see if at white rook was captured, unable to castle
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castle_rights.bqs = False
                elif move.end_col == 7:
                    self.current_castle_rights.bks = False

        # Update the castle log to keep track of castling
        self.castle_logs.append(CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks,
                                             self.current_castle_rights.wqs, self.current_castle_rights.bqs))

    """
    Function that undoes moves made on the board. 
    """

    def undo_move(self) -> None:
        if len(self.move_log) == 0:
            print('Can not UNDO at the start of the game')
            return

        # Removes last move from move log to get the information about the move (i.e. piece moved and piece captured)
        move = self.move_log.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.white_turn = not self.white_turn

        # Update Kings location to previous location
        if move.piece_moved.piece_color_type == "bK":
            self.black_king_loc = (move.start_row, move.start_col)
        elif move.piece_moved.piece_color_type == "wK":
            self.white_king_loc = (move.start_row, move.start_col)

        # Update enpassant to previous configuration
        if move.is_enpassant_move:
            self.board[move.end_row][move.end_col] = Pieces(move.start_row, move.start_col, "-")
            self.board[move.start_row][move.end_col] = move.piece_captured

        self.enpassant_possible_log.pop()
        self.enpassant_square = self.enpassant_possible_log[-1]

        # Undo castling
        self.castle_logs.pop()
        self.current_castle_rights = self.castle_logs[-1]

        # Undo Moving rooks for castling
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king
                if (0 <= move.end_col + 1 < 8) and (0 <= move.end_col - 1 < 8):
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = Pieces(move.end_row, move.end_col - 1, "-")
            elif (0 <= move.end_col - 2 < 8) and (0 <= move.end_col + 1 < 8):  # Queen
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = Pieces(move.end_row, move.end_col + 1, "-")

        # Undo checkmate/stalemate
        self.checkmate = False
        self.stalemate = False

    """
    Calculates all legal and valid moves on the board while considering if the king is in check
    """

    def get_valid_moves(self) -> list:

        # List of all moves that are possible, even when the king is in check
        moves = []

        # Calculates if the king is in check, the piece that are pinned and protecting the king, and checks
        self.in_check, self.pins, self.checks = self.check_for_pins_checks(self.white_king_loc, self.black_king_loc)

        if self.white_turn:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]

        if self.in_check:
            # If the king is in check from one piece, the king is able to move, other pieces can block the
            # attacking piece, other pieces can capture the attacking piece if possible
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()

                # Check information: the direction and square the enemy piece is attacking from
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]

                # Get information from attacking piece
                piece_checking = self.board[check_row][check_col]

                # List of all valid squares from the king toward the attacking piece. Pieces can block the check by 
                # positioning onto any of these squares.
                valid_squares = []

                # If the attacking piece is a knight, the valid move would be to move the king or capture the knight
                if piece_checking.piece_type == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    # Generates all valid square from the king toward the direction the attacking piece is positioned
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break

                # Removes all moves that wouldn't position a piece onto the valid square that would block the attack
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved.piece_type != 'K':
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            # If the king is being attacked by multiple pieces, the king must move, no 1 piece can block all attacks
            else:
                self.board[king_row][king_col].get_piece_move(king_row, king_col, moves, self.board,
                                                              self.check_for_pins_checks, self.white_king_loc,
                                                              self.black_king_loc, self.current_castle_rights,
                                                              self.square_under_attack)
        else:
            # if not in check, all possible moves are each piece can make is valid
            moves = self.get_all_possible_moves()

        # Verifies checkmate or stalemate
        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        # Checks for draws
        self.check_for_draw()

        return moves

    """
    Calculates checks, pins, and if the king is currently in check by using a radial algorithm to detect if there is 
    an attacking piece from any of the 8 directions. 
    """

    def check_for_pins_checks(self, white_king_loc, black_king_loc):
        pins = []
        checks = []
        in_check = False

        if self.white_turn:
            enemy_team = 'b'
            ally = 'w'
            start_row = white_king_loc[0]  # starting position for wk is 7
            start_col = white_king_loc[1]  # starting position for wk is 4

        else:
            enemy_team = 'w'
            ally = 'b'
            start_row = black_king_loc[0]  # starting position for bk is 0
            start_col = black_king_loc[1]  # starting position for bk is 4

        # Values that represent the 8 directions on the board
        directions = (
            (-1, 0),  # 0 Up
            (0, -1),  # 1 Left
            (1, 0),  # 2 Down
            (0, 1),  # 3 Right
            (-1, -1),  # 4 Top left diagonal
            (-1, 1),  # 5 Top right diagonal
            (1, -1),  # 6  Bottom left diagonal
            (1, 1),  # 7 Bottom right diagonal
        )

        # Identify checks for pawn, queen, bishop, king, rook by:
        for i in range(len(directions)):
            # Iterating through each of the 8 directions on the board with the king as its origin
            d = directions[i]
            possible_pin = ()
            for j in range(1, 8):
                # Radiates outward until a piece has been detected
                end_row = start_row + d[0] * j
                end_col = start_col + d[1] * j

                if 0 <= end_row < 8 and 0 <= end_col < 8:

                    # Saves the information of the given piece
                    end_piece = self.board[end_row][end_col]

                    # Determines if the piece is a piece of the same color
                    if end_piece.team == ally and end_piece.piece_type != 'K':
                        # if the piece is the same color, then it could potentially be blocking an attacking piece
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece.team == enemy_team:
                        piece_type = end_piece.piece_type

                        # In the event that the detected piece is attacking the king we check the following:
                        # Rook in the same row, bishop on the same diagonal, pawn on the same column, a queen (queen
                        # can move any direction and will always be an attacking piece no matter the direction), and
                        # a king one square away
                        if (0 <= i <= 3 and piece_type == 'R') or (4 <= i <= 7 and piece_type == 'B') or \
                                (j == 1 and piece_type == 'P' and
                                 ((enemy_team == 'w' and 6 <= i <= 7) or (enemy_team == 'b' and 4 <= i <= 5))) or \
                                (piece_type == 'Q') or (j == 1 and piece_type == 'K'):
                            # If the possible_pin list is empty, then there isn't any piece blocking the attack and the
                            # king is in check from a piece in a given direction
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            # If the possible_pin is not empty, then there is a blocking piece that is protecting the
                            # king and therefore pinned, restricting the movement to only the direction the pin is
                            # happening from
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break

        # determines the positions the knight is able to attack from
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        for k_moves in knight_moves:

            # calculates the location a knight can attack the king from
            end_row = start_row + k_moves[0]
            end_col = start_col + k_moves[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:

                # Checks to see if there is a knight at the position a knight could attack from
                # and if there is a knight, the king is now in check
                end_piece = self.board[end_row][end_col]

                if end_piece.team == enemy_team and end_piece.piece_type == 'N':
                    in_check = True
                    checks.append((end_row, end_col, k_moves[0], k_moves[1]))

        return in_check, pins, checks

    """
    Calculates all possible moves that each piece can make while disregarding any pieces that are pinned and 
    protecting the king and if the king is currently in check.    
    """

    def get_all_possible_moves(self) -> list:
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                team = self.board[r][c].team

                # Determines the piece type and calls the get_piece_move to calculate all possible move each
                # piece is able to make at its current position on the board
                if (team == 'w' and self.white_turn) or (team == 'b' and not self.white_turn):
                    if self.board[r][c].piece_type == 'P':
                        self.board[r][c].get_piece_move(r, c, self.white_turn, moves, self.board, self.pins,
                                                        self.white_king_loc,
                                                        self.black_king_loc, self.enpassant_square)
                    elif self.board[r][c].piece_type == 'K':
                        self.board[r][c].get_piece_move(r, c, moves, self.board, self.check_for_pins_checks,
                                                        self.white_king_loc, self.black_king_loc,
                                                        self.current_castle_rights,
                                                        self.square_under_attack)
                    else:
                        self.board[r][c].get_piece_move(r, c, moves, self.board, self.pins)

        return moves

    """
    Checks for ending game conditions that would results in a draw: King vs king, king and bishop vs king, 
    king and knight vs king, king and bishop vs king and bishop (same color bishop)
    """

    def check_for_draw(self) -> None:

        pieces_on_board = []

        # Scans to see which pieces are on the board
        for r in range(0, 8):
            for c in range(0, 8):
                if self.board[r][c].team != '-':
                    pieces_on_board.append(self.board[r][c])

        # 1- king vs king
        if len(pieces_on_board) == 2:
            self.draw = True

        # 2- King and bishop vs. king
        # 3- King and knight vs. king
        elif len(pieces_on_board) == 3:
            for i in range(len(pieces_on_board)):
                if pieces_on_board[i].piece_type == 'B' or pieces_on_board[i].piece_type == 'N':
                    self.draw = True
                    break

        # King and bishop vs. king and bishop (Same color bishop)
        elif len(pieces_on_board) == 4:
            bishop_square_color = ''
            for i in range(len(pieces_on_board)):
                if pieces_on_board[i].piece_type == 'B':
                    if pieces_on_board[i].square_color == bishop_square_color:
                        self.draw = True
                    else:
                        bishop_square_color = pieces_on_board[i].square_color

    """
    Calculates if there is any attacking pieces on a given square
    """

    @staticmethod
    def square_under_attack(r, c, board, piece_color) -> bool:

        if piece_color == 'w':
            enemy_team = 'b'
            ally = 'w'
        else:  # piece_color == 'b'
            enemy_team = 'w'
            ally = 'b'

        directions = (
            (-1, 0),  # 0 Up
            (0, -1),  # 1 Left
            (1, 0),  # 2 Down
            (0, 1),  # 3 Right
            (-1, -1),  # 4 Top left diagonal
            (-1, 1),  # 5 Top right diagonal
            (1, -1),  # 6  Bottom left diagonal
            (1, 1),  # 7 Bottom right diagonal
        )

        for i in range(len(directions)):
            d = directions[i]
            for j in range(1, 8):
                end_row = r + d[0] * j
                end_col = c + d[1] * j

                if 0 <= end_row < 8 and 0 <= end_col < 8:

                    end_piece = board[end_row][end_col]

                    if end_piece.team == ally:
                        break
                    elif end_piece.team == enemy_team:
                        piece_type = end_piece.piece_type

                        # Piece is under attack if any of the below conditionals are met
                        if (0 <= i <= 3 and piece_type == 'R') or (4 <= i <= 7 and piece_type == 'B') or \
                                (j == 1 and piece_type == 'P' and
                                 ((enemy_team == 'w' and 6 <= i <= 7) or (enemy_team == 'b' and 4 <= i <= 5))) or \
                                (piece_type == 'Q') or (j == 1 and piece_type == 'K'):
                            return True
                        else:
                            break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        # Identifies if a knight is attacking a square
        for k_moves in knight_moves:
            end_row = r + k_moves[0]
            end_col = c + k_moves[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = board[end_row][end_col]

                # Piece is under attack by a knight
                if end_piece.team == enemy_team and end_piece.piece_type == 'N':
                    return True

        return False
