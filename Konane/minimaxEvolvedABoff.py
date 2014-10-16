from konane import *
from StaticEvalModel import StaticEvalModel

# Note: side is either 'B' or 'W'
class MinimaxNode:
    """
    Black always goes first and is considered the maximizer.
    White always goes second and is considered the minimizer.
    """
    def __init__(self, board, lastMove, depth, player):
        self.state = board
        self.operator = lastMove
        self.depth = depth
        self.player = player
        # state: the current board configuration
        # operator: the move that resulted in the current board configuration
        # depth: the depth of the node in the search tree
        # player: maximizer or minimizer

    def isRoot(self):
        """ Returns if this node is the root node """
        return self.depth == 0 #May change to 1
        
    def isMaximizer(self):
        """ Returns if this node is the maximizer or not. """
        return self.player == 'B'

    def isMinimizer(self):
        """ Returns if this node is the minimizer or not. """
        return self.player == 'W'

class MinimaxPlayer(Konane, Player):

    def __init__(self, size, depthLimit):
        Konane.__init__(self, size)
        Player.__init__(self)
        self.limit = depthLimit
        self.ABPrune = False
        self.nodesExplored = 0
        self.model = StaticEvalModel(size)
        self.gamesPlayed = 0
        self.gamesWon = 0

    def getFitness(self):
        """ Gets the fitness of this player """
        return (float (self.gamesWon) / self.gamesPlayed)

    def initialize(self, side):
        """
        Initializes the player's color and name.
        """
        self.side = side
        self.name = "MinimaxDepth" + str(self.limit) + "Jocque"

    def isMaximizer(self):
        """ Returns if this player is the maximizer. """
        return self.side == 'B'

    def isMinimizer(self):
        """ Returns if this player is the minimizer. """
        return self.side == 'W'

    def getMove(self, board):
        """
        Returns the chosen move based on doing an alphaBetaMinimax 
        search.
        """
        node = MinimaxNode(board, [], 0, self.side)
        if self.ABPrune:
            self.alphaBetaMinimax(node, -100000000000, 100000000000)
        else:
            self.minimax(node)
        return self.bestMove

    def staticEval(self, node):
        """
        Returns an estimate of the value of the state associated
        with the given node.
        """
        return self.model.staticEval(node)


    def successors(self, node):
        """
        Returns a list of the successor nodes for the given node.
        """  
        successors = []
        for move in self.generateMoves(node.state, node.player):
            try:
                nextBoard = self.nextBoard(node.state, node.player, move)
            except KonaneError:
                print "Found a bad move while generating successors"
                continue
            nextNode = MinimaxNode(nextBoard, move, node.depth + 1, self.opponent(node.player))
            successors.append(nextNode)
        
        return successors

    def minimax(self, node):
        """
        Returns the best score for the player associated with the 
        given node.  Also sets the instance variable bestMove to the
        move associated with the best score at the root node.
        """
        self.nodesExplored += 1
        # check if at search bound
        if (node.depth == self.limit):
            return self.staticEval(node)

        # check if leaf
        children = self.successors(node)
        if len(children) == 0:
            if node.isRoot():
                self.bestMove = [] 
            return self.staticEval(node)

        # initialize bestMove
        if node.isRoot():
            self.bestMove = children[0].operator # First child's operator, unclear why that is default best move 
            # check if there is only one option
            if len(children) == 1:
                return None

        # if it is MAX's turn to move
        bestYet = -100000000000
        if node.isMaximizer():
            for child in children:
                result = self.minimax(child)
                if result > bestYet:
                    bestYet = result
                    if node.isRoot():
                        self.bestMove = child.operator
            return bestYet 

        # if it is MIN's turn to move
        lowestYet = 100000000000
        if node.isMinimizer():
            for child in children:
                result = self.minimax(child)
                if result < lowestYet:
                    lowestYet = result
                    if node.isRoot():
                        self.bestMove = child.operator
            return lowestYet 

    def alphaBetaMinimax(self, node, alpha, beta):
        """
        Returns the best score for the player associated with the 
        given node.  Also sets the instance variable bestMove to the
        move associated with the best score at the root node.
        Initialize alpha to -infinity and beta to +infinity.
        """
        self.nodesExplored += 1
        # check if at search bound
        if (node.depth == self.limit):
            return self.staticEval(node)

        # check if leaf
        children = self.successors(node)
        if len(children) == 0:
            if node.isRoot():
                self.bestMove = [] 
            return self.staticEval(node)

        # initialize bestMove
        if node.isRoot():
            self.bestMove = children[0].operator # First child's operator, unclear why that is default best move 
            # check if there is only one option
            if len(children) == 1:
                return None

        # if it is MAX's turn to move
        if node.isMaximizer():
            for child in children:
                result = self.alphaBetaMinimax(child, alpha, beta)
                if result > alpha:
                    alpha = result
                    if node.isRoot():
                        self.bestMove = child.operator
                if alpha >= beta:
                    return alpha
            return alpha

        # if it is MIN's turn to move
        if node.isMinimizer():
            for child in children:
                result = self.alphaBetaMinimax(child, alpha, beta)
                if result < beta:
                    beta = result
                    if node.isRoot():
                        self.bestMove = child.operator
                if beta <= alpha:
                    return beta
            return beta

