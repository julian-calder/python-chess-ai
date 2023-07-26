'''
This is the main driver file, for user input and GameState object
'''

import pygame as p  
import ChessEngine

p.init()

WIDTH = HEIGHT = 512 #could also do 400 here
DIMENSION = 8 #dimensions of board are 8 x 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #for animations later
IMAGES = {}


def load_images():
    '''
    Initialize a global dictionary of images. This will be called one time in the main
    '''

    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #Note: we can access an image by saying 'IMAGES['wp']'



def main():
    '''
    Main driver for our code. Will handle user input and updating graphics
    '''

    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()

    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made

    load_images() #only do this once
    running = True
    sqSelected = () #no square is selected initially. Will keep track of last click of user. Type (row, column)
    playerClicks = [] #keep track of player clicks (two tuples: [(6,4), (4,4)])
    
    
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN: #could add click and drag later
                location = p.mouse.get_pos() #(x, y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                
                if sqSelected == (row, col): #the user clicked the same square twice
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) #append for both first and second clicks

                if len(playerClicks) == 2: #after second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())

                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = () #reset user clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]

            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    '''
    Responsible for all graphics within current game state
    '''

    drawBoard(screen) #draw squares on the board
    #could later implement piece highlighting or move suggestions
    drawPieces(screen, gs.board) #draw pieces 

def drawBoard(screen):
    '''
    Draw the squares on the board. Top left square is always light.
    '''
    colors = [p.Color('white'), p.Color('gray')]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    '''
    Draw pieces on the board using current GameState.board variable
    '''
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != '--': #not empty square
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()