"""
Pieces class calculates all possible moves a piece can perform at a given square on the board,
determines if the piece is blocking the king from being in check, 
and all behavior unique to a piece (i.e. pawn promotion, castling, etc). 
"""

from Move import Move
from typing import Union


class Pieces:
    # Specifies the pieces type: K, Q, R, N, B, P, or - (empty piece)
    piece_type = "-"

    """
    Initializes a piece in a specific spot on the board
    """

    def __init__(self, r, c, team) -> None:
        # row, column, and team (b, w, -)
        self.r = r
        self.c = c
        self.team = team

        # Variable for indicating which image to load for a specific piece (i.e. wP or --)
        self.piece_color_type = self.team + self.piece_type

    """
    Calculates all possible movements at a given location on the board by:
            1. Checks to see if piece is pinned from a given direction
            2. Calculates all moves in the direction the pin is coming from (other directions
            are not calculated because the piece is protecting the king)
            3. If not pinned, then all possible moves are calculated
    """

    def get_piece_move(self, r, c, moves, board, pins) -> None:
        return

    """
    Compares current location of piece with list of pins to determine if the piece is blocking the
    enemy teams attack from putting the king in check, therefore, the piece cannot move  
    """

    def is_pinned(self, pins, r, c) -> Union[tuple, bool]:  # returns bool as well
        pin_direction = ()
        pinned = False

        for i in range(len(pins) - 1, -1, -1):
            if pins[i][0] == r and pins[i][1] == c:
                pinned = True
                pin_direction = (pins[i][2], pins[i][3])
                pins.remove(pins[i])
                break

        return pin_direction, pinned


"""
Pawn class inherits from Pieces class and calculates the movement for pawns 
"""


