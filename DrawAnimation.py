import pygame
import os

# Variables to control attributes of the games window
BOARD_WIDTH = BOARD_HEIGHT = 800

# Variables to control move log width and height
MOVE_LOG_RECTANGLE_WIDTH = 250
MOVE_LOG_RECTANGLE_HEIGHT = BOARD_HEIGHT
DIMENSION = 8

# Variable to control the size of the images and squares
SQ_SIZE = BOARD_HEIGHT // DIMENSION

# List to store images of each piece
IMAGES = {}

# Colors
colors = [pygame.Color("white"), pygame.Color("tan")]

# Variables to manage/create game window
WIN = pygame.display.set_mode((BOARD_WIDTH + MOVE_LOG_RECTANGLE_WIDTH, BOARD_HEIGHT))
WIN.fill(pygame.Color("white"))
pygame.display.set_caption("Chess")

"""
Loads the images for each piece into IMAGES list
"""


def load_images() -> None:
    pieces = ["bB", "bK", "bN", "bP", "bQ", "bR", "wB", "wK", "wN", "wP", "wQ", "wR"]

    # Stores scaled image to size of square into IMAGE list
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(os.path.join("img/" + piece + ".png")),
                                               (SQ_SIZE, SQ_SIZE))


"""
Draws each square comprising the board
"""


def draw_board() -> None:
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # Calculates odd and even numbers to generate alternating color pattern of the board
            color = colors[(r + c) % 2]
            pygame.draw.rect(WIN, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Highlights the piece and all spaces it can move to
"""


def highlight_move_squares(gs, valid_moves, sq_selected) -> None:
    if sq_selected != ():

        r, c = sq_selected

        if gs.board[r][c].team == ('w' if gs.white_turn else 'b'):
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            # Highlights selected piece blue
            s.fill(pygame.Color("blue"))
            WIN.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # Highlights all squares a piece can move to yellow
            s.fill(pygame.Color("yellow"))

            # Finds the matching move with row and column to highlight square a piece is able to move to
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    WIN.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


"""
Highlights the king when it is under attack
"""


def highlight_king_under_attack(gs) -> None:
    # Identifies which king to highlight
    if gs.white_turn:
        r, c = gs.white_king_loc
    else:
        r, c = gs.black_king_loc

    # High lights the kings square red if it is under attack
    if gs.square_under_attack(r, c, gs.board, gs.board[r][c].team):
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(pygame.Color("red"))
        WIN.blit(s, (c * SQ_SIZE, r * SQ_SIZE))


"""
Draws each piece onto the specific position on the board
"""


def draw_pieces(board) -> None:
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # Blit piece images from IMAGE list onto specific row and column on the board
            piece = board[r][c].piece_color_type

            # Skips drawing images at blank spaces
            if piece != "--":
                WIN.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draws the move log (located on the right side of the screen) and the text of each move
"""


def draw_move_log(gs, font) -> None:
    # Creates the black rectangle where the move log will be placed on the screen
    move_log_rect = pygame.Rect(BOARD_WIDTH, 0, MOVE_LOG_RECTANGLE_WIDTH, MOVE_LOG_RECTANGLE_HEIGHT)
    pygame.draw.rect(WIN, pygame.Color("black"), move_log_rect)

    # Copies the list that contains all the moves performed in the game
    move_log = gs.move_log
    move_texts = []

    # Variables to assist with aligning the text on the screen
    padding = 5
    text_y = padding
    line_space = 2
    move_per_row = 2

    instructions = ["z - Undo Move", "r - Reset Game", "a - Toggle Animation", "s - AI v AI",
                    "d - Human v AI", "f - Human v Human"]
    modes = ["Game Mode: AI v AI", "Game Mode: Human v AI", "Game Mode: Human v Human"]
    game_mode_text = ""

    # Concatenates the number with the specific move in chess notation
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + ". " + str(move_log[i]) + ' '
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + ' '

        move_texts.append(move_string)

    # Prints the move_per_row onto the screen
    # I.e. if move_per_row = 2, then each line on the black part of the screen will print that many moves
    for i in range(0, len(move_texts), move_per_row):
        text = ""
        for j in range(move_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]
        text_object = font.render(text, True, pygame.Color("white"))
        text_location = move_log_rect.move(padding, text_y)
        WIN.blit(text_object, text_location)
        text_y += text_object.get_height() + line_space
    
    # Moves the text further down the move log
    text_y = 670

    # Prints the current game mode
    if gs.game_mode == "AVA":
        game_mode_text = modes[0]
    elif gs.game_mode == "HVA":
        game_mode_text = modes[1]
    elif gs.game_mode == "HVH":
        game_mode_text = modes[2]

    text_object = font.render(game_mode_text, True, pygame.Color("white"))
    game_mode_text_loc = move_log_rect.move(padding, text_y)
    WIN.blit(text_object, game_mode_text_loc)
    text_y += text_object.get_height() + line_space

    # Prints the instructions at the bottom right of the screen
    for instruction in instructions:
        text_object = font.render(instruction, True, pygame.Color("white"))
        text_location = move_log_rect.move(padding, text_y)
        WIN.blit(text_object, text_location)
        text_y += text_object.get_height() + line_space


"""
Draws the end game text based on a string parameter that determines if the game ends in a draw, stalemate, or checkmate
"""


def draw_end_game_text(text) -> None:
    font = pygame.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, pygame.Color("Black"))
    text_location = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                      BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    WIN.blit(text_object, text_location)


"""
Draws the entire state of the board, pieces and board included
"""


def draw_game_state(gs, valid_moves, sq_selected, move_log_font) -> None:
    draw_board()
    highlight_move_squares(gs, valid_moves, sq_selected)
    highlight_king_under_attack(gs)
    draw_pieces(gs.board)
    draw_move_log(gs, move_log_font)


"""
Animates the pieces moving from start to the end position on the board
"""


def animate_move(move, board, clock) -> None:
    # Changes from start to ending position on the board
    delta_row = move.end_row - move.start_row
    delta_col = move.end_col - move.start_col

    # Controls the number of frames the animations will flip through
    frames_per_square = 10

    # Calculates the total number of frames the piece will move through during the animation
    frame_count = (abs(delta_col) + abs(delta_row)) * frames_per_square

    for frame in range(frame_count + 1):
        r, c = (move.start_row + delta_row * frame / frame_count,
                move.start_col + delta_col * frame / frame_count)

        # Draws board and pieces
        draw_board()
        draw_pieces(board)

        # Calculates the ending square color and position
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = pygame.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)

        # Draws the piece at the ending square
        pygame.draw.rect(WIN, color, end_square)

        # Animates the pawn capturing during enpassant so that the animation
        # shows the pawn capturing above or below the pawn that is captured
        if move.piece_captured.team != '-':
            if move.is_enpassant_move:
                enpassant_row = (move.end_row + 1) if move.piece_captured.team == 'b' else (move.end_row - 1)
                end_square = pygame.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            WIN.blit(IMAGES[move.piece_captured.piece_color_type], end_square)

        WIN.blit(IMAGES[move.piece_moved.piece_color_type], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        pygame.display.flip()
        clock.tick(60)
