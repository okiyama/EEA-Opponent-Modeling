### File: konane.py
### Classes defined: KonaneError, Konane, Player, SimplePlayer,
### RandomPlayer, HumanPlayer

import random
import copy

class KonaneError(AttributeError):
    """
    This class is used to indicate a problem in the konane game.
    """

class Konane:
    """
    This class implements Konane, the Hawaiian version of checkers.
    The board is represented as a two-dimensional list.  Each 
    location on the board contains one of the following symbols:
       'B' for a black piece
       'W' for a white piece
       '.' for an empty location
    The black player always goes first.  The opening moves by both
    players are special cases and involve removing one piece from
    specific designated locations.  Subsequently, each move is a
    jump over one of the opponent's pieces into an empty location.
    The jump may continue in the same direction, if appropriate.
    The jumped pieces are removed, and then it is the opponent's
    turn.  Play continues until one player has no possible moves,
    making the other player the winner. 
    """
    def __init__(self, n):
        self.size = n
        self.reset()
        self.GAs = 0
        
    def reset(self):
        """
        Resets the starting board state.
        """
        self.board = []
        value = 'B'
        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(value)
                value = self.opponent(value)
            self.board.append(row)
            if self.size%2 == 0:
                value = self.opponent(value)

    def __str__(self):
        return self.boardToStr(self.board)

    def boardToStr(self, board):
        """
        Returns a string representation of the konane board.
        """
        result = "  "
        for i in range(self.size):
            result += str(i) + " "
        result += "\n"
        for i in range(self.size):
            result += str(i) + " "
            for j in range(self.size):
                result += str(board[i][j]) + " "
            result += "\n"
        return result

    def valid(self, row, col):
        """
        Returns true if the given row and col represent a valid location on
        the konane board.
        """
        return row >= 0 and col >= 0 and row < self.size and col < self.size

    def contains(self, board, row, col, symbol):
        """
        Returns true if the given row and col represent a valid location on
        the konane board and that lcoation contains the given symbol.
        """
        return self.valid(row,col) and board[row][col]==symbol

    def countSymbol(self, board, symbol):
        """
        Returns the number of instances of the symbol on the board.
        """
        count = 0
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] == symbol:
                    count += 1
        return count

    def opponent(self, player):
        """
        Given a player symbol, returns the opponent's symbol, 'B' for black,
        or 'W' for white.
        """
        if player == 'B':
            return 'W'
        else:
            return 'B'

    def distance(self, r1, c1, r2, c2):
        """
        Returns the distance between two points in a vertical or
        horizontal line on the konane board.
        """
        return abs(r1-r2 + c1-c2)

    def makeMove(self, player, move):
        """
        Updates the current board with the next board created by the given
        move.
        """
        self.board = self.nextBoard(self.board, player, move)

    def nextBoard(self, board, player, move):
        """
        Given a move for a particular player from (r1,c1) to (r2,c2) this
        executes the move on a copy of the current konane board.  It will
        raise a KonaneError if the move is invalid. It returns the copy of
        the board, and does not change the given board.
        """
        r1 = move[0]
        c1 = move[1]
        r2 = move[2]
        c2 = move[3]
        next = copy.deepcopy(board)
        if not (self.valid(r1, c1) and self.valid(r2, c2)):
            raise KonaneError
        if next[r1][c1] != player:
            raise KonaneError
        dist = self.distance(r1, c1, r2, c2)
        if dist == 0:
            if self.openingMove(board):
                next[r1][c1] = "."
                return next
            raise KonaneError
        if next[r2][c2] != ".":
            raise KonaneError
        jumps = dist//2
        dr = (r2 - r1)//dist
        dc = (c2 - c1)//dist
        for i in range(jumps):
            if next[r1+dr][c1+dc] != self.opponent(player):
                raise KonaneError
            next[r1][c1] = "."
            next[r1+dr][c1+dc] = "."
            r1 += 2*dr
            c1 += 2*dc
            next[r1][c1] = player
        return next

    def openingMove(self, board):
        """
        Based on the number of blanks present on the konane board, determines
        whether the current move is the first or second of the game.
        """
        return self.countSymbol(board, ".") <= 1

    def generateFirstMoves(self, board):
        """
        Returns the special cases for the first move of the game.
        """
        moves = []
        moves.append([0]*4)
        moves.append([self.size-1]*4)
        moves.append([self.size/2]*4)
        moves.append([(self.size/2)-1]*4)
        return moves

    def generateSecondMoves(self, board):
        """
        Returns the special cases for the second move of the game, based
        on where the first move occurred.
        """
        moves = []
        if board[0][0] == ".":
            moves.append([0,1]*2)
            moves.append([1,0]*2)
            return moves
        elif board[self.size-1][self.size-1] == ".":
            moves.append([self.size-1,self.size-2]*2)
            moves.append([self.size-2,self.size-1]*2)
            return moves
        elif board[self.size/2-1][self.size/2-1] == ".":
            pos = self.size/2 -1
        else:
            pos = self.size/2
        moves.append([pos,pos-1]*2)
        moves.append([pos+1,pos]*2)
        moves.append([pos,pos+1]*2)
        moves.append([pos-1,pos]*2)
        return moves

    def check(self, board, r, c, rd, cd, factor, opponent):
        """
        Checks whether a jump is possible starting at (r,c) and going in the
        direction determined by the row delta, rd, and the column delta, cd.
        The factor is used to recursively check for multiple jumps in the same
        direction.  Returns all possible jumps in the given direction.
        """
        if self.contains(board,r+factor*rd,c+factor*cd,opponent) and \
           self.contains(board,r+(factor+1)*rd,c+(factor+1)*cd,'.'):
            return [[r,c,r+(factor+1)*rd,c+(factor+1)*cd]] + \
                   self.check(board,r,c,rd,cd,factor+2,opponent)
        else:
            return []

    def generateMoves(self, board, player):
        """
        Generates and returns all legal moves for the given player using the
        current board configuration.
        """
        if self.openingMove(board):
            if player=='B':
                return self.generateFirstMoves(board)
            else:
                return self.generateSecondMoves(board)
        else:
            moves = []
            rd = [-1,0,1,0]
            cd = [0,1,0,-1]
            for r in range(self.size):
                for c in range(self.size):
                    if board[r][c] == player:
                        for i in range(len(rd)):
                            moves += self.check(board,r,c,rd[i],cd[i],1,
                                                self.opponent(player))
            return moves

    def playOneGame(self, p1, p2, show):
        """
        Given two instances of players, will play out a game
        between them.  Returns 'B' if black wins, or 'W' if
        white wins. When show is true, it will display each move
        in the game.
        """
        self.reset()
        p1.initialize('B')
        p2.initialize('W')
        while 1:
            if show:
                print(self)
                print("player B's turn")
            move = p1.getMove(self.board)
            if move == []:
                result = 'W'
                break
            self.makeMove('B', move)
            if show:
                print(move)
                print()
                print(self)
                print("player W's turn")
            move = p2.getMove(self.board)
            if move == []:
                result = 'B'
                break
            self.makeMove('W', move)
            if show:
                print(move)
                print()
        if show:
            print("Game over")
        return result

    def playNGames(self, n, p1, p2, show):
        """
        Will play out n games between player p1 and player p2.
        The players alternate going first.  Prints the total
        number of games won by each player.
        """
        p1.reset()
        p2.reset()
        first = p1
        second = p2
        for i in range(n):
            print("Game", i)
            winner = self.playOneGame(first, second, show)
            if winner == 'B':
                first.won()
                print(first.name, "wins")
            else:
                second.won()
                print(second.name, "wins")
            temp = first
            first = second
            second = temp
        print(first.name, first.wins, second.name, second.wins)

    def playMatch(self, playerOne, playerTwo):
        """
        Will play a match between two players: Two games will always be played
        and a third will be played as a tie-breaker if neccesary.
        """
        pOneWins = 0
        pTwoWins = 0
        print(playerOne.name + " versus " + playerTwo.name)
        if self.playOneGame(playerOne, playerTwo, 0)=='B':
            print(playerOne.name + " wins game one.")
            pOneWins += 1
        else:
            print(playerTwo.name + " wins game one.")
            pTwoWins += 1
        if self.playOneGame(playerTwo, playerOne, 0)=='W':
            print(playerOne.name + " wins game two.")
            pOneWins += 1
        else: 
            print(playerTwo.name + " wins game two.")
            pTwoWins += 1
        if pOneWins==2:
            print(playerOne.name + " wins the match.")
            return 1
        if pTwoWins==2:
            print(playerTwo.name + " wins the match.")
            return 2
        if self.playOneGame(playerOne, playerTwo, 0)=='B':
            print(playerOne.name + " wins game three.")
            print(playerOne.name + " wins the match.")
            return 1
        else:
            print(playerTwo.name + " wins game three.")
            print(playerTwo.name + " wins the match.")
            return 2

    def randomTerm(self):
        random.seed()
        term = [(2*random.random())-1, False, False, False, False, False, False, False]
        term[random.randint(1,7)]=True
        return term

    def randomStrategy(self):
        strategy = []
        for x in range(1, random.randrange(2, 4)):
            strategy.append(self.randomTerm())
        return strategy

    def playRound(self, players):
        wins = []
        for player in players:
            player[0]=0
        for first in range(0, len(players)):
            for second in range(first+1, len(players)):
                winner = self.playMatch(players[first][1], players[second][1])
                if winner == 1:
                    players[first][0] += 1
                else:
                    players[second][0] += 1
        for vsRandom in range(0, len(players)):
            for x in range(0, len(players)):
                print(str(vsRandom) + " versus Random")
                winner = self.playMatch(players[vsRandom][1], RandomPlayer(6))
                if winner == 1:
                    players[vsRandom][0] += 1
        return players

    def rankings(self, players):
        for player in players:
            print(str(player[0]) + " - " + str(player[1]))

    def mutate(self, player):
        newStrategy = player.strategy
        mod = random.randrange(0, 3)
        print(str(mod))
        if (mod==0):
            modTerm = random.randrange(0, len(newStrategy))
            termMod = random.randrange(0,2)
            if termMod==0:
                newStrategy[modTerm][0] *= (2*random.random())-1
            if termMod==1:
                modVariable = random.randrange(1,5)
                newStrategy[modTerm][modVariable] = not newStrategy[modTerm][modVariable] 
        if (mod==1):
            newStrategy.pop()
        if (mod==2):
            newStrategy.append(self.randomTerm())
        self.GAs += 1
        return GAPlayer(6, str(self.GAs), newStrategy)

    def breedTerm(self, father, mother):
        newCo = (father[0]+mother[0])/2
        newStrategy = [newCo]
        for x in range(1, 8):
            parent = random.randrange(0, 2)
            if parent == 0:
                newStrategy.append(father[x])
            else:
                newStrategy.append(mother[x])
        return newStrategy

    def breedStrategy(self, father, mother):
        shared = min(len(father), len(mother))
        newStrat = []
        longer = []

        if len(father) > len(mother):
            longer = father
        else: 
            longer = mother

        for x in range(0, shared):
            newStrat.append(self.breedTerm(father[x], mother[x]))

        for x in range(shared, len(longer)):
            newStrat.append(longer[x])

        return newStrat

    def breedPlayer(self, father, mother):
        self.GAs += 1
        return GAPlayer(6, str(self.GAs), self.breedStrategy(father.strategy, mother.strategy))

    def gaTourny(self, participants):
        players = []
        for x in range(0, participants):
            players.append([0, GAPlayer(6, str(x), game.randomStrategy())])
        while True:
            players = self.playRound(players)
            players = sorted(players, key=lambda l:l[0], reverse=True)
            self.rankings(players)
            players.pop()
            players.pop()
            players.append([(players[0][0]+players[1][0])/2, self.breedPlayer(players[0][1], players[1][1])])
            players.append([players[0][0], self.mutate(players[0][1])])
            winnerfile = open('winner.txt', 'w')
            winnerfile.write(str(players[0][1]))
            winnerfile.close()
     

