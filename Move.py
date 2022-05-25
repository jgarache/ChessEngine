"""
The Move class stores the information of which chess piece is being moved,
the starting and ending location of the piece, and which piece was captured during the move.
"""


class Move:
    # Dictionary to convert ranks to rows
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}

    # Switches value and keys within dictionary
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    # Dictionary to convert files to columns
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}

    # Switches value and keys within dictionary
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    """   
    Initializes a move describing the starting and ending position of a chess piece 
    """

    def __init__(self, start_sq, end_sq, board, enpassant_move=False, castle_move=False) -> None:
        # Starting position (row x col) of the chess piece
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]

        # Ending position (row x col) where the chess piece will be placed
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        # Information of the piece being moved
        self.piece_moved = board[self.start_row][self.start_col]

        # Information of the piece being captured
        # A blank space is a Piece object and still can be captured
        self.piece_captured = board[self.end_row][self.end_col]

        # Unique integer to allow comparison between moves
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

        # Flag to determine if a pawn will be promoted
        self.is_pawn_promotion = ((self.piece_moved.piece_color_type == "wP" and self.end_row == 0) or
                                  (self.piece_moved.piece_color_type == "bP" and self.end_row == 7))

        # Flag to determine if en passant is achievable
        self.is_enpassant_move = enpassant_move

        if self.is_enpassant_move:
            self.piece_captured = board[self.start_row][self.end_col]

        # Castling
        self.is_castle_move = castle_move

        # Determine if move is capture
        self.is_capture = self.piece_captured.piece_type != '-'

    """   
    Allows comparison between two Move objects allowing to check if a move is valid
    """

    def __eq__(self, other) -> bool:
        return isinstance(other, Move) and self.move_id == other.move_id

    """
    Allows move objects to be printable with proper chess notation
    """

    def __str__(self) -> str:
        # Castle move
        if self.is_castle_move:
            return "O-O" if self.end_col == 6 else "O-O-O"

        end_square = self.get_rank_file(self.end_row, self.end_col)

        # Pawn moves
        if self.piece_moved.piece_type == 'P':
            if self.is_capture:
                return self.cols_to_files[self.start_col] + 'x' + end_square
            else:
                return end_square

        move_string = self.piece_moved.piece_type
        if self.is_capture:
            move_string += 'x'
        return move_string + end_square

        # Todo
        # pawn promotions
        # two of the same type of piece moving to the same square (i.e. two knights moving to same square)
        # Also adding + for check move, # for checkmate move

    """   
    Provides chess notation of a move that was made
    """

    def get_chess_notation(self) -> str:
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    """   
    Get file rank notation
    
    """

    def get_rank_file(self, r, c) -> str:
        return self.cols_to_files[c] + self.rows_to_ranks[r]
