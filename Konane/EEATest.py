## A single test for the EEA. Consists of multiple puzzles as well as an overall fitness for the test
## based on its ability to create disagreement among a set of models.
## Date: 1/13/15
__author__ = 'julian'

import KonanePuzzle
import random
import randomBoardStates
from copy import copy

class EEATest:
    def __init__(self, moveGenerator, testSize = 10, size = 8):
        self.moveGenerator = moveGenerator
        self.puzzles = self.genRandomPuzzles(testSize)
        self.fitness = 0
        self.mutatePercent = 50

    def genRandomPuzzle(self):
        """
        Generates a single random puzzle and returns it.
        :return: Random puzzle
        """
        return self.genRandomPuzzles(1)[0]

    def genRandomPuzzles(self, num):
        """
        :param num: number of random puzzles to generate
        :return: A list containing num random puzzles
        """
        puzzles = []
        for i in range(num):
            currSide = random.choice(["W", "B"])
            currState = self.moveGenerator.getRandom(currSide)
            currPuzzle = KonanePuzzle.KonanePuzzle(currState, currSide)
            puzzles.append(currPuzzle)
        return puzzles

    def mutate(self):
        """
        Mutates this test by randomly changing some of the puzzles out for new puzzles.
        :return: Mutated list of puzzles
        """
        for i in range(len(self.puzzles)):
            if random.randint(0, 100) <= self.mutatePercent:
                self.puzzles[i] = self.genRandomPuzzle()
        return self.puzzles

    def crossOver(self, other):
        """
        Crosses over self with the other test to generate a child. Crosses over by having a 50/50 chance
        of child getting each puzzle from either parent.
        :param other: The other EEATest to use as a parent.
        :return: The generated child.
        """
        copiedSelf = copy(self)
        for i in range(len(self.puzzles)):
            useOtherModel = bool(random.getrandbits(1)) #Gets a random bool quickly from
            # http://stackoverflow.com/questions/6824681/get-a-random-boolean-in-python
            if useOtherModel:
                copiedSelf.puzzles[i] = other.puzzles[i] #Sets the current puzzle to be that of other
        return copiedSelf

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