class Pawn(Pieces):
    # Specifies piece type as Pawn
    piece_type = "P"

    """
    Determines if there is an attacking piece on the same row that the pawn started on that is threatening the king. 
    If there are any blocking pieces preventing the attacking piece, then the enpassant is possible. Otherwise, the 
    pawn is unable to enpassant because that move would leave the king vulnerable to an attack.   
    """

    @staticmethod
    def enpassant_threats(r, c, white_turn, board, white_king_loc, black_king_loc, left_side_capture) -> bool:
        attack_piece = blocking_piece = False

        if white_turn:
            enemy_team = 'b'
            king_row, king_col = white_king_loc
        else:
            enemy_team = 'w'
            king_row, king_col = black_king_loc

        if king_row == r:
            if king_col < c:  # King is left of the pawn trying to enpassant
                if left_side_capture:  # Range between the pawns trying to capture from the left to the king/border
                    between_king_pawn = range(king_col + 1, c - 1)
                    between_pawn_border = range(c + 1, 8)
                else:  # Range between the pawns trying to capture from the right to the king/border
                    between_king_pawn = range(king_col + 1, c)
                    between_pawn_border = range(c + 2, 8)
            else:  # King is right of the pawn trying to enpassant
                if left_side_capture:  # Range between the pawns trying to capture from the left to the king/border
                    between_king_pawn = range(king_col - 1, c, -1)
                    between_pawn_border = range(c - 2, -1, -1)
                else:  # Range between the pawns trying to capture from the right to the king/border
                    between_king_pawn = range(king_col - 1, c + 1, -1)
                    between_pawn_border = range(c - 1, -1, -1)

            # King is located on the right of the pawn and checks to see if there is a blocking piece
            for i in between_king_pawn:
                if board[r][i].team != '-':
                    blocking_piece = True
                    break

            # King is located left of the pawn and checks to see if there is an attacking/blocking piece to the right
            # of the pawn
            for i in between_pawn_border:
                square = board[r][i]
                if square.team == enemy_team and (square.piece_type == 'R' or square.piece_type == 'Q'):
                    attack_piece = True
                elif square.team != '-':
                    blocking_piece = True
                    break

        # Enpassant is possible if:
        # There is an attacking piece and a blocking piece
        # No attacking piece and a blocking piece
        # No attacking piece nor blocking piece
        enpassant_threat = (not attack_piece or blocking_piece)

        return enpassant_threat

    """
    Calculates the following movements of a pawn:
        1 pawn advance, 2 pawn advance (at starting row only), diagonal capture, 
        en-passant, and pawn promotion.
    """

    def get_piece_move(self, r, c, white_turn, moves, board, pins, white_king_loc, black_king_loc,
                       enpassant_square) -> None:

        # Calculates pin direction and if the piece's current location is protecting the king
        pin_direction, pinned = self.is_pinned(pins, r, c)

        # White pawn movement
        if white_turn and board[r][c].team == 'w':
            if not pinned or pin_direction == (-1, 0):
                # 1 sq pawn advance
                if board[r - 1][c].team == '-':
                    moves.append(Move((r, c), (r - 1, c), board))
                    # 2 sq pawn advance
                    if r == 6 and board[r - 2][c].team == '-':
                        moves.append(Move((r, c), (r - 2, c), board))

            # Capture top left diagonal
            if not pinned or pin_direction == (-1, -1):
                if c - 1 >= 0:
                    if board[r - 1][c - 1].team == 'b':
                        moves.append(Move((r, c), (r - 1, c - 1), board))

                    if (r - 1, c - 1) == enpassant_square and self.enpassant_threats(r, c, white_turn, board,
                                                                                     white_king_loc, black_king_loc,
                                                                                     True):
                        moves.append(Move((r, c), (r - 1, c - 1), board, enpassant_move=True))

            # Capture top right diagonal
            if not pinned or pin_direction == (-1, 1):
                if c + 1 <= 7:
                    if board[r - 1][c + 1].team == 'b':
                        moves.append(Move((r, c), (r - 1, c + 1), board))

                    if (r - 1, c + 1) == enpassant_square and self.enpassant_threats(r, c, white_turn, board,
                                                                                     white_king_loc, black_king_loc,
                                                                                     False):
                        moves.append(Move((r, c), (r - 1, c + 1), board, enpassant_move=True))

        # Black pawn movement
        if not white_turn and board[r][c].team == 'b':
            # 1 sq pawn advance
            if not pinned or pin_direction == (1, 0):
                if board[r + 1][c].team == '-':
                    moves.append(Move((r, c), (r + 1, c), board))

                    # 2 sq pawn advance
                    if r == 1 and board[r + 2][c].team == '-':
                        moves.append(Move((r, c), (r + 2, c), board))

            # Capture bottom left diagonal
            if not pinned or pin_direction == (1, -1):
                if c - 1 >= 0:
                    if board[r + 1][c - 1].team == 'w':
                        moves.append(Move((r, c), (r + 1, c - 1), board))

                    if (r + 1, c - 1) == enpassant_square and self.enpassant_threats(r, c, white_turn, board,
                                                                                     white_king_loc, black_king_loc,
                                                                                     True):
                        moves.append(Move((r, c), (r + 1, c - 1), board, enpassant_move=True))

            # Capture bottom right diagonal
            if not pinned or pin_direction == (1, 1):
                if c + 1 <= 7:
                    if board[r + 1][c + 1].team == 'w':
                        moves.append(Move((r, c), (r + 1, c + 1), board))

                    if (r + 1, c + 1) == enpassant_square and self.enpassant_threats(r, c, white_turn, board,
                                                                                     white_king_loc, black_king_loc,
                                                                                     False):
                        moves.append(Move((r, c), (r + 1, c + 1), board, enpassant_move=True))


"""
Rook class inherits from Pieces class and calculates the movement for rooks 
"""