class Player:
    """
    A base class for Konane players.  All players must implement
    the the initialize and getMove methods.
    """
    name = "Player"
    wins = 0
    def won(self):
        self.wins += 1
    def reset(self):
        self.wins = 0
    def setSide(self, side):
        self.side = side
    def initialize(self, side):
        """
        Records the player's side, either 'B' for black or
        'W' for white.  Should also set the name of the player.
        """
        abstract()
    def getMove(self, board):
        """
        Given the current board, should return a valid move.
        """
        abstract()


class SimplePlayer(Konane, Player):
    """
    Always chooses the first move from the set of possible moves.
    """
    def initialize(self, side):
        self.side = side
        self.name = "Simple"
    def getMove(self, board):
        moves = self.generateMoves(board, self.side)
        n = len(moves)
        if n == 0:
            return []
        else:
            return moves[0]

class RandomPlayer(Konane, Player):
    """
    Chooses a random move from the set of possible moves.
    """
    def initialize(self, side):
        self.side = side
        self.name = "Random"
    def getMove(self, board):
        moves = self.generateMoves(board, self.side)
        n = len(moves)
        if n == 0:
            return []
        else:
            return moves[random.randrange(0, n)]

class FewestPlayer(Konane, Player):
    """
    Chooses the move which results in the opponent having the fewest moves.
    """
    def initialize(self, side):
        self.side = side
        self.name = "Fewest"
    
    def getMove(self, board):
        moves = self.generateMoves(board, self.side)
        if len(moves)==0:
            return []
        else:
            return min(moves, key=lambda move: len(self.generateMoves(self.nextBoard(board, self.side, move), self.opponent(self.side))))
 
