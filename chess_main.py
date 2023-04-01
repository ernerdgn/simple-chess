"""
this part is responsible for user inputs and displaying current game state information
"""

import pygame as p
import chess_engine
#p.init()
WIDTH = HEIGHT = 512  #alternative: 400
DIMENSION = 8  #8*8 board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  #for the animations (maybe...)
IMAGES = {}

"""
initialize a global dictionary of images, this will be called just once in the main
"""

def load_images():
    pieces = ["bp", "wp", "bR", "wR", "bN", "wN", "bB", "wB", "bQ", "wQ", "bK", "wK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+ piece +".png"), (SQ_SIZE, SQ_SIZE))
    #we can get the image by typing something like: IMAGES["bQ"]

"""
main driver of the program, will be interested to user input and updating the board according to moves
"""

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()  #not for now
    screen.fill(p.Color("black"))
    game_state = chess_engine.gamestate()
    print(game_state.board)
    valid_moves = game_state.get_valid_moves()
    move_made = False  #flag variable for when a move is made
    load_images()  #will be done once
    running = True
    sq_selected = () #no square selected in the first place, will keep track of the LATEST input (tuple: (r, c))
    user_click = []  #keep track of user inputs (two tuples: [(7, 4), (5,4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #======================================== MOUSE ========================================#
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  #(x,y) locations of the mouse
                c = location[0] // SQ_SIZE
                r = location[1] // SQ_SIZE
                if sq_selected == (r,c): #if the user clicks the same square
                    sq_selected = ()  #deselecting
                    user_click = []  #deleting the data
                else:
                    sq_selected = (r,c)
                    user_click.append(sq_selected) #appened for first and second clicks
                if len(user_click) == 2:  #after the second click
                    move = chess_engine.Move(user_click[0], user_click[1], game_state.board)
                    print(move.get_chess_notation())
                    if move in valid_moves:
                        game_state.make_move(move)
                        move_made = True
                        sq_selected = ()  #reseting the user input
                        user_click = []  #likewise, if not: len(user_click) cannot be 2
                    else:  #if move is invalid
                        user_click = [sq_selected]


            #======================================== KEYBOARD ========================================#
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:  #for undo, press 'u'
                    game_state.undo_move()
                    move_made = True  #alternative: valid_moves = game_state.get_valid_moves()

        if move_made:
            valid_moves = game_state.get_valid_moves()
            move_made = False

        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()

"""
drawing the squares of board and pieces on them
"""

def draw_game_state(screen, game_state):
    draw_board(screen)  #this function draws the squares on the board
    draw_pieces(screen, game_state.board)
    #adding piece highlighting and possible move squares will be done later.. i hope

"""
drawing the squares
"""

def draw_board(screen):
    colors = [p.Color("white"), p.Color("dark gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row+column) % 2)]
            p.draw.rect(screen, color, p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
drawing the pieces
"""

def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":  #if not an empty square
                screen.blit(IMAGES[piece], p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