class Rook(Pieces):
    # Specifies piece type as Rook
    piece_type = "R"

    """
    Calculates all orthogonal directions of a rook at a given square on the board.
    """

    def get_piece_move(self, r, c, moves, board, pins) -> None:

        # Calculates pin direction and if the piece's current location is protecting the king
        pin_direction, pinned = self.is_pinned(pins, r, c)

        # UP and DOWN
        if not pinned or (pin_direction == (-1, 0) or pin_direction == (1, 0)):
            # UP
            for i in range(8):
                if r - i - 1 >= 0:
                    # Empty space
                    if board[r - i - 1][c].team == '-':
                        moves.append(Move((r, c), (r - i - 1, c), board))

                    # Same color piece is blocking the way
                    if board[r - i - 1][c].team != '-' and board[r - i - 1][c].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r - i - 1][c].team != '-' and board[r - i - 1][c].team != board[r][c].team:
                        moves.append(Move((r, c), (r - i - 1, c), board))
                        break

                else:
                    break

            # DOWN
            for i in range(8):

                if r + i + 1 <= 7:
                    # Empty space
                    if board[r + i + 1][c].team == '-':
                        moves.append(Move((r, c), (r + i + 1, c), board))

                    # Same color piece is blocking the way
                    if board[r + i + 1][c].team != '-' and board[r + i + 1][c].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r + i + 1][c].team != '-' and board[r + i + 1][c].team != board[r][c].team:
                        moves.append(Move((r, c), (r + i + 1, c), board))
                        break

                else:
                    break

        # LEFT and RIGHT
        if not pinned or (pin_direction == (0, -1) or pin_direction == (0, 1)):
            # LEFT
            for i in range(8):
                if c - i - 1 >= 0:
                    # Empty space
                    if board[r][c - i - 1].team == '-':
                        moves.append(Move((r, c), (r, c - i - 1), board))

                    # Same color piece is blocking the way
                    if board[r][c - i - 1].team != '-' and board[r][c - i - 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r][c - i - 1].team != '-' and board[r][c - i - 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r, c - i - 1), board))
                        break

                else:
                    break

            # RIGHT
            for i in range(8):
                if c + i + 1 <= 7:
                    # Empty space
                    if board[r][c + i + 1].team == '-':
                        moves.append(Move((r, c), (r, c + i + 1), board))

                    # Same color piece is blocking the way
                    if board[r][c + i + 1].team != '-' and board[r][c + i + 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r][c + i + 1].team != '-' and board[r][c + i + 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r, c + i + 1), board))
                        break

                else:
                    break


"""
Knight class inherits from Pieces class and calculates the movement for knights 
"""


class Knight(Pieces):
    # Specifies piece type as Knight
    piece_type = "N"

    """
    Compares the current location of the knight with the list of pins to determine if the knight is pinned 
    and protecting the king, if so, the knight is unable to move

    """

    def is_pinned(self, pins, r, c) -> bool:
        pinned = False

        for i in range(len(pins) - 1, -1, -1):
            if pins[i][0] == r and pins[i][1] == c:
                pinned = True
                pins.remove(pins[i])
                break

        return pinned

    """
    Calculates all 8 locations a knight is able to move. Check README for more information.
    """

    def get_piece_move(self, r, c, moves, board, pins) -> None:

        # Calculates if the knight is pinned and protecting the king from check
        pinned = self.is_pinned(pins, r, c)

        # If the knight isn't pinned, then it is able to move
        if not pinned:
            # LEFT TOP
            if r - 1 >= 0 and c - 2 >= 0:
                # Empty space or Piece capture
                if board[r - 1][c - 2].team == '-' or (
                        board[r - 1][c - 2].team != '-' and board[r - 1][c - 2].team != board[r][c].team):
                    moves.append(Move((r, c), (r - 1, c - 2), board))

            # LEFT BOTTOM
            if r + 1 <= 7 and c - 2 >= 0:
                # Empty space or Piece capture
                if board[r + 1][c - 2].team == '-' or (
                        board[r + 1][c - 2].team != '-' and board[r + 1][c - 2].team != board[r][c].team):
                    moves.append(Move((r, c), (r + 1, c - 2), board))

            # RIGHT TOP
            if r - 1 >= 0 and c + 2 <= 7:
                # Empty space or Piece capture
                if board[r - 1][c + 2].team == '-' or (
                        board[r - 1][c + 2].team != '-' and board[r - 1][c + 2].team != board[r][c].team):
                    moves.append(Move((r, c), (r - 1, c + 2), board))

            # RIGHT BOTTOM
            if r + 1 <= 7 and c + 2 <= 7:
                # Empty space or Piece capture
                if board[r + 1][c + 2].team == '-' or (
                        board[r + 1][c + 2].team != '-' and board[r + 1][c + 2].team != board[r][c].team):
                    moves.append(Move((r, c), (r + 1, c + 2), board))

            # MIDDLE TOP LEFT
            if r - 2 >= 0 and c - 1 >= 0:

                # Empty space or Piece capture
                if board[r - 2][c - 1].team == '-' or (
                        board[r - 2][c - 1].team != '-' and board[r - 2][c - 1].team != board[r][c].team):
                    moves.append(Move((r, c), (r - 2, c - 1), board))

            # MIDDLE TOP RIGHT
            if r - 2 >= 0 and c + 1 <= 7:
                # Empty space or Piece capture
                if board[r - 2][c + 1].team == '-' or (
                        board[r - 2][c + 1].team != '-' and board[r - 2][c + 1].team != board[r][c].team):
                    moves.append(Move((r, c), (r - 2, c + 1), board))

            # MIDDLE BOTTOM LEFT
            if r + 2 <= 7 and c - 1 >= 0:
                # Empty space or Piece capture
                if board[r + 2][c - 1].team == '-' or (
                        board[r + 2][c - 1].team != '-' and board[r + 2][c - 1].team != board[r][c].team):
                    moves.append(Move((r, c), (r + 2, c - 1), board))

            # MIDDLE BOTTOM RIGHT
            if r + 2 <= 7 and c + 1 <= 7:
                # Empty space or Piece capture
                if board[r + 2][c + 1].team == '-' or (
                        board[r + 2][c + 1].team != '-' and board[r + 2][c + 1].team != board[r][c].team):
                    moves.append(Move((r, c), (r + 2, c + 1), board))


