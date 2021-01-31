import os, copy

class Game():
    def __init__(self):
        self.__board = [[" "," "," "],[" "," "," "],[" "," "," "]]
        self.__winner = None
        self.__gameState = "X" # X, O, end
        self.__control = Engine()
        self.__aiTurn = None
        self.__computer = None

    @property
    def board(self):
        return self.__board

    @board.setter
    def board(self, value):
        self.__board = value

    @property
    def winner(self):
        return self.__winner

    @winner.setter
    def winner(self, value):
        self.__winner = value

    @property
    def gameState(self):
        return self.__gameState

    @gameState.setter
    def gameState(self, value):
        self.__gameState = value

    @property
    def control(self):
        return self.__control

    @control.setter
    def control(self, value):
        self.__control = value

    @property
    def aiTurn(self):
        return self.__aiTurn

    @aiTurn.setter
    def aiTurn(self, value):
        self.__aiTurn = value

    @property
    def computer(self):
        return self.__computer

    @computer.setter
    def computer(self, value):
        self.__computer = value

    def runGame(self, start, prune, monitor):
        self.aiSetup(start, prune, monitor)

        while self.gameState == "X" or self.gameState == "O":
            if self.aiTurn == True:
                self.setPiece(self.computer.passMove(self))
                self.control.renderFrame(self)
            else:
                self.control.renderFrame(self)
                self.setPiece(self.control.passInput(self))
            self.evaluateBoard()

        self.control.renderFrame(self)
        self.control.renderEndGame(self)

    def setPiece(self, coords):
        self.board[coords[0]][coords[1]] = self.gameState
        self.changePlayer()
    
    def evaluateBoard(self):
        winner = self.checkWinner()

        if winner == "X" or winner == "O":
            self.changeState("win")
        elif self.checkPossibleMoves() != 0:
            self.changeState("pass")
        else:
            self.changeState("draw")

    def checkPossibleMoves(self):
        cnt = 0

        for row in self.board:
            for cell in row:
                if cell == " ":
                    cnt += 1
        
        return cnt


    def checkDiagonal(self):
        if (self.board[0][0] == self.board[1][1] and self.board[0][0] == self.board[2][2]) or (self.board[0][2] == self.board[1][1] and self.board[2][0] == self.board[1][1]):
            return self.board[1][1]
        else:
            return ""

    def checkRowsColums(self):
        if (self.board[0][0] == self.board[0][1] and self.board[0][0] == self.board[0][2]) or (self.board[0][0] == self.board[1][0] and self.board[0][0] == self.board[2][0]):
            return self.board[0][0]
        elif (self.board[1][0] == self.board[1][1] and self.board[1][0] == self.board[1][2]) or (self.board[0][1] == self.board[1][1] and self.board[2][1] == self.board[1][1]):
            return self.board[1][1]
        elif (self.board[2][2] == self.board[2][1] and self.board[2][0] == self.board[2][2]) or (self.board[0][2] == self.board[1][2] and self.board[2][2] == self.board[1][2]):
            return self.board[2][2]
        else:
            return ""

    def checkWinner(self):
        diag = self.checkDiagonal()
        rnc = self.checkRowsColums()

        if diag != "":
            return diag
        elif rnc != "":
            return rnc
        else:
            return ""
        
    def changePlayer(self):
        if self.aiTurn:
            self.aiTurn = False
        else:
            self.aiTurn = True

    def changeState(self, value):
        if self.gameState == "X":
            if value == "pass":
                self.gameState = "O"
            elif value == "win":
                self.winner = "X"
                self.gameState = "end"
            else:
                self.winner = ""
                self.gameState = "end"
        else:
            if value == "pass":
                self.gameState = "X"
            elif value == "win":
                self.winner = "O"
                self.gameState = "end"

    def aiSetup(self, start, prune, monitor):
        self.computer = AI(prune, monitor)

        if start:
            self.aiTurn = True
        else:
            self.aiTurn = False

    def runSim(self, start, prune, monitor, board):
        self.setGameState(board)
        self.runGame(start, prune, monitor)

    def setGameState(self, board):
        self.board = copy.deepcopy(board)
        cnt = 0

        for row in board:
            for cell in row:
                if cell == " ":
                    cnt += 1
        
        if not cnt:
            self.winner = self.checkWinner()
            self.gameState = "end"
        elif cnt%2 + 1 == 0:
            self.gameState = "O"
        else:
            self.gameState = "X"

    def checkCellAvailable(self, t):
        if self.board[t[0]][t[1]] == ' ':
            return True
        else:
            return False

    def boardStateOutput(self):
        output = ''

        for i in range(0,3):
            for j in range(0,3):
                output += f'|{self.board[i][j]}'
            output += '|\n'

        return output

    def endGameOutput(self):
        if self.winner == 'X':
            return "X is the winner!"
        if self.winner == 'O':
            return "O is the winner!"
        else:
            return "Game is a draw!"

