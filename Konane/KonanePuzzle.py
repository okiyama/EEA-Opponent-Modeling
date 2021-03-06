## A single puzzle for Konane. This is a board state, as well as the side of that board state and
## The resultant move from the opponent.
## Can get the result from a given opponent on their solution to this puzzle.
## Date: 1/6/15
__author__ = 'julian'

from copy import copy

class KonanePuzzle:
    def __init__(self, boardState, side, result = None):
        """
        :param boardState: the state the opponent responds to
        :param side: what side the opponent is playing in that state
        :param result: The resultant move from the opponent
        :return:
        """
        self.state = boardState
        self.side = side
        self.result = result

    def getResult(self, opponent):
        """
        Given an opponent, gets the resultant move from them. Also sets the instance variable self.result.
        :param opponent: A Konane Player to get the move from
        :return: The resultant move
        """
        initialSide = copy(opponent.side)
        opponent.setSide(self.side)
        self.result = opponent.getMove(self.state)
        opponent.setSide(initialSide)
        return self.result