import pygame

from ChessEngine import GameState
import ChessAI
from Move import Move
# from multiprocessing import Process, Queue
from multiprocessing import Queue
import DrawAnimation


"""
Determines if the game is over either by checkmate, stalemate, or draw
"""


def is_game_over(gs, game_over) -> bool:
    text = ''

    if gs.checkmate or gs.stalemate or gs.draw:

        game_over = True

        if gs.stalemate:
            text = "Stalemate!"
        elif gs.checkmate:
            text = "Black wins by Checkmate!" if gs.white_turn else "White wins by Checkmate!"
        elif gs.draw:
            text = "Draw!"

        # Draws the end game text on the screen
        DrawAnimation.draw_end_game_text(text)

    return game_over


"""
Uses mouse clicks to select the board position and piece the player would like to move
"""


def player(gs, sq_selected, player_clicks, move_made, valid_moves, human_turn):
    # Specifies which square on the board the player has selected (i.e. row x column)
    location = pygame.mouse.get_pos()
    row = location[1] // DrawAnimation.SQ_SIZE
    col = location[0] // DrawAnimation.SQ_SIZE

    # Checking if user selects the same square twice
    # Deselects if the user selects the same square twice in a row
    if sq_selected == (row, col) or col >= 8:
        sq_selected = ()
        player_clicks.clear()
    else:  # User has selected a diff square
        sq_selected = (row, col)
        # Appends two sets of tuples/ mouse coordinates to indicate a players move
        player_clicks.append(sq_selected)

    # If there are two tuples in the player_clicks list, the start and ending positions have been
    # selected, so make the move
    if len(player_clicks) == 2 and human_turn:
        move = Move(player_clicks[0], player_clicks[1], gs.board)

        # Validates a players move
        for i in range(len(valid_moves)):
            if move == valid_moves[i]:
                gs.make_move(valid_moves[i], human_turn)
                move_made = True

                # Resets the tuple and list in preparation of the next move
                sq_selected = ()
                player_clicks.clear()

        # If a player changes their mind to select a different piece to move after select
        # the initial piece, instead of clicking the new piece twice and then make a move,
        # this will allow clicking the new piece once and then the desire ending location
        if not move_made:
            player_clicks = [sq_selected]

    return sq_selected, player_clicks, move_made


"""
Controls the AI's movement and uses multi threading so the player is able to click the board while 
the AI is calculating the best move 
"""


def artificial_intel(gs, AI_processing, move_finder_process, return_queue, valid_moves, human_turn,
                     move_made):

    # Starts the move calculation in another thread if the AI isn't already calculating
    # if not AI_processing:
    #    AI_processing = True
    #    move_finder_process = Process(target=ChessAI.find_best_move, args=(gs, valid_moves, return_queue))
    #    move_finder_process.start()

    # Once the move calculation is complete, the thread will have terminated and placed the move into a move queue
    # The AI retrieves the move from the return_queue, if the move is None, then a random move will be selected instead
    # if not move_finder_process.is_alive():
    if not human_turn:
        # AI_move = return_queue.get()
        AI_move = ChessAI.find_best_move(gs, valid_moves, return_queue)
        if AI_move is None:
            AI_move = ChessAI.find_random_move(valid_moves)
        gs.make_move(AI_move, human_turn)
        move_made = True
        AI_processing = False

    return move_made, AI_processing, move_finder_process


"""
Handles running all critical functions for the game to run such as:
draw_game_state, moves, and event loop that captures all inputs from mouse and keyboard 
"""


