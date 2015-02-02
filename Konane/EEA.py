## Evolve static evaluators (models) using tests (board states) for an EEA
## Author: Julian Jocque
## Date: 10/6/14

import StaticEvalModel
import updatedKonane
import TestSuite
import johnMinimaxEvolved
import Pie
import random
from python27Defs import *
from time import strftime
from copy import copy
from datetime import datetime

#Evolve tests by having the fitness of a test determine the probability that a random(non-repeated?) puzzle
#from its set of puzzles be chosen.
#Perhaps it would be good to only use the top 5 or maybe even top 2.
#They also mutate after being made, the same way as before. This increases diversity.

#Make the incSize much smaller, and make the models evolve continuously until they all have 100% agreement(and some
#differences between them, that's later) and THEN we can add some puzzles to the test.

#Disagreement is sum squared mean error between the moves the different models pick for a puzzle
#Need to ratchet up mutation and crossover to reach a population which all agrees on the moves for the current test
class EEA(updatedKonane.Konane):
    def __init__(self):
        self.numModels = 10
        self.size = 6 # If you want to change this, you need to generate new random states and specify the new file
                      # in the call for the RandomStateGenerator
                      # Must also do similar stuff for initializing TestSuite
        self.depthLimit = 3
        self.models = []

        # self.opponent = updatedKonane.HumanPlayer(self.size)
        # self.opponent.initialize("W")
        # depth = random.randint(1,4) #randomize depth
        depth = 3
        print "opponent depth is " + str(depth)
        self.opponent = self.generateOpponent(numTimesToMutate=100, depthLimit = depth)

        self.incSize = 2
        self.testSuite = TestSuite.TestSuite(self.incSize, self.size)

        self.initModels(numTimesToMutate=20)
        self.startTime = strftime("%Y-%m-%d %H:%M:%S")
        self.datafile = open("data/truerEEA/data/data-" + self.startTime + ".csv", "w+")
        self.attrFile = open("data/truerEEA/attr/attr-" + self.startTime + ".csv", "w+")
        self.logAttributes()
        self.initDataFile()

    def initModels(self, numTimesToMutate = 5):
        """ Initializes the models that we'll evolve """
        for i in range(self.numModels):
            currModel = StaticEvalModel.StaticEvalModel(self.size)
            for _ in range(numTimesToMutate):
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
                self.testSuite.evolve(self.models, testSetSize=self.incSize)
                self.updateModelFitness(self.testSuite)
                while any([model.getFitness() < 1.0 for model in self.models]):
                    self.log(self.models, roundNum, datetime.time(datetime.now()))
                    self.evolveModels()
                    self.updateModelFitness(self.testSuite)
                    print "Test suite now length: " + str(len(self.testSuite.getBestTest()))
                print("Had a good generation, moving on.")
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

        #Get the opponent's responses to the test once
        for puzzle in test:
            #Only need to get a result for a puzzle in the tests if it is not set yet
            #This assumes an opponent will always give the same answer to the same puzzle
            if not puzzle.result:
                puzzle.getResult(self.opponent)

        #For ever model, see if they get the same move as the opponent. If they do, they are more fit
        #If not, they are less fit. Uses previously acquired moves from the opponent for the test
        for model in self.models:
            model.numCorrect = 0
            model.numTested = 0
            for puzzle in test:
                puzzleSide = puzzle.side
                puzzleState = puzzle.state
                puzzleResult = puzzle.result
                dummyPlayer.model = model
                dummyPlayer.setSide(puzzleSide)
                modelMove = dummyPlayer.getMove(puzzleState)
                model.numTested += 1
                # print "model move " + str(modelMove)
                # print "opponent move " + str(puzzleResult)
                # print "possible moves " + str(self.opponent.generateMoves(puzzleState, puzzleSide))
                # print "Num possible moves: " + str(len(self.opponent.generateMoves(puzzleState, puzzleSide)))
                # if modelMove not in self.opponent.generateMoves(puzzleState, puzzleSide):
                #     print "Model move was not in the possible moves for the opponent!"
                #     print self.opponent.generateMoves(puzzleState, puzzleSide)
                #     print "model move " + str(modelMove)
                #     print "puzzle size " + str(puzzleSide)
                #     print "opponent move " + str(puzzleResult)

                if puzzleResult == modelMove:
                    model.numCorrect += 1
            # print("Fitness of current model: " + str(model.getFitness()))

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

        self.attrFile.close() #This may need to move in the future

    def evolveModels(self, numModelsToKeep = 5):
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
        fitnessSortedModels = sorted(self.models, key= lambda x: x.getFitness(), reverse=True)
        print("Best fitness of generation is: " + str(fitnessSortedModels[0].getFitness()))
        # print("Fitness of generation is: " + str([model.getFitness() for model in fitnessSortedModels]))

        pie = Pie.Pie(fitnessSortedModels[0:numModelsToKeep])
        for i in range(len(self.models)):
            in1, in2 = pie.getTwo()
            curr = in1.crossOver(in2)
            curr.mutate()
            self.models[i] = curr
        self.models[0] = fitnessSortedModels[0] #Hang onto the best model, so we hypothetically never get worse

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
    # import cProfile
    # cProfile.run('eea.run(120)', sort="ncalls")
