## A test suite, contains tests which are board states with a side of the board associated with them
## As well as the response from the opponent
## This assumes that the board size in RandomStateGenerator and in the opponent is the same
## Date: 1/6/15
__author__ = 'julian'

import EEATest
import randomBoardStates
import random

class TestSuite:

    #Increment is how many new tests to create to present the opponent with for each round of tests
    def __init__(self, opponent, increment = 5, size = 8):
        self.moveGenerator = randomBoardStates.RandomStateGenerator(boardSize=size)
        self.incSize = increment
        self.opponent = opponent
        self.tests = []

    def runRound(self):
        """
        Runs one round of tests on self.incSize new random board states against self.opponent
        :return: The updated testSuite, as a list of EEATests
        """
        for i in range(self.incSize):
            currSide = random.choice(["W", "B"])
            currState = self.moveGenerator.getRandom(currSide)
            currTest = EEATest.EEATest(currState, currSide)
            currTest.getResult(self.opponent)
            self.tests.append(currTest)
        return self.getSuite()

    def getSuite(self):
        """
        :return: the test suite as a list of EEATests
        """
        return self.tests