# A model that can be evoled for a static evaluator
# Julian Jocque
# 10/3/14

import random
from updatedKonane import *

class StaticEvalModel(Konane):
    def __init__(self, size):
        self.size = size
        self.myMovesWeight = 1.0
        self.theirMovesWeight = 1.0
        self.myPiecesWeight = 1.0
        self.theirPiecesWeight = 1.0
        self.myMovableWeight = 1.0
        self.theirMovableWeight = 1.0
        self.chanceToMutate = 15 #as a percent
        self.numCorrect = 0
        self.numTested = 0
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
        pass

    def mutate(self):
        for featureName in ["myMovesWeight", "theirMovesWeight", "myPiecesWeight", "theirPiecesWeight", 
                        "myMovableWeight", "theirMovableWeight"]:
            if random.randint(0, 100) <= self.chanceToMutate:
                setattr(self, featureName, getattr(self, featureName) + random.uniform(-0.5, 0.5))

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

    def getFitness(self):
        """ Gets the fitness as a win percentage for this model. """
        return float(self.numCorrect / self.numTested)