"""
Bishop class inherits from Pieces class and calculates the movement for bishop 
"""


class Bishop(Pieces):
    # Specifies piece type as Bishop
    piece_type = "B"

    # initializes the bishop piece with additional variable, square_color, to distinguish if the bishop is on a light
    # or dark square
    def __init__(self, r, c, team, square_color) -> None:
        self.square_color = square_color
        super().__init__(r, c, team)

    """
    Calculates all diagonal positions the bishop can move in
    """

    def get_piece_move(self, r, c, moves, board, pins) -> None:

        # Calculates if the knight is pinned and protecting the king from check
        pin_direction, pinned = self.is_pinned(pins, r, c)

        # TOP LEFT DIAGONAL and BOTTOM RIGHT DIAGONAL
        if not pinned or (pin_direction == (-1, -1) or pin_direction == (1, 1)):
            # TOP LEFT DIAGONAL
            for i in range(8):

                if r - i - 1 >= 0 and c - i - 1 >= 0:
                    # Empty space
                    if board[r - i - 1][c - i - 1].team == '-':
                        moves.append(Move((r, c), (r - i - 1, c - i - 1), board))

                    # Same color piece is blocking the way
                    if board[r - i - 1][c - i - 1].team != '-' and board[r - i - 1][c - i - 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r - i - 1][c - i - 1].team != '-' and board[r - i - 1][c - i - 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r - i - 1, c - i - 1), board))
                        break

                else:
                    break

            # BOTTOM RIGHT DIAGONAL
            for i in range(8):

                if r + i + 1 <= 7 and c + i + 1 <= 7:
                    # Empty space
                    if board[r + i + 1][c + i + 1].team == '-':
                        moves.append(Move((r, c), (r + i + 1, c + i + 1), board))

                    # Same color piece is blocking the way
                    if board[r + i + 1][c + i + 1].team != '-' and board[r + i + 1][c + i + 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r + i + 1][c + i + 1].team != '-' and board[r + i + 1][c + i + 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r + i + 1, c + i + 1), board))
                        break

                else:
                    break

        # TOP RIGHT DIAGONAL and BOTTOM LEFT DIAGONAL
        if not pinned or (pin_direction == (-1, 1) or pin_direction == (1, -1)):
            # TOP RIGHT DIAGONAL
            for i in range(8):

                if r - i - 1 >= 0 and c + i + 1 <= 7:
                    # Empty space
                    if board[r - i - 1][c + i + 1].team == '-':
                        moves.append(Move((r, c), (r - i - 1, c + i + 1), board))

                    # Same color piece is blocking the way
                    if board[r - i - 1][c + i + 1].team != '-' and board[r - i - 1][c + i + 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r - i - 1][c + i + 1].team != '-' and board[r - i - 1][c + i + 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r - i - 1, c + i + 1), board))
                        break

                else:
                    break

            # BOTTOM LEFT DIAGONAL
            for i in range(8):

                if r + i + 1 <= 7 and c - i - 1 >= 0:
                    # Empty space
                    if board[r + i + 1][c - i - 1].team == '-':
                        moves.append(Move((r, c), (r + i + 1, c - i - 1), board))

                    # Same color piece is blocking the way
                    if board[r + i + 1][c - i - 1].team != '-' and board[r + i + 1][c - i - 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r + i + 1][c - i - 1].team != '-' and board[r + i + 1][c - i - 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r + i + 1, c - i - 1), board))
                        break

                else:
                    break