class AI():
    def __init__(self, prune, monitor):
        self.__prune = prune
        self.__monitor = monitor

    @property
    def prune(self):
        return self.__prune
    
    @property
    def monitor(self):
        return self.__monitor

    def passMove(self, game):
        coordsList = list()
        alpha, beta = -2, 2

        for i in range(0,3):
            for j in range(0,3):
                if game.board[i][j] == " ":
                    coords = [i,j]
                    passToEval = copy.deepcopy(game)
                    passToEval.setPiece(coords)

                    if self.prune:
                        ev = self.minimaxWithPruning(passToEval, alpha, beta)
                        coordsList.append((coords, ev))
                        alpha = max(ev, alpha)
                        beta = min(ev, beta)

                        if beta <= alpha:
                            break
                    else:
                        ev = self.minimax(passToEval)
                        coordsList.append((coords, ev))
        
        coordsList = sorted(coordsList, key=lambda x:x[1])
        return coordsList[0][0]
    
    def minimax(self, game):
        game.evaluateBoard()

        if self.monitor:
            print(game.boardStateOutput() + f'Turn to play:{game.aiTurn}, Game state:{game.gameState}, Winner: {game.winner}\n')
            input("Pritisnite enter za nastavak!")

        if game.gameState == "end":
            if game.winner == '':
                return 0
            elif game.aiTurn:
                return 1
            else:
                return -1
        
        if game.aiTurn:
            maxEval = -1

            for i in range(0,3):
                for j in range(0,3):
                    if game.board[i][j] == " ":
                        passToEval = copy.deepcopy(game)
                        passToEval.setPiece((i,j))
                        ev = self.minimax(passToEval)
                        maxEval = max(ev, maxEval)
            
            return maxEval
        else:
            minEval = 1

            for i in range(0,3):
                for j in range(0,3):
                    if game.board[i][j] == " ":
                        passToEval = copy.deepcopy(game)
                        passToEval.setPiece((i,j))
                        ev = self.minimax(passToEval)
                        minEval = min(ev, minEval)
            
            return minEval

    def minimaxWithPruning(self, game, alpha, beta):
        game.evaluateBoard()

        if self.monitor:
            print(game.boardStateOutput() + f'Turn to play:{game.aiTurn}, Game state:{game.gameState}, Winner: {game.winner}, Alpha:{alpha}, Beta:{beta}\n')
            input("Pritisnite enter za nastavak!")

        if game.gameState == "end":
            if game.winner == '':
                return 0
            elif game.aiTurn:
                return 1
            else:
                return -1
        
        if game.aiTurn:
            maxEval = -1

            for i in range(0,3):
                for j in range(0,3):
                    if game.board[i][j] == " ":
                        passToEval = copy.deepcopy(game)
                        passToEval.setPiece((i,j))
                        ev = self.minimaxWithPruning(passToEval, alpha, beta)
                        maxEval = max(ev, maxEval)

                        alpha = max(ev, alpha)
                        if beta <= alpha:
                            break
            return maxEval
        else:
            minEval = 1

            for i in range(0,3):
                for j in range(0,3):
                    if game.board[i][j] == " ":
                        passToEval = copy.deepcopy(game)
                        passToEval.setPiece((i,j))
                        ev = self.minimaxWithPruning(passToEval, alpha, beta)
                        minEval = min(ev, minEval)

                        alpha = min(ev, beta)
                        if beta <= alpha:
                            break
            return minEval

class Engine():
    def renderFrame(self, game):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(game.boardStateOutput())

    def renderEndGame(self, game):
        print(game.endGameOutput())
        input("Stisnite enter za nastavak!")

    def passInput(self, game):
        while True:
            i, j = [int(i) for i in input("Unesite koordinate: ").split(", ")]

            if game.checkCellAvailable((i, j)):
                break

        return [i, j]

if __name__ == "__main__":
    game = Game()
    #game.runGame(False, False, False)
    game.runSim(False, True, True, [['O', ' ', 'X'], ['X', ' ', ' '], ['X', 'O', 'O']])
