## A single test for the EEA. Consists of multiple puzzles as well as an overall fitness for the test
## based on its ability to create disagreement among a set of models.
## Date: 1/13/15
__author__ = 'julian'

import KonanePuzzle
import random
import randomBoardStates

class EEATest:
    def __init__(self, moveGenerator, testSize = 10, size = 8):
        self.moveGenerator = moveGenerator
        self.puzzles = self.genRandomPuzzles(testSize)
        self.fitness = 0

    def genRandomPuzzles(self, num):
        puzzles = []
        for i in range(num):
            currSide = random.choice(["W", "B"])
            currState = self.moveGenerator.getRandom(currSide)
            currPuzzle = KonanePuzzle.KonanePuzzle(currState, currSide)
            puzzles.append(currPuzzle)
        return puzzles

    def getTest(self):
        """
        :return: The test as a set of KonanePuzzles with no responses associated with them.
        """
        return self.puzzles

    def getFitness(self):
        """
        :return: The fitness of this test.
        """
        return self.fitness