class HumanPlayer(Player):
    """
    Prompts a human player for a move.
    """
    def initialize(self, side):
        self.side = side
        self.name = "Human"
    def getMove(self, board):
        (r1, c1, r2, c2) = eval(input("Enter r1, c1, r2, c2 (or -1's to concede): "))
        if r1 == -1:
            return []
        return [r1, c1, r2, c2]

        

class KOnane(Konane, Player):
    """
    Chooses moves based on a hyper-heuristic generated strategy
    """
    def __init__(self, size, depthlimit):
        Konane.__init__(self, size)
        self.limit = depthlimit

    def initialize(self, side):
        self.side = side
        self.name = "Konane AI from Github"

    def heuristic(self, board):
        return (0.174 * self.myMoves(board)) + (-0.437 * self.opponentMoves(board)) + 0.1807 

    def getMove(self, board):
        moves = self.generateMoves(board, self.side)
        if len(moves)==0:
            return []
        results = map(lambda move: tuple([self.minValue(self.nextBoard(board, self.side, move), 
                                                       self.limit-1, -9999, 9999), move]), moves)   
        return max(results)[1]

    def maxValue(self, board, depth, alpha, beta):
        moves = self.generateMoves(board, self.side)
        v = -9999
        if len(moves)==0:
            return []
        if (depth == 0):
            return self.heuristic(board)
        for move in moves:
            v = max(v, self.minValue(self.nextBoard(board, self.side, move), depth-1, alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def minValue(self, board, depth, alpha, beta):
        moves = self.generateMoves(board, self.opponent(self.side))
        v = 9999
        if len(moves)==0:
            return []
        if (depth == 0):
            return self.heuristic(board)
        for move in moves:
            v = min(v, self.maxValue(self.nextBoard(board, self.opponent(self.side), move), depth-1, alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def myMoves(self, board):
        return len(self.generateMoves(board, self.side))

    def opponentMoves(self, board):
        return len(self.generateMoves(board, self.opponent(self.side)))

    def myPieces(self, board):
        return self.countSymbol(board, self.side)

    def opponentPieces(self, board):
        return self.countSymbol(board, self.opponent(self.side))

    def myCorners(self, board):
        myPieces = 0
        if self.contains(board, 0, 0, self.side):
            myPieces += 1
        if self.contains(board, 0, self.size-1, self.side):
            myPieces += 1
        if self.contains(board, self.size-1, 0, self.side):
            myPieces += 1
        if self.contains(board, self.size-1, self.size-1, self.side):
            myPieces += 1
        return myPieces

    def oppCorners(self, board):
        oppPieces = 0
        if self.contains(board, 0, 0, self.opponent(self.side)):
            oppPieces += 1
        if self.contains(board, 0, self.size-1, self.opponent(self.side)):
            oppPieces += 1
        if self.contains(board, self.size-1, 0, self.opponent(self.side)):
            oppPieces += 1
        if self.contains(board, self.size-1, self.size-1, self.opponent(self.side)):
            oppPieces += 1
        return oppPieces

    def isFirstMove(self, board):
        if self.openingMove(board):
            return 1
        else:
            return 0


      
# class RevMini(MiniMaxPlayer):
#     def initialize(self, side):
#         self.side = side
#         self.name = "Reverse Heuristic"
#
#     def heuristic(self, board):
#         return -len(self.generateMoves(board, self.side))
#
#
# class PiecesMini(MiniMaxPlayer):
#     def initialize(self, side):
#         self.side = side
#         self.name = "Pieces Heuristic"
#
#     def heuristic(self, board):
#         return 2 * self.countSymbol(board, self.side)
#
# # Slightly better than PiecesMini; Slower than Minimax; Faster than RevMini
# class RevPiecesMini(MiniMaxPlayer):
#     def initialize(self, side):
#         self.side = side
#         self.name = "Rev Pieces Heuristic"
#
#     def heuristic(self, board):
#         return 2 * self.countSymbol(board, self.side)
#
# class GAPlayer(MiniMaxPlayer):
#     def initialize(self, side):
#         self.side = side
#
#     def __init__(self, size, name, strategy):
#         MiniMaxPlayer.__init__(self, size, 4)
#         self.name = name
#         self.strategy = strategy
#
#     def heuristic(self, board):
#         accum = 0
#         for term in self.strategy:
#             value = term[0]
#             if term[1]==True:
#                 value *=self.myMoves(board)
#             if term[2]==True:
#                 value *=self.opponentMoves(board)
#             if term[3]==True:
#                 value *=self.myPieces(board)
#             if term[4]==True:
#                 value *=self.opponentPieces(board)
#             if term[5]==True:
#                 value *=self.myCorners(board)
#             if term[6]==True:
#                 value *=self.oppCorners(board)
#             if term[7]==True:
#                 value *=self.isFirstMove(board)
#             accum += value
#         return accum
#
#     def myMoves(self, board):
#         return len(self.generateMoves(board, self.side))
#
#     def opponentMoves(self, board):
#         return len(self.generateMoves(board, self.opponent(self.side)))
#
#     def myPieces(self, board):
#         return self.countSymbol(board, self.side)
#
#     def opponentPieces(self, board):
#         return self.countSymbol(board, self.opponent(self.side))
#
#     def myCorners(self, board):
#         myPieces = 0
#         if self.contains(board, 0, 0, self.side):
#             myPieces += 1
#         if self.contains(board, 0, self.size-1, self.side):
#             myPieces += 1
#         if self.contains(board, self.size-1, 0, self.side):
#             myPieces += 1
#         if self.contains(board, self.size-1, self.size-1, self.side):
#             myPieces += 1
#         return myPieces
#
#     def oppCorners(self, board):
#         oppPieces = 0
#         if self.contains(board, 0, 0, self.opponent(self.side)):
#             oppPieces += 1
#         if self.contains(board, 0, self.size-1, self.opponent(self.side)):
#             oppPieces += 1
#         if self.contains(board, self.size-1, 0, self.opponent(self.side)):
#             oppPieces += 1
#         if self.contains(board, self.size-1, self.size-1, self.opponent(self.side)):
#             oppPieces += 1
#         return oppPieces
#
#     def isFirstMove(self, board):
#         if self.openingMove(board):
#             return 1
#         else:
#             return 0
#
#     def getStrategy(self):
#         return self.strategy
#
#     def __str__(self):
#         return self.name + ":" + str(self.strategy)
#
#
# #class JumpMini(MiniMaxPlayer):
# #    def initialize(self, side):
# #        self.side = side
# #        self.name = "Jump Heuristic"
# #
# #    def heuristic(self, board):
# #        if #checkforjump:
# #            return 2 * len(self.generateMoves(board, self.side))
# #        else:
# #            return len(self.generateMoves(board, self.side))
#
# game = Konane(6)
#
# game.gaTourny(4)
