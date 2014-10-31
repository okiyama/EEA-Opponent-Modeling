## This is a file for generating and then retrieving random legal board states
## The generation can take as long as wanted, and will store to
## "radomStates<board size>.p" which is a pickle file 
## containing a list of the states.
## Board size will usually be 8, since that is the size used in actual Konane

## Author: Julian Jocque
## Date: 10/30/14 (spooky!)

import updatedKonane as konane
import cPickle
import random

##TODO: Woops, need the states to be pairs of (board, player) where player corresponds to whose turn it is to move at that board.
## This means scrapping all previous data.
class randomStateGenerator:

    def __init__(self, fileName="randomStates"):
        self.boardSize = 8
        self.statesFilename = fileName + str(self.boardSize) + ".p"
        try:
            self.states = cPickle.load(open(self.statesFilename, "rb"))
        except (EOFError, IOError):
            self.states = []

    def dupeCheck(self):
        """ To check if there are any duplicates in the states. """
        print "len: " + str(len(self.states))
        for i in range(len(self.states)):
            if self.states[i] in self.states[i+1:len(self.states)]:
                print "duplicate!"
            if i % 100 == 0:
                print "at " + str(i)
        print "Done duplicate checking"

    def getRandom(self):
        """ Gets a random legal board state. """


    def genRandom(self, N = None):
        """ 
        Generates either N random board states and saves them to the file,
        or if N is not provided, continues generating until a keyboard interrupt
        occurs.
        """
        #N = None means generate until a keyboard interrupt is caught
        print "Now generating states"
        numGenerated = 0
        count = 0
        player1 = konane.RandomPlayer(self.boardSize)
        player1.initialize("W")
        player2 = konane.RandomPlayer(self.boardSize)
        player2.initialize("B")
        game = konane.Konane(self.boardSize)
        player1Turn = True
        try:
            while N is None or count < N:
                if not game.board in self.states:
                    numGenerated += 1
                    self.states.append(game.board)
                if player1Turn:
                    # Would be nice to do this, doesn't fit current control flow
                    # if len(game.generateMoves(game.board, player1.side)) == 1:
                    #     #Only one valid move, we don't care about that
                    #     #We get no info from this for EEA
                    #     player1Turn = False
                    #     continue
                    move = player1.getMove(game.board)
                    if move == []:
                        #Player1 loses, no need to store this
                        game.reset()
                        player1Turn = True
                        continue
                    game.makeMove(player1.side, move)
                    player1Turn = False
                else:
                    # Would be nice to do this, doesn't fit current control flow
                    # if len(game.generateMoves(game.board, player1.side)) == 1:
                    #     #Only one valid move, we don't care about that
                    #     #We get no info from this for EEA
                    #     player1Turn = False
                    #     continue
                    move = player2.getMove(game.board)
                    if move == []:
                        #Player2 loses, no need to store this
                        game.reset()
                        player1Turn = True
                        continue
                    game.makeMove(player2.side, move)
                    player1Turn = True
                count += 1
                if count % 1000 == 0:
                    print "Just generated state " + str(count)
        except KeyboardInterrupt:
            pass #We always want to close out, if we hit this or if we complete the loop
        cPickle.dump(self.states, open(self.statesFilename, "wb+"))
        print "Out of " + str(count) + " states generated, " + str(numGenerated) + " were unique"
        print "Done generating"


if __name__ == "__main__":
    generator = randomStateGenerator()
    generator.genRandom()