"""
King class inherits from Pieces class and calculates the movement for kings 
"""


class King(Pieces):
    # Specifies piece type as King
    piece_type = "K"

    """
    A utility function to calculates if a given set of coordinates (squares on the board) 
    would place the king into check
    """

    @staticmethod
    def get_piece_move_utility(r, c, r_end, c_end, moves, board, check_for_pins_checks, white_king_loc,
                               black_king_loc) -> None:
        # Check for white or black king/temp move king position to specific square
        if board[r][c].team == 'w':
            white_king_loc = (r_end, c_end)
        elif board[r][c].team == 'b':
            black_king_loc = (r_end, c_end)

        # check for pins and checks
        in_check, pins, checks = check_for_pins_checks(white_king_loc, black_king_loc)

        # if not in check, append move
        if not in_check:
            moves.append(Move((r, c), (r_end, c_end), board))

    """
    Calculates to see if the king side castle is not under attack, blocked by other pieces, and that the rook is still
    in its starting position
    """

    @staticmethod
    def get_king_side_castle(r, c, moves, board, square_under_attack) -> None:

        if 0 <= c + 1 < 8 and 0 <= c + 2 < 8:
            if board[r][c + 1].piece_type == '-' and board[r][c + 2].piece_type == '-':

                # None of the squares are under attack
                if not square_under_attack(r, c + 1, board, board[r][c].team) and \
                        not square_under_attack(r, c + 2, board, board[r][c].team):
                    moves.append(Move((r, c), (r, c + 2), board, castle_move=True))

    """
    Calculates to see if the queen side castle is not under attack, blocked by other pieces, and that the rook is still
    in its starting position
    """

    @staticmethod
    def get_queen_side_castle(r, c, moves, board, square_under_attack) -> None:

        if 0 <= c - 1 < 8 and 0 <= c - 2 < 8 and 0 <= c - 3 < 8:
            if board[r][c - 1].piece_type == '-' and board[r][c - 2].piece_type == '-' \
                    and board[r][c - 3].piece_type == '-':

                # None of the squares are under attack
                if not square_under_attack(r, c - 1, board, board[r][c].team) and \
                        not square_under_attack(r, c - 2, board, board[r][c].team) and \
                        not square_under_attack(r, c - 3, board, board[r][c].team):
                    moves.append(Move((r, c), (r, c - 2), board, castle_move=True))

    """
    Main function that calls get_king_side_castle and get_queen_side_castle to calculate if castling is possible 
    on either the king or queen side 
    """

    def get_castle_moves(self, r, c, moves, board, check_for_pins_checks, white_king_loc,
                         black_king_loc, castle_rights, square_under_attack) -> None:

        # check for pins and checks
        in_check, pins, checks = check_for_pins_checks(white_king_loc, black_king_loc)

        # Checks to see if king is in check
        if in_check:
            return

        # Checks to see if King side squares are all empty
        if (board[r][c].team == 'w' and castle_rights.wks) or (board[r][c].team == 'b' and castle_rights.bks):
            self.get_king_side_castle(r, c, moves, board, square_under_attack)

        # checks to see if Queen side squares are all empty
        if (board[r][c].team == 'w' and castle_rights.wqs) or (board[r][c].team == 'b' and castle_rights.bqs):
            self.get_queen_side_castle(r, c, moves, board, square_under_attack)

    """
    Primary function to calculate the kings movement in all direction. Calculates the potential squares the 
    king could move to and uses the utility function to verify if that move is valid or not.   
    """

    def get_piece_move(self, r, c, moves, board, check_for_pins_checks, white_king_loc, black_king_loc, castle_rights,
                       square_under_attack) -> None:

        # UP
        if r - 1 >= 0 and (board[r - 1][c].team == '-' or (
                board[r - 1][c].team != '-' and board[r - 1][c].team != board[r][c].team)):
            self.get_piece_move_utility(r, c, r - 1, c, moves, board, check_for_pins_checks, white_king_loc,
                                        black_king_loc)

        # DOWN 
        if r + 1 <= 7 and (board[r + 1][c].team == '-' or (
                board[r + 1][c].team != '-' and board[r + 1][c].team != board[r][c].team)):
            self.get_piece_move_utility(r, c, r + 1, c, moves, board, check_for_pins_checks, white_king_loc,
                                        black_king_loc)

        # LEFT    
        if c - 1 >= 0 and (board[r][c - 1].team == '-' or (
                board[r][c - 1].team != '-' and board[r][c - 1].team != board[r][c].team)):
            self.get_piece_move_utility(r, c, r, c - 1, moves, board, check_for_pins_checks, white_king_loc,
                                        black_king_loc)

        # RIGHT
        if c + 1 <= 7 and (board[r][c + 1].team == '-' or (
                board[r][c + 1].team != '-' and board[r][c + 1].team != board[r][c].team)):
            self.get_piece_move_utility(r, c, r, c + 1, moves, board, check_for_pins_checks, white_king_loc,
                                        black_king_loc)

        # TOP LEFT DIAGONAL    
        if (r - 1 >= 0 and c - 1 >= 0) and (board[r - 1][c - 1].team == '-' or (
                board[r - 1][c - 1].team != '-' and board[r - 1][c - 1].team != board[r][c].team)):
            self.get_piece_move_utility(r, c, r - 1, c - 1, moves, board, check_for_pins_checks, white_king_loc,
                                        black_king_loc)

        # TOP RIGHT DIAGONAL    
        if (r - 1 >= 0 and c + 1 <= 7) and (board[r - 1][c + 1].team == '-' or (
                board[r - 1][c + 1].team != '-' and board[r - 1][c + 1].team != board[r][c].team)):
            self.get_piece_move_utility(r, c, r - 1, c + 1, moves, board, check_for_pins_checks, white_king_loc,
                                        black_king_loc)

        # BOTTOM LEFT DIAGONAL
        if (r + 1 <= 7 and c - 1 >= 0) and (board[r + 1][c - 1].team == '-' or (
                board[r + 1][c - 1].team != '-' and board[r + 1][c - 1].team != board[r][c].team)):
            self.get_piece_move_utility(r, c, r + 1, c - 1, moves, board, check_for_pins_checks, white_king_loc,
                                        black_king_loc)

        # BOTTOM RIGHT DIAGONAL
        if (r + 1 <= 7 and c + 1 <= 7) and (board[r + 1][c + 1].team == '-' or (
                board[r + 1][c + 1].team != '-' and board[r + 1][c + 1].team != board[r][c].team)):
            self.get_piece_move_utility(r, c, r + 1, c + 1, moves, board, check_for_pins_checks, white_king_loc,
                                        black_king_loc)

        # CASTLING
        self.get_castle_moves(r, c, moves, board, check_for_pins_checks, white_king_loc,
                              black_king_loc, castle_rights, square_under_attack)


