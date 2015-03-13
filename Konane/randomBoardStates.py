## This is a file for generating and then retrieving random legal board states
## The generation can take as long as wanted, and will store to
## "radomStates<board size>.p" which is a pickle file 
## containing a list of the states.

## Author: Julian Jocque
## Date: 10/30/14 (spooky!)

import updatedKonane as konane
import cPickle
import random

class RandomStateGenerator:

    def __init__(self, fileName="randomStates", boardSize = 8):
        self.boardSize = boardSize
        self.blackStatesFilename = fileName + "black" + str(self.boardSize) + ".p"
        self.whiteStatesFilename = fileName + "white" + str(self.boardSize) + ".p"
        try:
            self.blackStates = cPickle.load(open(self.blackStatesFilename, "rb"))
            self.whiteStates = cPickle.load(open(self.whiteStatesFilename, "rb"))
        except (EOFError, IOError):
            self.blackStates = []
            self.whiteStates = []

    def dupeCheck(self):
        """ To check if there are any duplicates in the states. """
        print "len: " + str(len(self.states))
        for i in range(len(self.states)):
            if self.states[i] in self.states[i+1:len(self.states)]:
                print "duplicate!"
            if i % 100 == 0:
                print "at " + str(i)
        print "Done duplicate checking"

    def cleanUp(self):
        """
        Cleans up the states to remove anything where the number of states is 0 or 1, since we
        gain no information from those states.
        :return: None
        """
        #TODO: If the move is of the form [A, B, A, B] Then it is invalid and should be removed.
        game = konane.Konane(self.boardSize)
        print(len(self.blackStates))
        shouldRemove = False
        for blackState in self.blackStates:
            moves = game.generateMoves(blackState, "B")
            if len(moves) <= 1:
                #print("Removing black move " + str(blackState))
                #print(str(game.generateMoves(self.blackStates[i], "B")))
                shouldRemove = True
            for move in moves:
                if move[0] == move[2] and move[1] == move[3]:
                    #Remove moves of the form [A, B, A, B] because that's impossible
                    shouldRemove = True
            if shouldRemove:
                self.blackStates.remove(blackState)
                shouldRemove = False
        print(len(self.blackStates))

        print(len(self.whiteStates))
        for whiteState in self.whiteStates:
            moves = game.generateMoves(whiteState, "W")
            if len(moves) <= 1:
                #print("Removing white move " + str(whiteState))
                shouldRemove = True
            for move in moves:
                if move[0] == move[2] and move[1] == move[3]:
                    #Remove moves of the form [A, B, A, B] because that's impossible
                    shouldRemove = True
            if shouldRemove:
                self.whiteStates.remove(whiteState)
                shouldRemove = False
        print(len(self.whiteStates))

        self.updatePickleFiles()

    def getRandom(self, side):
        """ Gets a random legal board state from the given side. 
        :rtype : boardState
        """
        if side.lower() == "w":
            return random.choice(self.whiteStates)
        elif side.lower() == "b":
            return random.choice(self.blackStates)
        else:
            raise ValueError("Side must be W or B")

    def getRandomNoSide(self):
        """ Gets a random legal board state from a random side.
         Returns (state, side)
        :rtype : boardState
        """
        side = random.choice(["W", "B"])
        state = self.getRandom(side)
        return (state, side)

    def getAvgMoveCount(self):
        """
        Gets the average number of moves for a random board state
        :return: average number of moves
        """
        game = konane.Konane(self.boardSize)
        moveLens = []
        while True:
            state, side = self.getRandomNoSide()
            moves = game.generateMoves(state, side)
            # print moves
            moveLens.append(len(moves))
            print "Average: " + str((float(sum(moveLens)) / len(moveLens)))

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
                if player1Turn and not game.board in self.whiteStates:
                    numGenerated += 1
                    self.whiteStates.append(game.board)
                elif not player1Turn and not game.board in self.blackStates:
                    numGenerated += 1
                    self.blackStates.append(game.board)

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
        self.updatePickleFiles()
        print "Out of " + str(count) + " states generated, " + str(numGenerated) + " were unique"
        print "Done generating"
        print "Now at " + str(len(self.whiteStates)) + " white board states and " + str(len(self.blackStates)) + " black states."

    def updatePickleFiles(self):
        """
        Updates the pickle files to contain the current whiteStates and blackStates.
        :return:
        """
        cPickle.dump(self.whiteStates, open(self.whiteStatesFilename, "wb+"))
        cPickle.dump(self.blackStates, open(self.blackStatesFilename, "wb+"))

if __name__ == "__main__":
    generator = RandomStateGenerator(boardSize=8)
    #generator.genRandom()
    #generator.cleanUp()
    generator.getAvgMoveCount()
