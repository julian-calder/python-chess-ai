import random 

#white trying to make score as positive as possible, black as negative as possible

pieceScore = {'K': 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0

def findRandomMove(validMoves):
    '''
    Picks and returns a random move.
    '''
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove(gs, validMoves):
    '''
    Find best move based on material alone (Greedy Algorithm)
    '''
    turnMultiplier = 1 if gs.whiteToMove else -1

    opponentMinMaxScore = CHECKMATE #want to find the smallest score of opponents maximum
    bestPlayerMove = None
    random.shuffle(validMoves)


    for playerMove in validMoves: #tries to make best move based on maximizing total number of points on board
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()

        opponentMaxScore = -CHECKMATE #find opponents best move in the state I give them
        for opponentMove in opponentsMoves:
            gs.makeMove(opponentMove)
            if gs.checkmate:
                score = -turnMultiplier * CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore: #minimization part of algorithm
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove 
        gs.undoMove()

    return bestPlayerMove

def scoreMaterial(board):
    '''
    Score the board based on material
    '''
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score