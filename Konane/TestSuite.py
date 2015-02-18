## A test suite, evolves a test which maximizes disagreement among models.
## The test is given as a list of EEATests.
## Date: 1/6/15
__author__ = 'julian'

import EEATest, randomBoardStates, johnMinimaxEvolved, Pie
from python27Defs import *

class TestSuite:
    def __init__(self, dummyPlayer, testSize = 10, size = 8):
        self.dummyPlayer = dummyPlayer #this is the player we'll use to get moves from the models.
        self.boardSize = size
        self.testSize = testSize
        #This is just so we can have one universal generator rather than many be made.
        self.moveGenerator = randomBoardStates.RandomStateGenerator(boardSize=size)
        self.disagreementReqToContinue = 0.5
        self.bestTest = []

    def evolve(self, models, testSetSize = 10):
        """
        Given a set of models, evolves a test which maximizes for disagreement among the models.
        :param models: The models to evolve against.
        :return: The best test from evolution, as a set of KonanePuzzles.
        """
        """
        3. First, a random set of tests to run will be generated. That is to say, a set of the repre-
        sentations for tests from step 1 will be created randomly. Then these representations will be evolved
        based on the best model(s) so far and tested for fitness, storing the results. Fitness will be determined
        by how much a particular test creates disagreement among the given set of models.
        """
        NUM_GENS_BEFORE_GIVING_UP = 100
        #1: Generate random set of tests
        testSet = []
        for i in range(testSetSize):
            test = EEATest.EEATest(self.moveGenerator, testSize=self.testSize, size=self.boardSize) #initializes to random puzzles
            test.fitness = self.disagreement(test, models)
            testSet.append(test)

        #2: Evolve these tests, with fitness being disagreement.
        #Maybe evolution crosses over puzzles from the best tests

        #Do just one round of evolution
        evolvedTests = []
        pie = Pie.Pie(testSet)
        for i in range(len(testSet)):
            in1, in2 = pie.getTwo()
            curr = in1.crossOver(in2)
            curr.mutate()
            curr.fitness = self.disagreement(curr, models)
            evolvedTests.append(curr)

        #Wait until we find a test that reaches a particular desired disagreement value
        print "Evolving tests now"
        numGenerations = 0
        while not any([evolvingTest.getFitness() > self.disagreementReqToContinue for evolvingTest in evolvedTests])\
                and numGenerations < NUM_GENS_BEFORE_GIVING_UP:
            currTests = []
            pie = Pie.Pie(evolvedTests)
            for i in range(len(evolvedTests)):
                in1, in2 = pie.getTwo()
                curr = in1.crossOver(in2)
                curr.mutate()
                curr.fitness = self.disagreement(curr, models)
                currTests.append(curr)
            evolvedTests = currTests
            numGenerations += 1
            # print [test.getFitness() for test in evolvedTests]

        evolvedTests.append(max(testSet, key= lambda x: x.getFitness())) #Hang onto the best test, so we hypothetically never get worse

        #3: Return the best test.
        self.bestTest.extend(max(evolvedTests, key= lambda x: x.getFitness()).getTest())

        print "Disagreement score of best after evolution: " + str(max(evolvedTests, key= lambda x: x.getFitness()).getFitness())
        return self.getBestTest()

    def disagreement(self, test, models):
        """
        The disagreement score of a given test against the given set of models.
        Assumes all models use a Minimax player that has self.boardSize size
        and also that they all have the same depth. Can be easily modified to use
        models of different depths, but it'll be less efficient.
        :param test: The test to measure disagreement for.
        :param models: The models to use to determine disagreement
        :return: The disagreement score
        """
        """
        I'm thinking of just counting the number of unique moves that a test causes among the set of models
        and dividing by (size of test * num models)
        So if I have a test with 2 board states in it and my 5 models predict moves like:
        [(0, 1), (1, 2), (1, 2), (3, 4), (1, 1)]
        Then the only unique moves predicted are The 0 from the first tuple and the 3 and 4.
        So that's 3 / (2 * 5) = 0.3 disagreement.
        """
        disagreement = 0.0
        results = [] #This will be a 2D list where every entry is a list of the models responses to each puzzle in the test
                     #These are in order, so results[i][0] corresponds to results[j][0]
        for model in models:
            currModelResults = []
            for puzzle in test.getTest():
                self.dummyPlayer.model = model
                result = puzzle.getResult(self.dummyPlayer)
                currModelResults.append(result)
            results.append(currModelResults)

        # Computes the disagreement.
        # Disagreement is +1 for every time two of the models don't agree on what move to make.
        # Then divided by the number of moves that are considered.
        for i in range(len(results[0])):
            for j in range(len(results) - 1):
                if results[j][i] != results[j+1][i]:
                    disagreement += 1.0
        disagreement /= (float(len(results[0])) * len(results))
        # print "Disagreement score: " + str(disagreement)

        #Need to clear the results of the test so that we correctly ask opponent for a move later
        for puzzle in test.getTest():
            puzzle.result = None

        return disagreement

    def getBestTest(self):
        """
        :return: the test suite as a list of EEATests
        """
        return self.bestTest
