'''
This is how we will store everything about current state of chess game.

Also responsible for determining valid moves. Will also maintain move log.
'''
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

    def makeMove(self, move):
        '''
        Takes move as a parameter and executes it. Note: will not work for castling,
        pawn promotion, and en passant
        '''
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved #assume move is already valid
        self.moveLog.append(move) #log move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players

    def undoMove(self):
        '''
        Undo the last move made
        '''
        if len(self.moveLog) != 0: #make sure move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured

            self.whiteToMove = not self.whiteToMove #switch turns back

    def getValidMoves(self):
        '''
        All moves considering checks
        '''
        return self.getAllPossibleMoves()

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
        if self.whiteToMove: #white pawn moves
            if self.board[row - 1][col] == '--': #pawn single advance
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == '--': #pawn double advance
                    moves.append(Move((row, col), (row - 2, col), self.board))
            #captures
            if (col - 1) >= 0: #captures to the left
                if self.board[row - 1][col - 1][0] == 'b': #black piece to capture
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if (col + 1) <= 7: #captures to the right
                if self.board[row - 1][col + 1][0] == 'b': #black piece to capture
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
        
        else: #black pawn moves
            if self.board[row + 1][col] == '--': #pawn single advance
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == '--': #pawn double advance
                    moves.append(Move((row, col), (row + 2, col), self.board))
            #captures
            if (col - 1) >= 0: #captures to the left
                if self.board[row + 1][col - 1][0] == 'w': #white piece to capture
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if (col + 1) <= 7: #captures to the right
                if self.board[row + 1][col + 1][0] == 'w': #white piece to capture
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))

        #add pawn promotions later

    def getRookMoves(self, row, col, moves):
        '''
        Get all the rook moves for the rook located at row, col and add these moves to the list
        '''
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up, left, down, right
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
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
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, 2), (1, -2), (2, 1), (2, -1))
        allyColor = 'w' if self.whiteToMove else 'b'

        for move in knightMoves:
            endRow = row + move[0]
            endCol = col + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not friendly piece (enemy or empty)
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    def getBishopMoves(self, row, col, moves):
        '''
        Get all the bishop moves for the bishop located at row, col and add these moves to the list
        '''
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # top left, top right, bottom left, bottom right
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
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
                    moves.append(Move((row, col), (endRow, endCol), self.board))




class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]  #this isn't necessary
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol] #might be an empty square and that's ok

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

