from konane import *
from StaticEvalModel import *

class MinimaxNode:
    """
    Black always goes first and is considered the maximizer.
    White always goes second and is considered the minimizer.
    """
    maximizer = 'B'
    minimizer = 'W'
    def __init__(self, state, operator, depth, player):
        self.state = state
        self.operator = operator
        self.depth = depth
        self.player = player
    def __str__(self):
        result = ""
        if self.maximizing():
            result += "Maximizing "
        else:
            result += "Minimizing "
        result += "node at depth: " + str(self.depth) + "\n"
        result += "Operator: " + str(self.operator) + "\n"
        #result += str(self.state)
        return result
    def maximizing(self):
        return self.player == self.maximizer

class MinimaxPlayer(Konane, Player):
    infinity = 5000
    limit = 0
    bestMove = None

    def __init__(self, size, depthLimit):
        Konane.__init__(self, size)
        Player.__init__(self)
        self.limit = depthLimit
        self.model = StaticEvalModel(size)
        self.gamesPlayed = 0
        self.gamesWon = 0

    def initialize(self, side):
        self.side = side
        self.name = "MinimaxDepth" + str(self.limit)

    def getMove(self, board):
        initialNode = MinimaxNode(board, None, 0, self.side)
        #self.boundedMinimax(initialNode)
        self.alphaBeta(initialNode, -self.infinity, self.infinity)
        #print "BEST MOVE:", self.bestMove
        return self.bestMove

    def getFitness(self):
        """ Gets the fitness of this player """
        return (float(self.gamesWon) / self.gamesPlayed)

    def eval(self, node):
        """
        Given a search node, returns an estimate of the value of its
        associated state.
        """
        maxMoves = len(self.generateMoves(node.state, node.maximizer))
        if maxMoves == 0 and node.player == node.maximizer:
            return -self.infinity
        minMoves = len(self.generateMoves(node.state, node.minimizer))
        if minMoves == 0 and node.player == node.minimizer:
            return self.infinity
        return self.model.staticEval(node)

    def successors(self, node):
        result = []
        for move in self.generateMoves(node.state, node.player):
            nextState = self.nextBoard(node.state, node.player, move)
            nextNode = MinimaxNode(nextState, move, node.depth+1,
                                   self.opponent(node.player))
            result.append(nextNode)
        return result

    def boundedMinimax(self, node):
        """
        Returns the best score for the given node, and only for the root
        node sets the class variable bestMove to the move corresponding to
        the best score.
        """
        # check for depth limit
        if node.depth == self.limit:
            return self.eval(node)
        children = self.successors(node)
        # check for leaf
        if len(children) == 0:
            if node.depth == 0:
                self.bestMove = []
            return self.eval(node)
        # initialize best move
        if node.depth == 0:
            self.bestMove = children[0].operator
            # if only one choice at root level, take it
            if len(children) == 1:
                #print "only one option"
                return None
        # call procedure recursively to find maximum successor
        if node.maximizing():
            maxValue = -self.infinity
            for i in range(len(children)):
                result = self.boundedMinimax(children[i])
                if result > maxValue:
                    maxValue = result
                    if node.depth == 0:
                        self.bestMove = children[i].operator
            return maxValue
        # call procedure recursively to find minimum successor
        else:
            minValue = self.infinity
            for i in range(len(children)):
                result = self.boundedMinimax(children[i])
                if result < minValue:
                    minValue = result
                    if node.depth == 0:
                        self.bestMove = children[i].operator
            return minValue

    def alphaBeta(self, node, alpha, beta):
        """
        The variable alpha is the maximum value found so far in the
        descendants of a maximizing node.  The variable beta is the
        minimum value found so far in the descendants of a minimizing
        node. alpha is initialized to -infinity and beta is
        initialized to infinity.
        """
        #print node
        if node.depth == self.limit:
            return self.eval(node)
        children = self.successors(node)
        if len(children) == 0:
            if node.depth == 0:
                self.bestMove = []
            return self.eval(node)
        if node.depth == 0:
            self.bestMove = children[0].operator
            if len(children) == 1:
                #print "only one option"
                return None
        if node.maximizing():
            for i in range(len(children)):
                result = self.alphaBeta(children[i], alpha, beta)
                if result > alpha:
                    alpha = result
                    if node.depth == 0: self.bestMove = children[i].operator
                if alpha >= beta:
                    #print "Braches cut off:", len(children)-i 
                    return alpha
            return alpha
        else:
            for i in range(len(children)):
                result = self.alphaBeta(children[i], alpha, beta)
                if result < beta:
                    beta = result
                    if node.depth == 0: self.bestMove = children[i].operator
                if beta <= alpha:
                    #print "Branches cut off:", len(children)-i
                    return beta
            return beta

if __name__ == '__main__':
    game = Konane(8)
    game.playNGames(50, MinimaxPlayer(8,2), RandomPlayer(8))


