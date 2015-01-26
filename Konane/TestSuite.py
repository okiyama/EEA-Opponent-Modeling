## A test suite, evolves a test which maximizes disagreement among models.
## The test is given as a list of EEATests.
## Date: 1/6/15
__author__ = 'julian'

import EEATest, randomBoardStates

class TestSuite:
    def __init__(self, testSize = 10, size = 8):
        self.boardSize = size
        self.testSize = testSize
        #This is just so we can have one universal generator rather than many be made.
        self.moveGenerator = randomBoardStates.RandomStateGenerator(boardSize=size)
        self.bestTest = []

    def evolve(self, models, testSetSize = 10):
        """
        Given a set of models, evolves a test which maximizes for disagreement among the models.
        :param models: The models to evolve against.
        :return: The best test from evolution, as a set of KonanePuzzles.
        """
        #1: Generate random set of tests
        testSet = []
        for i in range(testSetSize):
            test = EEATest.EEATest(self.moveGenerator, testSize=self.testSize, size=self.boardSize) #initializes to random puzzles
            test.fitness = self.disagreement(test, models)
            testSet.append(test)
        #2: Evolve these tests, with fitness being disagreement.
        #Maybe evolution crosses over puzzles from the best tests
        #3: Return the best test.
        """
        3. First, a random set of tests to run will be generated. That is to say, a set of the repre-
        sentations for tests from step 1 will be created randomly. Then these representations will be evolved
        based on the best model(s) so far and tested for fitness, storing the results. Fitness will be determined
        by how much a particular test creates disagreement among the given set of models.
        """
        self.bestTest.extend(testSet[0].getTest())
        return self.getBestTest()


    def disagreement(self, test, models):
        """
        The disagreement score of a given test against the given set of models.
        :param test: The test to measure disagreement for.
        :param models: The models to use to determine disagreement
        :return: The disagreement score
        """
        #So there's a test with puzzles in it, for every puzzle, check what moves each model makes.
        #For every
        test = []
        for puzzle in test:
            pass
        return 0.0

    def getBestTest(self):
        """
        :return: the test suite as a list of EEATests
        """
        return self.bestTest