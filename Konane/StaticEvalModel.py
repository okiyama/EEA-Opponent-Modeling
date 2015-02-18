# A model that can be evolved for a static evaluator
# Julian Jocque
# 10/3/14

import random
import updatedKonane
from copy import copy

class StaticEvalModel(updatedKonane.Konane):
    def __init__(self, size):
        self.CORRECTNESS_WEIGHT = 100.0
        self.DIVERSITY_WEIGHT = 0.05

        self.size = size
        self.myMovesWeight = 1.0
        self.theirMovesWeight = 1.0
        self.myPiecesWeight = 1.0
        self.theirPiecesWeight = 1.0
        self.myMovableWeight = 1.0
        self.theirMovableWeight = 1.0
        self.featuresNameList = ["myMovesWeight", "theirMovesWeight", "myPiecesWeight", "theirPiecesWeight",
                                    "myMovableWeight", "theirMovableWeight"]
        self.chanceToMutate = 50 #as a percent
        self.mutateAmount = 3.0
        self.numCorrect = 0
        self.numTested = 0
        self.diversity = 0.0 #The diversity of this versus the current population
        #self.fitness = 0 #Fitness should be win rate of past X games?


    # def staticEval(self, node):
    #     return ((self.countSymbol(node.state, node.player) * self.myPiecesWeight) \
    #                 - (self.countSymbol(node.state, self.opponent(node.player)) * self.theirPiecesWeight))

    #Return the weighted static evaluation of the given node
    #This is the sum of the weighted differences of each pair of features
    def staticEval(self, node):
        return ((len(self.generateMoves(node.state, node.player)) * self.myMovesWeight) \
                    - (len(self.generateMoves(node.state, self.opponent(node.player))) * self.theirMovesWeight)) \
                    + ((self.countSymbol(node.state, node.player) * self.myPiecesWeight) \
                    - (self.countSymbol(node.state, self.opponent(node.player)) * self.theirPiecesWeight)) \
                    + ((self.countMovablePieces(node.state, node.player) * self.myMovableWeight ) \
                    - (self.countMovablePieces(node.state, self.opponent(node.player)) * self.theirMovableWeight))
    
    # Returns weighted static evaluation of the given node.
    # Uses board evaluation function L from the Thompson paper.
    # This is (number of moves J have / (number of moves opponent has * 3))
    # This was chosen for its high win rate versus a random player as well as ease of implementation
    # def staticEval(self, node):
    #     return (len(self.generateMoves(node.state, node.player)) * self.myMovesWeight) \
    #         - (len(self.generateMoves(node.state, self.opponent(node.player))) * self.theirMovesWeight)

    def crossOver(self, other):
        """
        Crosses over self with the other model to generate a child. Crosses over by having a 50/50 chance
        of child getting each feature from either parent.
        :param other: The other model to use as a parent.
        :return: The generated child.
        """
        copiedSelf = copy(self)
        for featureName in self.featuresNameList:
            useOtherModel = bool(random.getrandbits(1)) #Gets a random bool quickly from
                # http://stackoverflow.com/questions/6824681/get-a-random-boolean-in-python
            if useOtherModel:
                setattr(copiedSelf, featureName, getattr(other, featureName)) #Sets the current feature to be that of other
        return copiedSelf

    def mutate(self):
        """
        Mutates this model by randomly changing some of the values by a small value.
        """
        for featureName in self.featuresNameList:
            if random.randint(0, 100) <= self.chanceToMutate:
                setattr(self, featureName, getattr(self, featureName) +
                        random.uniform(-1.0 * (self.mutateAmount / 2.0), (self.mutateAmount / 2.00)))

    def dumpModel(self):
        """ Dumps out the model as a string in the format:
        %myMovesWeight, %theirMovesWeight, %myPiecesWeight, %theirPiecesWeight """
        return str(self.myMovesWeight) + ", " + str(self.theirMovesWeight) + ", " \
                + str(self.myPiecesWeight) + ", " + str(self.theirMovesWeight) + ", " \
                + str(self.myMovableWeight) + ", " + str(self.theirMovableWeight)

    def dumpFeatures(self):
        return "%myMovesWeight" + ", " + "%theirMovesWeight" + ", " \
                + "%myPiecesWeight" + ", " + "%theirMovesWeight" + ", " \
                + "%myMovableWeight" + ", " + "%theirMovableWeight"

    def getCorrectPercent(self):
        """
        :return: The percentage of time this model correctly predicted the opponent.
        """
        return float(self.numCorrect) / self.numTested

    def getFitness(self):
        """
        Gets the fitness as a win percentage for this model.
        Assumes that both the diversity and the correctness have been updated prior to this being run.
        """
        fitness = (self.getCorrectPercent() * self.CORRECTNESS_WEIGHT)
        fitness += (self.diversity * self.DIVERSITY_WEIGHT)
        return fitness
