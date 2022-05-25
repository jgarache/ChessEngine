"""
Chess AI creates an AI that uses the Negative-Max Alpha Pruning algorithm to play chess. The AI weighs piece material
multiplied by a positional weight (depending on the piece type) to determine the best move. Also, considers checks
and checkmates at a higher weight when deciding which move to make.
"""

import random

# Dictionary of values representing the score material of each piece
piece_score = {'K': 0, 'Q': 10, 'R': 5, 'N': 3, 'B': 3, 'P': 1}

# 2D lists that represent the weights of each position on the board depending on the piece
knight_score = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_score = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queen_score = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 4, 4, 4, 4, 2, 1],
               [1, 2, 4, 4, 4, 4, 2, 1],
               [1, 2, 4, 4, 4, 4, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]

rook_score = [[4, 4, 4, 4, 4, 4, 4, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [3, 3, 3, 3, 3, 3, 3, 3],
              [1, 2, 4, 4, 4, 4, 2, 1],
              [1, 2, 4, 4, 4, 4, 2, 1],
              [3, 3, 3, 3, 3, 3, 3, 3],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 4, 4, 4, 4, 4, 4, 4]]

b_king_score = [[5, 5, 5, 1, 1, 5, 5, 5],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

w_king_score = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [5, 5, 5, 5, 5, 5, 5, 5]]

w_pawn_score = [[5, 5, 5, 5, 5, 5, 5, 5],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0]]

b_pawn_score = [[0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [5, 5, 5, 5, 5, 5, 5, 5]]

# Dictionary of positional weights of each piece
piece_position_scores = {"bK": b_king_score, "wK": w_king_score, 'Q': queen_score, 'R': rook_score,
                         'N': knight_score, 'B': bishop_score, "wP": w_pawn_score, "bP": b_pawn_score}

# Value to indicate that it is the AI's turn
HUMAN_TURN = False

# Start checkmate at really high number to determine a move that would prevent placing the AI's 
# king into checkmate
CHECKMATE = 1000

# Setting stalemate to 0 to avoid moves that would end in a stalemate
STALEMATE = 0

# Controls the level of recursive calls the AI will undergo when calculating the best move
DEPTH = 3

# Next move
NEXT_MOVE = None

"""
If the AI is unable to determine the best move, the AI will default to using a 
random algorithm to select a move from list of valid moves
"""


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


"""
Helper function to start the recursive calls of the Negative-Max Alpha Beta Pruning function
"""


def find_best_move(gs, valid_moves, return_queue):
    global NEXT_MOVE

    NEXT_MOVE = None
    random.shuffle(valid_moves)
    find_move_negative_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_turn else -1)
    return_queue.put(NEXT_MOVE)


"""
The main move calculation that uses Negative-Max Alpha Beta pruning to select the best move 
from the given position on the board
"""


def find_move_negative_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global NEXT_MOVE

    # Base case - returns value of the pieces in a given board position
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE

    for move in valid_moves:
        gs.make_move(move, HUMAN_TURN)
        next_moves = gs.get_valid_moves()
        score = -find_move_negative_max_alpha_beta(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                NEXT_MOVE = move
        gs.undo_move()

        # Pruning stage
        if max_score > alpha:
            alpha = max_score

        if alpha >= beta:
            break

    return max_score


"""
Calculates score based on piece material, positions on the board, and checkmate/stalemate
"""


def score_board(gs):
    # + score is for white, - score is for black
    if gs.checkmate:
        if gs.white_turn:
            # Black wins
            return -CHECKMATE
        else:
            # White wins
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0

    # Add up the material on the board based on piece values and positional score
    for r in range(0, 8):
        for c in range(0, 8):
            piece_on_square = gs.board[r][c]
            if piece_on_square.team != '-':
                if piece_on_square.piece_type == 'P':
                    if piece_on_square.team == 'w':
                        piece_position_score = piece_position_scores["wP"][r][c]
                    else:
                        piece_position_score = piece_position_scores["bP"][r][c]
                elif piece_on_square.piece_type == 'K':
                    if piece_on_square.team == 'w':
                        piece_position_score = piece_position_scores["wK"][r][c]
                    else:
                        piece_position_score = piece_position_scores["bK"][r][c]
                else:
                    piece_position_score = piece_position_scores[piece_on_square.piece_type][r][c]
                if gs.board[r][c].team == 'w':
                    score += piece_score[piece_on_square.piece_type] + piece_position_score * 0.1
                elif gs.board[r][c].team == 'b':
                    score -= piece_score[piece_on_square.piece_type] + piece_position_score * 0.1

    return score
