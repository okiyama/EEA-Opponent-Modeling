## Evolve static evaluators (models) using tests (board states) for an EEA
## Author: Julian Jocque
## Date: 10/6/14

import StaticEvalModel
import updatedKonane
import TestSuite
import johnMinimaxEvolved
from time import strftime
from copy import copy
from datetime import datetime

#Evolve tests by having the fitness of a test determine the probability that a random(non-repeated?) puzzle
#from its set of puzzles be chosen.
#Perhaps it would be good to only use the top 5 or maybe even top 2.
#They also mutate after being made, the same way as before. This increases diversity.
class EEA(updatedKonane.Konane):
    def __init__(self):
        self.numModels = 10
        self.size = 6 # If you want to change this, you need to generate new random states and specify the new file
                      # in the call for the RandomStateGenerator
                      # Must also do similar stuff for initializing TestSuite
        self.depthLimit = 1
        self.models = []

        # self.opponent = updatedKonane.SimplePlayer(self.size)
        # self.opponent.initialize("W")
        self.opponent = self.generateOpponent(numTimesToMutate=100, depthLimit = 3) #Try it with limit 4, see if a limit 3 can model it

        self.incSize = 25
        self.testSuite = TestSuite.TestSuite(self.incSize, self.size)

        self.initModels()
        self.startTime = strftime("%Y-%m-%d %H:%M:%S")
        self.datafile = open("data/EEA/data/data-" + self.startTime + ".csv", "w")
        self.attrFile = open("data/EEA/attr/attr-" + self.startTime + ".csv", "w")
        self.logAttributes()
        self.initDataFile()

    def initModels(self):
        """ Initializes the models that we'll evolve """
        for i in range(self.numModels):
            currModel = StaticEvalModel.StaticEvalModel(self.size)
            currModel.mutate()
            self.models.append(currModel)

    def generateOpponent(self, side = "W", numTimesToMutate = 25, depthLimit = 3):
        """
        Generates an opponent by making a default model and then mutating it numTimesToMutate times.
        Then, puts that model in an opponent with default board size and depth limit to be played against.
        :param side: The side the opponent should start as
        :param numTimesToMutate: Number of times to mutate the model, higher means harder to find.
        :return: An opponent who has a mutated model.
            The model is mutated more than the default values for a model's mutation.
            Just to make it a bit harder to find.
        """
        opponent = johnMinimaxEvolved.MinimaxPlayer(self.size, depthLimit)
        opponent.initialize(side)
        opponent.model = StaticEvalModel.StaticEvalModel(self.size)
        opponent.model.chanceToMutate = 100
        for i in range(numTimesToMutate):
            opponent.model.mutate()
        return opponent

    def run(self, timeToRun = None):
        """
        Runs the EEA, trying to determine the static evaluator of self.opponent
        """
        # Generate random model (static evaluator). This can be subbed in for any given opponent. DONE - self.opponent
        ## Therefore, better to have it be a KonanePlayer or whatever, for subbing in easily.
        # Record the opponent's evaluator to a file, for starters.
        self.recordOpponent()

        startTime = datetime.now()
        elapsedTime = 0
        roundNum = 1
        try:
            while timeToRun is None or elapsedTime < timeToRun:
                elapsedTime = (datetime.now() - startTime).seconds
                self.testSuite.evolve(self.models)
                self.updateModelFitness(self.testSuite)
                self.log(self.models, roundNum, datetime.time(datetime.now()))
                self.evolveModels()
                roundNum += 1
        except KeyboardInterrupt:
            pass
        self.datafile.close()


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

    def updateModelFitness(self, testSuite):
        """
        Updates the fitnesses of the models in self.models given the current testSuite
        :param testSuite: The recently updated suite used to update the model's fitnesses
        :return: The models as a list of StaticEvalModels
        """
        test = testSuite.getBestTest()
        dummyPlayer = johnMinimaxEvolved.MinimaxPlayer(self.size, self.depthLimit)
        dummyPlayer.initialize("W")

        for model in self.models:
            for puzzle in test:
                puzzleSide = puzzle.side
                puzzleState = puzzle.state
                puzzleResult = puzzle.getResult(self.opponent)
                dummyPlayer.model = model
                dummyPlayer.setSide(puzzleSide)
                modelMove = dummyPlayer.getMove(puzzleState)
                model.numTested += 1
                if puzzleResult == modelMove:
                    model.numCorrect += 1
            print("Fitness of current model: " + str(model.getFitness()))


    def recordOpponent(self):
        """
        Records relevant information about self.opponent to the attribute file.
        """
        self.attrFile.write("Opponent info:\n")
        self.attrFile.write("Name: " + self.opponent.name + "\n")
        try:
            oppModel = self.opponent.model
            self.attrFile.write(oppModel.dumpFeatures() + ", %depth\n")
            self.attrFile.write(oppModel.dumpModel() + ", " + str(self.opponent.limit) + "\n")
        except AttributeError:
            #No model found
            pass


    def evolveModels(self):
        """
        Evolves the models by choosing the best one yet and mutating it to generate children
        The resulting population has the one best parents and N-1 generated children, generated by mutation
        :return: The evolved models
        """
        """
        4. Estimation - The existing models of the system will be evolved, encouraging diversity among them.
        The fitness of a particular model is defined by its ability to accurately model all previous sets of inputs
        and outputs from the system. The best model out of the set of models will be sent to step 6, and N of
        the best models will be sent to step 3 to continue evolution.
        """
        # Bleh, Python 2.4...
        bestYet = -1000000
        bestIndex = 0
        for i in range(len(self.models)):
            if self.models[i].getFitness() >= bestYet:
                bestIndex = i
                bestYet = self.models[i].getFitness()
        parent = self.models[bestIndex]
        print("Best fitness of generation is: " + str(parent.getFitness()))

        for i in range(len(self.models)):
            if i == bestIndex:
                continue #Keep the parent in the population
            curr = copy(parent)
            curr.mutate()
            self.models[i] = curr

        return self.models


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
            except updatedKonane.KonaneError:
                print "Game over: Invalid move by", p1.name
                print move
                print self
                return p2
            move = p2.getMove(self.board)
            if move == []:
                return p1
            try:
                self.makeMove('W', move)
            except updatedKonane.KonaneError:
                print "Game over: Invalid move by", p2.name
                print move
                print self
                return p1

    def logAttributes(self):
        """ 
        Logs the attributes of this test run.
        Format is as follows:
        %numTestsPerRound, %depth, %boardSize, %numModels
        """
        self.attrFile.write("%numTestsPerRound, %depth, %boardSize, %numModels\n")
        self.attrFile.write(str(self.incSize) + ", "
            + str(self.depthLimit) + ", " + str(self.size) + ", " + str(self.numModels) + "\n")

    def initDataFile(self):
        """
        Initializes the data file by writing the attributes line of the CSV.
        :return: None
        """
        dummyModel = StaticEvalModel.StaticEvalModel(self.size)
        self.datafile.write("%roundNum, %fitness, " + dummyModel.dumpFeatures() + ", %roundEndTime\n")

    def log(self, models, roundNum, roundEndTime):
        """ 
        Logs the results of one round of the EEA to the log file.
        Each line is this format:
        %roundNum, %fitness, %myMovesWeight, %theirMovesWeight, %myPiecesWeight, %theirPiecesWeight,
         %myMovableWeight , %theirMovableWeight, %roundEndTime
        """
        for model in models:
            self.datafile.write(str(roundNum) + ", " + str(model.getFitness())
                + ", " + model.dumpModel() + ", " + str(roundEndTime) + "\n")

if __name__ == "__main__":
    eea = EEA()
    eea.run()
    #cProfile.run('eea.run(60)', sort="cumtime")
