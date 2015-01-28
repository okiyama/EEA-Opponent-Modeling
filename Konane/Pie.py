# Generates pairs for crossover by giving a higher probability to more fit individuals and a lower probability
# to less fit individuals to appear in a pair. Pairs must have two unique elements.
# Date: 1/26/15
__author__ = 'julian'

import random
from bisect import bisect
from copy import copy

class Pie:
    def __init__(self, individuals):
        self.individuals = individuals
        self.fitnesses = self.getIndividualFitness(individuals)

    def getIndividualFitness(self, individuals):
        """
        Gets the list of fitnesses such that fitness[i] corresponds to individuals[i].
        :param individuals: Individuals to use
        :return: The list created
        """
        toRet = []
        for indiv in individuals:
            toRet.append(indiv.getFitness())
        return toRet

    def getTwo(self):
        """
        :return: Two individuals as a tuple, to be used for crossover elsewhere in the program.
        These individuals are weighted such that the higher the fitness of an individual, the higher probability
        that they will appear in the pair. Pairs contain two unique individuals.
        """
        indivs = copy(self.individuals)
        fits = copy(self.fitnesses)
        in1 = self.weightedChoice(indivs, fits)
        fits.pop(indivs.index(in1))
        indivs.remove(in1)
        in2 = self.weightedChoice(indivs, fits)
        # print str(in1.getFitness()) + ", " + str(in2.getFitness())
        return (in1, in2)

    def weightedChoice(self, individuals, fitnesses):
        #Modified from: http://stackoverflow.com/questions/3679694/a-weighted-version-of-random-choice
        total = sum(fitnesses)
        r = random.uniform(0, total)
        upto = 0
        for i in range(len(individuals)):
            c = individuals[i]
            weight = fitnesses[i]
            if upto + weight > r:
                return c
            upto += weight
        assert False, "Shouldn't get here"



if __name__ == "__main__":
    import randomBoardStates, EEATest
    generator = randomBoardStates.RandomStateGenerator()
    in1 = EEATest.EEATest(generator)
    in2 = EEATest.EEATest(generator)
    in3 = EEATest.EEATest(generator)
    in4 = EEATest.EEATest(generator)
    in5 = EEATest.EEATest(generator)
    in1.fitness = 1.0
    in2.fitness = 2.0
    in3.fitness = 3.0
    in4.fitness = 4.0
    in5.fitness = 5.0
    pi = Pie([in1, in2, in3, in4, in5])
    for _ in range(10):
        pi.getTwo()