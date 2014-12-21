## Hill Climb some static evaluators for konane
## Author: Julian Jocque
## Date: 10/6/14

from StaticEvalModel import *
from updatedKonane import *
from johnMinimaxEvolved import *
from time import strftime
from copy import copy
from datetime import datetime
from randomBoardStates import RandomStateGenerator

class EEA(Konane):

    def __init__(self):
        self.numModels = 5
        self.numTests = 5
        self.size = 8 # If you want to change this, you need to generate new random states and specify the new file
                      # in the call for the RandomStateGenerator
        self.depthLimit = 3
        self.models = []
        self.randomMoveGenerator = RandomStateGenerator()


        self.eeaOpponent = self.generateOpponent()

        self.initModels()
        self.currPlayers = []
        self.startTime = strftime("%Y-%m-%d %H:%M:%S")
        self.datafile = open("data/EEA/data-" + self.startTime + ".csv", "w")
        self.attrFile = open("data/EEA/attr-" + self.startTime + ".csv", "w")
        self.logAttributes()

    def initModels(self):
        """ Initializes the models that we'll evolve """
        for i in range(self.numModels):
            currModel = StaticEvalModel(self.size)
            currModel.mutate()
            self.models.append(currModel)

    def generateOpponent(self):
        """
        :return: An opponent who has a singly mutated model.
            The model is mutated more than the default values for a model's mutation.
            Just to make it a bit harder to find.
        """
        opponent = MinimaxPlayer(self.size, self.depthLimit)
        opponent.model = StaticEvalModel(self.size)
        opponent.model.chanceToMutate = 100
        opponent.model.mutate()
        return opponent


    def run(self, timeToRun = None):
        # If timeToRun is None, go until interrupt else do that many seconds
        """
        Runs the EEA, trying to determine the static evaluator of self.opponent
        """
        # Generate random model (static evaluator). This can be subbed in for any given opponent. DONE - self.opponent
        ## Therefore, better to have it be a KonanePlayer or whatever, for subbing in easily.
        # Record the opponent's evaluator to a file, for starters.
        self.recordOpponent()
        # Generate random models DONE - initModels
        # LOOP:

        ## Generate a set of N random board states, randomizing the sides would be good.
        ### This will eventually be evolved to maximize disagreement among the existing models.
        ### A bit annoying to implement because we'd need to ask for moves from different sides from opponent.
        ### Not awful though, it might just be opponent.side = state.side, opponent.getMove(state.board)
        ## Get the moves the opponent responds with and store them internally.
        ### Keep track of the sides, so there is a self.whiteOpponentResponses and self.blackOpponentResponses
        ### OR it could be (initial board, whose turn it is from that board, resulting move) tuples.
        ## Evolve the models
        ### Fitness is what percent of the test suite that it correctly predicts the outcome for
        ### Might need a notion of diversity eventually

    def recordOpponent(self):
        """
        Records relevant information about self.opponent.
        """
        pass

    def hillClimb(self):
        self.datafile.write("%roundNum, %playerNum, %fitness, " +
                            self.models[0].dumpFeatures() + ", %timeIndividualFinished\n")
        running = True
        roundNum = 0
        try:
            while running:
                for playerNum in range(self.numModels):
                    player1 = MinimaxPlayer(self.size, self.depthLimit)
                    player1.model = self.models[playerNum]
                    # player1.ABPrune = self.ABPrune
                    self.currPlayers.append(player1)
                    player2 = RandomPlayer(self.size)

                    for gameNum in range(self.numGames):
                        # print "On game num", gameNum
                        winner = self.playOneGame(player1, player2)
                        player1.model.gamesPlayed += 1
                        if winner == player1:
                            player1.model.gamesWon += 1
                    self.log(player1, playerNum, roundNum, datetime.time(datetime.now()))
                self.datafile.flush()
                roundNum += 1

                # Bleh, Python 2.4...
                bestYet = -1000000
                bestIndex = 0
                for i in range(len(self.currPlayers)):
                    if self.currPlayers[i].model.getFitness() > bestYet:
                        bestIndex = i
                parent = self.currPlayers[bestIndex]
                self.evolveModels(parent)
                self.currPlayers = []
        except KeyboardInterrupt:
            self.datafile.close()

    def evolveModels(self, parent):
        """ Evolves the models in self.models based on the given parent. """
        for i in range(self.numModels):
            curr = copy(parent.model)
            curr.mutate()
            self.models[i] = curr


    def playOneGame(self, p1, p2):
        """
        Given two instances of players, will play out a game
        between them.  Returns the instance of the player than won.
        """
        self.reset()
        p1.initialize('B')
        p2.initialize('W')
        while True:
            move = p1.getMove(self.board)
            if move == []:
                return p2
            try: 
                self.makeMove('B', move)
            except KonaneError:
                print "Game over: Invalid move by", p1.name
                print move
                print self
                return p2
            move = p2.getMove(self.board)
            if move == []:
                return p1
            try:
                self.makeMove('W', move)
            except KonaneError:
                print "Game over: Invalid move by", p2.name
                print move
                print self
                return p1

    def logAttributes(self):
        """ 
        Logs the attributes like depth, number of games and if AB is on or off. 
        Format is as follows:
        %numGamesPerRound, %depth, %boardSize, %numPlayers
        """
        self.attrFile.write("%numGamesPerRound, %depth, %boardSize, %numPlayers\n")
        self.attrFile.write(str(self.numGames) + ", "
            + str(self.depthLimit) + ", " + str(self.size) + ", " + str(self.numModels) + "\n")

    def log(self, player, playerNum, roundNum, time):
        """ 
        Logs the results of hill climbing to the log file.
        Each line is this format:
        %roundNum, %playerNum, %fitness, %myMovesWeight, %theirMovesWeight, %myPiecesWeight, %theirPiecesWeight, %time
        """
        self.datafile.write(str(roundNum) + ", " + str(playerNum) + ", " + str(player.getFitness())
                + ", " + player.model.dumpModel() + ", " + str(time) + "\n")

if __name__ == "__main__":
    eea = EEA()
    eea.run()