def main() -> None:
    # Initializes pygame
    pygame.init()

    # Creates GameState object
    gs = GameState()

    # Generates list of valid moves both the AI and player are able to make at a given GameState
    valid_moves = gs.get_valid_moves()

    # Flag to determine if a move has been made
    move_made = False

    # Loads all images onto the board
    DrawAnimation.load_images()

    # Controls the frame rate at a given FPS
    clock = pygame.time.Clock()

    # Allows the Game loop to run
    run = True

    # tuple and list to indicate a starting and ending square when trying to move a piece
    # sq_selected - Tuple to indicated row and column of the piece a player would like to move
    # player_clicks - List to indicate the start and ending location of the piece being moved
    sq_selected = ()
    player_clicks = []

    # animates a chess move
    animate = False
    enable_animation = True

    # Game start variable to indicated when the game has started
    # Game over variable to indicated when the game is over
    game_start = False
    game_over = False

    # AI Flags
    # True - Human
    # False - AI
    player_one = True
    player_two = True

    # AI variables
    # AI_processing determines if the AI is calculating the best move
    # move_finder_process is the thread that performs the move calculations
    AI_processing = False
    move_finder_process = False

    # If a move was undone, then skips over the AI's turn to allow the human player to take their turn again
    move_undone = False

    # Move log font
    move_log_font = pygame.font.SysFont("Helvetica", 14, False, False)

    # Pass data between threads
    return_queue = Queue()

    # Controls the FPS of the game
    FPS = 10

    # Game loop
    while run:

        # Determines if it is the human players turn, not the AI
        human_turn = (gs.white_turn and player_one) or (not gs.white_turn and player_two)

        # Controls all events that occur either from keyboard or mouse clicks
        for event in pygame.event.get():

            # Terminates the game loop
            if event.type == pygame.QUIT:
                run = False

            # Gets all clicks performed on the screen
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Makes player move
                if not game_over:
                    sq_selected, player_clicks, move_made = player(gs, sq_selected, player_clicks,
                                                                   move_made, valid_moves, human_turn)
                    # Animates player move
                    if enable_animation:
                        animate = True

            # Gets all key presses
            if event.type == pygame.KEYDOWN:

                # Undoes moves
                if event.key == pygame.K_z:
                    if human_turn:
                        gs.undo_move()

                        # Undoes AI move
                        if not player_two:
                            gs.undo_move()
                        move_made = True
                        animate = False
                        game_over = False

                        # Terminates any threads that are in progress
                        if AI_processing:
                            move_finder_process.terminate()
                            AI_processing = False
                        move_undone = True

                # Resets game
                if event.key == pygame.K_r:

                    # Re-initialize the GameState
                    gs = GameState()

                    # Re-calculates all valid_moves at the beginning of the game
                    valid_moves = gs.get_valid_moves()
                    gs.white_turn = True

                    # Re-initialize mouse clicks
                    sq_selected = ()
                    player_clicks = []

                    # Resets move made and animations
                    move_made = False
                    animate = False

                    # Resets flag's for game start/over
                    game_over = False
                    game_start = False

                    # Terminates any threads that are in progress
                    if AI_processing:
                        move_finder_process.terminate()
                        AI_processing = False

                    # If AI is playing, reset move undone to allow AI to make moves again
                    move_undone = False

                    # Resets game back to Human vs Human
                    player_one = True
                    player_two = True
                    human_turn = True
                    gs.game_mode = "HVH"

                # Toggles Animations
                if event.key == pygame.K_a:
                    enable_animation = not enable_animation

                # Selects which game mode to play
                if not game_start:
                    # s - AI vs AI - Will infinitely be AI vs AI until code is added
                    if event.key == pygame.K_s:
                        player_one = False
                        player_two = False
                        gs.game_mode = "AVA"

                    # d - human vs AI
                    if event.key == pygame.K_d:
                        player_one = True
                        player_two = False
                        gs.game_mode = "HVA"

                    # f - human vs human
                    if event.key == pygame.K_f:
                        player_one = True
                        player_two = True
                        gs.game_mode = "HVH"

        # Make's AI moves
        if not game_over and not human_turn and not move_undone:
            move_made, AI_processing, move_finder_process = artificial_intel(gs, AI_processing, move_finder_process,
                                                                             return_queue, valid_moves, human_turn,
                                                                             move_made)
            # Animates AI moves
            if enable_animation:
                animate = True

        # Regenerates the next set of valid moves after a move was made
        if move_made:
            if animate:
                DrawAnimation.animate_move(gs.move_log[-1], gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            game_start = True
            move_undone = False

        # Redraws and updates all events that have occurred on the screen at a set FPS
        DrawAnimation.draw_game_state(gs, valid_moves, sq_selected, move_log_font)

        # End game conditions
        game_over = is_game_over(gs, game_over)

        # Controls FPS and updates any changes on the screen
        clock.tick(FPS)
        pygame.display.update()


"""
Calls driver code
"""

if __name__ == '__main__':
    main()
