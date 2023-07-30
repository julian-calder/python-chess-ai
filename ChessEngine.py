'''
This is how we will store everything about current state of chess game.

Also responsible for determining valid moves. Will also maintain move log.
'''

import copy

class GameState():
    def __init__(self):
        '''
        Consider using a numpy array to improve efficiency.

        Board is 8x8 2-D list, each element in list has 2 characters.
        First character represents color of the piece, 'b' or 'w'

        Second character represents type of piece, 'K', 'Q', 'R', 'B', 'N', or 'p'

        '--' represents an empty space
        '''
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []

        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.inCheck = False
        self.pins = []
        self.checks = []

        self.checkMate = False
        self.staleMate = False

        self.enPassantPossible = () #coordinates for square where enpassant capture is possible
        
        self.currentCastlingRights = CastleRights(True, True, True, True)

        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]



    def makeMove(self, move):
        '''
        Takes move as a parameter and executes it.
        '''
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved #assume move is already valid
        self.moveLog.append(move) #log move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players

        #update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            promotedPiece = input("Promote to Q, R, B, or N: ") 
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

        #en passant move
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--' #capturing the pawn

        #update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enPassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] #moves the rook
                self.board[move.endRow][move.endCol + 1] = '--' #erase old rook
            else: #queenside castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] # moves the rook
                self.board[move.endRow][move.endCol - 2] = '--' #erase old rook

        #update castling rights - whenever rook or king moves
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))


    def undoMove(self):
        '''
        Undo the last move made
        '''
        if len(self.moveLog) != 0: #make sure move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured

            self.whiteToMove = not self.whiteToMove #switch turns back

            #update King's position if necessary
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            #undo en passant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = '--' #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)

            #undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()
        
            #undo castling rights
            self.castleRightsLog.pop() #get rid of new castle rights from move we are undoing
            castle_rights = copy.deepcopy(self.castleRightsLog[-1])
            self.currentCastlingRights = castle_rights

            #undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else: #queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'


    def updateCastleRights(self, move):
        '''
        Update castle rights given the move
        '''
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRights.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRights.bks = False
        
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0: #left rook
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7: #right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0: #left rook
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7: #right rook
                    self.currentCastlingRights.bks = False


    def getValidMoves(self):
        '''
        Returns all moves considering checks
        '''
        moves = []

        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1: #only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                #to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]

                pieceChecking = self.board[checkRow][checkCol] #enemy piece causing check
                validSquares = [] #squares that piece can move into
                #if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                
                #get rid of any moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K': #move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doesn't block check or capture piece
                            moves.remove(moves[i])
            else: #if double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: #not in check, all moves valid
            moves = self.getAllPossibleMoves()

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves, 'w')
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves, 'b')

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves
    
    def checkForPinsAndChecks(self):
        '''
        Returns if player is in check, a list of pins, and a list of checks
        '''
        pins = [] #places where allied pin piece is and direction that it is pinned from
        checks = [] #squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        #check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): #first allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #second allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5 possibilities here if you hit an enemy piece
                        #1. away along axes and it is a rook
                        #2. diagonally from king and it is a bishop
                        #3. 1 square away diagonally and it is a pawn
                        #4. any direction and it is a queen
                        #5. any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == 'K'):
                                if possiblePin == (): #no piece blocking, so check
                                    inCheck = True
                                    checks.append((endRow, endCol, d[0], d[1]))
                                    break
                                else: #piece blocking so pin
                                    pins.append(possiblePin)
                                    break
                        else: #enemy piece not applying check
                            break
                else:
                    break #off board
        #check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, 2), (1, -2), (2, 1), (2, -1))

        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': #enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, move[0], move[1]))

        return inCheck, pins, checks        

    def getAllPossibleMoves(self):
        '''
        All moves without considering checks
        '''
        moves = []
        for row in range(len(self.board)): #number of rows
            for col in range(len(self.board[row])): #number of columns in given row
                turn = self.board[row][col][0] #could improve efficiency of this
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)
        return moves
    
    def getPawnMoves(self, row, col, moves):
        '''
        Get all the pawn moves for the pawn located at row, col and add these moves to the list
        '''
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
        isPawnPromotion = False

        #advances
        if self.board[row + moveAmount][col] == '--':
            if not piecePinned or pinDirection == (moveAmount, 0):
                if row + moveAmount == backRow: #if piece gets to back rank then it is pawn promotion
                    pawnPromotion = True
                moves.append(Move((row, col), (row + moveAmount, col), self.board, isPawnPromotion = isPawnPromotion))
                if row == startRow and self.board[row + 2 * moveAmount][col] == '--': #2 square move
                    moves.append(Move((row, col), (row + 2 * moveAmount, col), self.board))

        #captures
        if col - 1 >= 0: #capture to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][col - 1][0] == enemyColor:
                    if row + moveAmount == backRow: #if piece gets to back rank then it is pawn promotion
                        pawnPromotion = True
                    moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, isPawnPromotion = isPawnPromotion))
                if (row + moveAmount, col - 1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, isEnPassantMove = True))

        if col + 1 <= 7: #capture to the right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[row + moveAmount][col + 1][0] == enemyColor:
                    if row + moveAmount == backRow: #if piece gets to back rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, isPawnPromotion = isPawnPromotion))
                if (row + moveAmount, col + 1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, isEnPassantMove = True))



    def getRookMoves(self, row, col, moves):
        '''
        Get all the rook moves for the rook located at row, col and add these moves to the list
        '''
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = self.pins[i][2], self.pins[i][3]
                if self.board[row][col][i] != 'Q': #can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up, left, down, right
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': #moving to empty space
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #capturing enemy piece
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break #stop checking direction if we get to enemy piece
                        else: #encountering friendly piece
                            break 
                else: #off board
                    break            

    def getKnightMoves(self, row, col, moves):
        '''
        Get all the knight moves for the knight located at row, col and add these moves to the list
        '''
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, 2), (1, -2), (2, 1), (2, -1))
        allyColor = 'w' if self.whiteToMove else 'b'

        for move in knightMoves:
            endRow = row + move[0]
            endCol = col + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #not friendly piece (enemy or empty)
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def getBishopMoves(self, row, col, moves):
        '''
        Get all the bishop moves for the bishop located at row, col and add these moves to the list
        '''
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # top left, top right, bottom left, bottom right
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': #moving to empty space
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #capturing enemy piece
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break #stop checking direction if we get to enemy piece
                        else: #encountering friendly piece
                            break 
                else: #off board
                    break    

    def getQueenMoves(self, row, col, moves):
        '''
        Get all the queen moves for the queen located at row, col and add these moves to the list
        '''
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        '''
        Get all the king moves for the king located at row, col and add these moves to the list
        '''
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'

        for i in range(8):
            endRow = row + kingMoves[i][0]
            endCol = col + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] !=  allyColor: #not friendly (empty or enemy)
                    #place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()

                    if not inCheck:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    
                    #place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

    def getCastleMoves(self, row, col, moves, allyColor):
        '''
            Generate all valid castle moves for the king at (row, col) and add them to the list of moves
        '''
        inCheck, pins, checks = self.checkForPinsAndChecks()
        if inCheck:
            return #can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(row, col, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(row, col, moves, allyColor)

    def getKingsideCastleMoves(self, row, col, moves, allyColor):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if allyColor == 'w':
                self.whiteKingLocation = (row, col + 1)             #inefficient code, but this checks if squares being moved into would result in a check
                inCheck, pins, checks = self.checkForPinsAndChecks()
                if not inCheck:
                    self.whiteKingLocation = (row, col + 2)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))
            else:
                self.blackKingLocation = (row, col + 1)
                inCheck, pins, checks = self.checkForPinsAndChecks()
                if not inCheck:
                    self.blackKingLocation = (row, col + 2)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, row, col, moves, allyColor):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if allyColor == 'w':
                self.whiteKingLocation = (row, col - 1)             #inefficient code, but this checks if squares being moved into would result in a check
                inCheck, pins, checks = self.checkForPinsAndChecks()
                if not inCheck:
                    self.whiteKingLocation = (row, col - 2)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))
            else:
                self.blackKingLocation = (row, col - 1)
                inCheck, pins, checks = self.checkForPinsAndChecks()
                if not inCheck:
                    self.blackKingLocation = (row, col - 2)
                    inCheck, pins, checks = self.checkForPinsAndChecks
                    if not inCheck:
                        moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))


class CastleRights(): #stores current state of castling rights
    def __init__(self, white_kingside, black_kingside, white_queenside, black_queenside):
        self.wks = white_kingside
        self.bks = black_kingside
        self.wqs = white_queenside
        self.bqs = black_queenside


class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isPawnPromotion = False, isEnPassantMove = False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]  #this isn't necessary
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol] #might be an empty square and that's ok

        #pawn promotion
        self.isEnPassantMove = isEnPassantMove
        self.isPawnPromotion = isPawnPromotion

        #en passant
        if isEnPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        #castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #creates unique move ID

    def __eq__(self, other):
        '''
        Overriding the equals method
        '''
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]

