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
    animate = False #flag variable for when we should animate a move

    load_images() #only do this once
    running = True
    sqSelected = () #no square is selected initially. Will keep track of last click of user. Type (row, column)
    playerClicks = [] #keep track of player clicks (two tuples: [(6,4), (4,4)])
    
    gameOver = False #flag for whenever 
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN: #could add click and drag later
                if not gameOver:
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
                                animate = True
                                sqSelected = () #reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r: #reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        
        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')

        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen, gs, validMoves, sqSelected, moveLog):
    '''
    Highlight square selected and moves available for selected piece. Highlights possible captures in red.

    Implement feature to highlight last move made
    '''
    surface = p.Surface((SQ_SIZE, SQ_SIZE))
    surface.set_alpha(100)
    if len(moveLog) != 0:
        surface.fill(p.Color('green')) #highlight previous move in green
        lastMove = moveLog[-1]
        screen.blit(surface, (lastMove.startCol * SQ_SIZE, lastMove.startRow * SQ_SIZE))
        screen.blit(surface, (lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE))

    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'): #making sure that square selected is piece that can be moved
            #highlight selected square
            surface.fill(p.Color('blue'))
            screen.blit(surface, (col * SQ_SIZE, row * SQ_SIZE))
            #highlight moves from that square
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    if (gs.board[move.endRow][move.endCol][0] == ('b' if gs.whiteToMove else 'w')) or move.isEnPassantMove: #if move would capture a piece, highlight red
                        squareColor = 'red'
                        surface.fill(p.Color(squareColor))
                        screen.blit(surface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
                    else:
                        squareColor = 'yellow' #otherwise, highlight yellow
                        surface.fill(p.Color(squareColor))
                        screen.blit(surface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    '''
    Responsible for all graphics within current game state
    '''

    drawBoard(screen) #draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected, gs.moveLog)
    drawPieces(screen, gs.board) #draw pieces

def drawBoard(screen):
    '''
    Draw the squares on the board. Top left square is always light.
    '''
    global colors
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


def animateMove(move, screen, board, clock):
    '''
    Fairly inefficient move animation, going to redraw the entire board each time instead of just the area that is changing.
    '''
    global colors
    
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5 #frames to move one square

    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        row, col = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()