"""
Queen class inherits from Pieces class and calculates the movement for Queens
"""


class Queen(Pieces):
    # Specifies piece type as Queen
    piece_type = 'Q'

    """
    Calculates all diagonal and orthogonal directions a Queen can move in
    """

    def get_piece_move(self, r, c, moves, board, pins) -> None:

        # Calculates if the knight is pinned and protecting the king from check
        pin_direction, pinned = self.is_pinned(pins, r, c)

        # UP and DOWN
        if not pinned or (pin_direction == (-1, 0) or pin_direction == (1, 0)):
            # UP
            for i in range(8):
                if r - i - 1 >= 0:
                    # Empty space
                    if board[r - i - 1][c].team == '-':
                        moves.append(Move((r, c), (r - i - 1, c), board))

                    # Same color piece is blocking the way
                    if board[r - i - 1][c].team != '-' and board[r - i - 1][c].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r - i - 1][c].team != '-' and board[r - i - 1][c].team != board[r][c].team:
                        moves.append(Move((r, c), (r - i - 1, c), board))
                        break

                else:
                    break

            # DOWN
            for i in range(8):

                if r + i + 1 <= 7:
                    # Empty space
                    if board[r + i + 1][c].team == '-':
                        moves.append(Move((r, c), (r + i + 1, c), board))

                    # Same color piece is blocking the way
                    if board[r + i + 1][c].team != '-' and board[r + i + 1][c].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r + i + 1][c].team != '-' and board[r + i + 1][c].team != board[r][c].team:
                        moves.append(Move((r, c), (r + i + 1, c), board))
                        break

                else:
                    break

        # LEFT and RIGHT
        if not pinned or (pin_direction == (0, -1) or pin_direction == (0, 1)):
            # LEFT
            for i in range(8):
                if c - i - 1 >= 0:
                    # Empty space
                    if board[r][c - i - 1].team == '-':
                        moves.append(Move((r, c), (r, c - i - 1), board))

                    # Same color piece is blocking the way
                    if board[r][c - i - 1].team != '-' and board[r][c - i - 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r][c - i - 1].team != '-' and board[r][c - i - 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r, c - i - 1), board))
                        break

                else:
                    break

            # RIGHT
            for i in range(8):
                if c + i + 1 <= 7:
                    # Empty space
                    if board[r][c + i + 1].team == '-':
                        moves.append(Move((r, c), (r, c + i + 1), board))

                    # Same color piece is blocking the way
                    if board[r][c + i + 1].team != '-' and board[r][c + i + 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r][c + i + 1].team != '-' and board[r][c + i + 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r, c + i + 1), board))
                        break

                else:
                    break

        # TOP LEFT DIAGONAL and BOTTOM RIGHT DIAGONAL
        if not pinned or (pin_direction == (-1, -1) or pin_direction == (1, 1)):
            # TOP LEFT DIAGONAL
            for i in range(8):

                if r - i - 1 >= 0 and c - i - 1 >= 0:
                    # Empty space
                    if board[r - i - 1][c - i - 1].team == '-':
                        moves.append(Move((r, c), (r - i - 1, c - i - 1), board))

                    # Same color piece is blocking the way
                    if board[r - i - 1][c - i - 1].team != '-' and board[r - i - 1][c - i - 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r - i - 1][c - i - 1].team != '-' and board[r - i - 1][c - i - 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r - i - 1, c - i - 1), board))
                        break

                else:
                    break

            # BOTTOM RIGHT DIAGONAL
            for i in range(8):

                if r + i + 1 <= 7 and c + i + 1 <= 7:
                    # Empty space
                    if board[r + i + 1][c + i + 1].team == '-':
                        moves.append(Move((r, c), (r + i + 1, c + i + 1), board))

                    # Same color piece is blocking the way
                    if board[r + i + 1][c + i + 1].team != '-' and board[r + i + 1][c + i + 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r + i + 1][c + i + 1].team != '-' and board[r + i + 1][c + i + 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r + i + 1, c + i + 1), board))
                        break

                else:
                    break

        # TOP RIGHT DIAGONAL and BOTTOM LEFT DIAGONAL
        if not pinned or (pin_direction == (-1, 1) or pin_direction == (1, -1)):
            # TOP RIGHT DIAGONAL
            for i in range(8):

                if r - i - 1 >= 0 and c + i + 1 <= 7:
                    # Empty space
                    if board[r - i - 1][c + i + 1].team == '-':
                        moves.append(Move((r, c), (r - i - 1, c + i + 1), board))

                    # Same color piece is blocking the way
                    if board[r - i - 1][c + i + 1].team != '-' and board[r - i - 1][c + i + 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r - i - 1][c + i + 1].team != '-' and board[r - i - 1][c + i + 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r - i - 1, c + i + 1), board))
                        break

                else:
                    break

            # BOTTOM LEFT DIAGONAL
            for i in range(8):

                if r + i + 1 <= 7 and c - i - 1 >= 0:
                    # Empty space
                    if board[r + i + 1][c - i - 1].team == '-':
                        moves.append(Move((r, c), (r + i + 1, c - i - 1), board))

                    # Same color piece is blocking the way
                    if board[r + i + 1][c - i - 1].team != '-' and board[r + i + 1][c - i - 1].team == board[r][c].team:
                        break

                    # Piece capture
                    if board[r + i + 1][c - i - 1].team != '-' and board[r + i + 1][c - i - 1].team != board[r][c].team:
                        moves.append(Move((r, c), (r + i + 1, c - i - 1), board))
                        break

                else:
                    break
