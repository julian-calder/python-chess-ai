import random 

#white trying to make score as positive as possible, black as negative as possible

pieceScore = {'K': 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

def findRandomMove(validMoves):
    '''
    Picks and returns a random move.
    '''
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove(gs, validMoves):
    '''
    Find best move based on material alone, looking two tiers in
    '''
    turnMultiplier = 1 if gs.whiteToMove else -1

    opponentMinMaxScore = CHECKMATE #want to find the smallest score of opponents maximum
    bestPlayerMove = None
    random.shuffle(validMoves)


    for playerMove in validMoves: #tries to make best move based on maximizing total number of points on board
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate: 
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE #find opponents best move in the state I give them
            for opponentMove in opponentsMoves:
                gs.makeMove(opponentMove)
                gs.getValidMoves() #this is inefficient but necessary for the subsequent steps
                if gs.checkmate:
                    score = CHECKMATE
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

def findBestMoveMinMax(gs, validMoves):
    '''
    Helper method to make first recursive call
    '''
    global nextMove
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    '''
    Depth represents how many levels of recursion you will look
    '''
    global nextMove
    if depth == 0: #at the deepest you want to go
        return scoreMaterial(gs.board)
    
    random.shuffle(validMoves)

    if whiteToMove: # trying to maximize
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False) #False indicating not whiteToMove
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

    


def scoreBoard(gs):
    '''
    Positive score from this is good for white, negative score is good for black
    '''
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    
    elif gs.stalemate:
        return STALEMATE


    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score


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