"""
File: konane.py
Classes defined: KonaneError, Konane, Player, SimplePlayer,
RandomPlayer, HumanPlayer

New feature: See the SimplePlayer class for an example of how to limit
the time that a method will run.  For the Konane tournament, your
minimax player's getMove method must run within 5 seconds.  Notice how
the getMove method is called within the playOneGame method.  If the
getMove method times out, then a random move is chosen instead.

Bug fix: When doing multiple inheritance in the player classes,
must explicitly initialize the second base class.
"""

import random
import copy
from time import sleep

def log(string):
    #We really don't need to log this
    pass

class KonaneError(AttributeError):
    """
    This class is used to indicate a problem in the konane game.
    """

class Konane:
    """
    This class implements Konane, the Hawaiian version of checkers.
    The board is represented as a two-dimensional list.	 Each
    location on the board contains one of the following symbols:
       'B' for a black piece
       'W' for a white piece
       '.' for an empty location
    The black player always goes first.	 The opening moves by both
    players are special cases and involve removing one piece from
    specific designated locations.	Subsequently, each move is a
    jump over one of the opponent's pieces into an empty location.
    The jump may continue in the same direction, if appropriate.
    The jumped pieces are removed, and then it is the opponent's
    turn.  Play continues until one player has no possible moves,
    making the other player the winner.
    """
    def __init__(self, n):
        self.size = n
        self.reset()

    def reset(self):
        """
        Resets the starting board state.
        """
        self.board = []
        value = 'B'
        for i in xrange(self.size):
            row = []
            for j in xrange(self.size):
                row.append(value)
                value = self.opponent(value)
            self.board.append(row)
            if self.size%2 == 0:
                value = self.opponent(value)

    def __str__(self):
        result = "	"
        for i in xrange(self.size):
            result += str(i) + " "
        result += "\n"
        for i in xrange(self.size):
            result += str(i) + " "
            for j in xrange(self.size):
                result += str(self.board[i][j]) + " "
            result += "\n"
        return result

    def valid(self, row, col):
        """
        Returns true if the given row and col represent a valid location on
        the konane board.
        """
        #return row >= 0 and col >= 0 and row < self.size and col < self.size
        return 0 <= row < self.size and 0 <= col < self.size

    def contains(self, board, row, col, symbol):
        """
        Returns true if the given row and col represent a valid location on
        the konane board and that location contains the given symbol.
        """
        #return self.valid(row,col) and board[row][col]==symbol
        return 0 <= row < self.size and 0 <= col < self.size and board[row][col] == symbol

    # TODO: This is O(n^2), we can cache this
    def countSymbol(self, board, symbol):
        """
        Returns the number of instances of the symbol on the board.
        """
        count = 0
        for row in board:
            for val in row:
                if val == symbol:
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
        horizontal line on the konane board. Diagonal jumps are NOT
        allowed.
        """
        return abs(r1-r2 + c1-c2)

    def makeMove(self, player, move):
        """
        Updates the current board with the next board created by the given
        move.
        """
        # TODO: Why are we copying the board
        self.board = self.nextBoard(self.board, player, move)

    def boardCopy(self, board):
        # NOTE: "row[:]" means copy the row into a new list
        return [row[:] for row in board]

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
        next = self.boardCopy(board)
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
        jumps = dist/2
        dr = (r2 - r1)/dist
        dc = (c2 - c1)/dist
        for i in xrange(jumps):
            if next[r1+dr][c1+dc] != self.opponent(player):
                raise KonaneError
            next[r1][c1] = "."
            next[r1+dr][c1+dc] = "."
            r1 += 2*dr
            c1 += 2*dc
            next[r1][c1] = player
        return next

    def openingMove(self, board):
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

    def check(self, board, r, c, rd, cd, factor, opponent, moves=None):
        """
        Checks whether a jump is possible starting at (r,c) and going
        in the direction determined by the row delta, rd, and the
        column delta, cd.  The factor is used to check for
        multiple jumps in the same direction.  Returns all possible
        jumps in the given direction.
        """
        # NOTE: This version is no longer recursive. It maintains the old interface,
        #       but enables a slightly faster technique - passing your current 'moves'
        #       list in as an additional parameter makes it do the list extension for you,
        #       and somewhat faster.

        if moves is None:
            moves = []

        contains = self.contains
        append = moves.append
        scaledRD = factor*rd
        scaledCD = factor*cd

        nextR = r + scaledRD
        nextC = c + scaledCD
        while contains(board, nextR, nextC, opponent):
            targetR = nextR + scaledRD
            targetC = nextC + scaledCD
            if contains(board, targetR, targetC, '.'):
                append([r, c, targetR, targetC])
                nextR = targetR + scaledRD
                nextC = targetC + scaledCD
            else:
                break

        return moves

    def generateMoves(self, board, player):
        """
        Generates and returns all legal moves for the given player
        using the current board configuration.
        """
        if self.openingMove(board):
            if player=='B':
                return self.generateFirstMoves(board)
            else:
                return self.generateSecondMoves(board)
        else:
            moves = []
            mv = [(0,-1),(-1,0),(0,1),(1,0)]
            # TODO: Optimize! Loop for pieces owned by each player, instead of looking for them
            check = self.check
            opponent = self.opponent(player)

            # NOTE: enumerate() steps over both the indices and the values in a list
            for r, row in enumerate(board):
                for c, val in enumerate(row):
                    if val == player:
                        for mvR, mvC in mv:
                            check(board,r,c,mvR,mvC,1,
                                  opponent, moves)
            return moves

    def countMovablePieces(self, board, player):
        """
        Generates and returns all legal moves for the given player
        using the current board configuration.
        """
        if self.openingMove(board):
            if player=='B':
                return len(self.generateFirstMoves(board))
            else:
                return len(self.generateSecondMoves(board))
        else:
            count = 0
            rd = [-1,0,1,0]
            cd = [0,1,0,-1]
            for r in range(self.size):
                for c in range(self.size):
                    if board[r][c] == player:
                        for i in range(len(rd)):
                            if (self.check(board,r,c,rd[i],cd[i],1,
                                           self.opponent(player)) != []):
                                count += 1
                                break
            return count


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
        #		log = open(p1.name + "vs" + p2.name + ".log", "w")
        log(p1.name + " vs " + p2.name +"\n")
        #print p1.name, "vs", p2.name
        while True:
            log(str(self))
            log("\nplayer B's turn\n")
            if show:
                print self
                print "player B's turn"
            move = p1.getMove(self.board)
            if move == []:
                #print("Game over: " + p1.name + " loses.\n")
                #print "Game over"
                return 'W'
            try:
                self.makeMove('B', move)
            except KonaneError:
                log("Game over: Invalid move by " + p1.name + "\n")
                log(str(move) + "\n")
                log(str(self))
                print "Game over: Invalid move by", p1.name
                print move
                print self
                return 'W'
            log(str(move) + "\n")
            log(str(self))
            log("\nplayer W's turn\n")
            if show:
                print move
                print
                print self
                print "player W's turn"
            move = p2.getMove(self.board)
            if move == []:
                #print("Game over: " + p2.name + " loses.\n")
                #print "Game over"
                return 'B'
            try:
                self.makeMove('W', move)
            except KonaneError:
                log("Game over: Invalid move by " + p2.name + "\n")
                log(str(move) + "\n")
                log(str(self))
                print "Game over: Invalid move by", p2.name
                print move
                print self
                return 'B'
            log(str(move) + "\n")
            if show:
                print move
                print
            #		log.close()

    def playNGames(self, n, p1, p2, show):
        """
        Will play out n games between player p1 and player p2.
        The players alternate going first.	Prints the total
        number of games won by each player.
        """
        first = p1
        second = p2
        for i in range(n):
            print "Game", i
            winner = self.playOneGame(first, second, show)
            if winner == 'B':
                first.won()
                second.lost()
                print first.name, "wins"
            else:
                first.lost()
                second.won()
                print second.name, "wins"
            first, second = second, first


class Player:
    """
    A base class for Konane players.  All players must implement
    the the initialize and getMove methods.
    """
    def __init__(self):
        self.name = "Player"
        self.wins = 0
        self.losses = 0
    def setSide(self, side):
        self.side = side
    def results(self):
        result = self.name
        result += " Wins:" + str(self.wins)
        result += " Losses:" + str(self.losses)
        return result
    def lost(self):
        self.losses += 1
    def won(self):
        self.wins += 1
    def reset(self):
        self.wins = 0
        self.losses = 0
    def initialize(self, side):
        """
        Records the player's side, either 'B' for black or
        'W' for white.  Should also set the name of the player.
        """
        pass
    def getMove(self, board):
        """
        Given the current board, should return a valid move.
        """
        pass


class SimplePlayer(Konane, Player):
    """
    Always chooses the first move from the set of possible moves.
    """
    def __init__(self, boardSize):
        Konane.__init__(self, boardSize)
        Player.__init__(self)
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
    def __init__(self, boardSize):
        Konane.__init__(self, boardSize)
        Player.__init__(self)
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

class HumanPlayer(Konane, Player):
    """
    Prompts a human player for a move.
    """
    def __init__(self, boardSize):
        Konane.__init__(self, boardSize)
        Player.__init__(self)
    def initialize(self, side):
        self.side = side
        self.name = "Human"
    def getMove(self, board):
        moves = self.generateMoves(board, self.side)
        while True:
            print "Possible moves:", moves
            n = len(moves)
            if n == 0:
                print "You must concede"
                return []
            index = input("Enter index of chosen move (0-"+ str(n-1) +
                          ") or -1 to concede: ")
            if index == -1:
                return []
            if 0 <= index <= (n-1):
                print "returning", moves[index]
                return moves[index]
            else:
                print "Invalid choice, try again."

if __name__ == '__main__':
    #main()
    import johnMinimaxEvolved
    Konane(6).playOneGame(RandomPlayer(6), johnMinimaxEvolved.MinimaxPlayer(6, 4), False)
