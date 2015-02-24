# Analyzes models by seeing what percent of moves out of thousands of random moves they correctly predict
# Versus an opponent. Opponent must be willing to give thousands of moves for this to work.
#
# Author: Julian Jocque
# Date: 2/19/15
__author__ = 'julian'

import FigMaker, johnMinimaxEvolved, randomBoardStates, random, StaticEvalModel, os
import gakonane

class ModelAnalyzer:
    def __init__(self, attrFileName, dataFileName, opponent, generator = None):
        self.attrFile = FigMaker.AttrFile(attrFileName)
        self.dataFile = FigMaker.DataFile(dataFileName, self.attrFile)
        self.modelPlayer = johnMinimaxEvolved.MinimaxPlayer(self.attrFile.boardSize, self.attrFile.modelsDepth)
        self.modelPlayer.initialize("W")
        self.modelPlayer.model = self.getModelFromDataFile(self.dataFile)

        self.opponent = opponent
        if generator is not None:
            self.moveGenerator = generator
        else:
            self.moveGenerator = randomBoardStates.RandomStateGenerator(boardSize=self.attrFile.boardSize)

    def getModelFromDataFile(self, dataFile):
        """
        Gets the best model from the given dataFile.
        Best means that it has the highest percent correct out of the last EEA round in the file.
        In the case of a tie, chooses the last one in the datafile.
        :return: StaticEvalModel with best model from the given dataFile
        """
        numRounds = dataFile.getNumGenerations()
        start = dataFile.roundNum.index(numRounds)
        percentCorrects = []
        for i in range(start, len(dataFile.roundNum)):
            percentCorrects.append(dataFile.percentCorrect[i])

        correctMax = max(percentCorrects)
        bestIndex = len(percentCorrects) - 1
        while percentCorrects[bestIndex] != correctMax:
            bestIndex -= 1

        modelToRet = StaticEvalModel.StaticEvalModel(self.attrFile.boardSize)
        modelToRet.myMovesWeight = dataFile.myMovesWeight[bestIndex]
        modelToRet.theirMovesWeight = dataFile.theirMovesWeight[bestIndex]
        modelToRet.myPiecesWeight = dataFile.myPiecesWeight[bestIndex]
        modelToRet.theirPiecesWeight = dataFile.theirPiecesWeight[bestIndex]
        modelToRet.myMovableWeight = dataFile.myMovableWeight[bestIndex]
        modelToRet.theirMovableWeight = dataFile.theirMovableWeight[bestIndex]

        return modelToRet

    def getBestModelsFromDataFile(self, dataFile):
        """
        Gets the best models from the given dataFile.
        Best means that they have the highest percent correct out of the last EEA round in the file.
        :return: StaticEvalModels with best model from the given dataFile
        """
        models = []
        numRounds = dataFile.getNumGenerations()
        start = dataFile.roundNum.index(numRounds)
        percentCorrects = []
        for i in range(start, len(dataFile.roundNum)):
            percentCorrects.append(dataFile.percentCorrect[i])

        correctMax = max(percentCorrects)
        curr = len(percentCorrects) - 1
        while dataFile.roundNum[curr] == dataFile.roundNum[curr - 1]:
            if percentCorrects[curr] == correctMax:
                modelToAdd = StaticEvalModel.StaticEvalModel(self.attrFile.boardSize)
                modelToAdd.myMovesWeight = dataFile.myMovesWeight[curr]
                modelToAdd.theirMovesWeight = dataFile.theirMovesWeight[curr]
                modelToAdd.myPiecesWeight = dataFile.myPiecesWeight[curr]
                modelToAdd.theirPiecesWeight = dataFile.theirPiecesWeight[curr]
                modelToAdd.myMovableWeight = dataFile.myMovableWeight[curr]
                modelToAdd.theirMovableWeight = dataFile.theirMovableWeight[curr]
                models.append(modelToAdd)
            curr -= 1

        return models

    def analyze(self, N):
        """
        Analyzes self.modelPlayer versus self.opponent by trying many random puzzles and seeing how much
        they agree on the result.
        :return: None
        """
        testedPuzzles = []
        try:
            count = 0
            while count < N:
                side = random.choice(["W", "B"])
                board = self.moveGenerator.getRandom(side)
                if board not in testedPuzzles: #Skip duplicates
                    testedPuzzles.append(board)
                    self.opponent.setSide(side)
                    oppMove = self.opponent.getMove(board)
                    self.modelPlayer.setSide(side)
                    modelMove = self.modelPlayer.getMove(board)
                    self.modelPlayer.model.numTested += 1

                    if oppMove == modelMove:
                        self.modelPlayer.model.numCorrect += 1
                    # if self.modelPlayer.model.numTested % 100 == 0:
                    #     print "Just tested " + str(self.modelPlayer.model.numTested)
                    #     print str(self.modelPlayer.model.getCorrectPercent() * 100.0) + " % correct!"
                count += 1
        except KeyboardInterrupt:
            pass
        print "Tested " + str(self.modelPlayer.model.numTested) + " puzzles"
        print str(self.modelPlayer.model.getCorrectPercent() * 100.0) + " % correct!"

        return self.modelPlayer.model.getCorrectPercent() * 100.0

def folderAnalyzer(folderName):
    dataFileList = sorted(os.listdir(folderName + "/data/"))
    attrFileList = sorted(os.listdir(folderName + "/attr/"))
    moveGen = randomBoardStates.RandomStateGenerator(boardSize=6)

    for i in range(len(dataFileList)):
        modelsPercentCorrects = {}
        print "Now on " + str(i) + ": " + str(dataFileList[i])
        attrFileName = folderName + "attr/" + attrFileList[i]
        dataFileName = folderName + "data/" + dataFileList[i]
        attrFile= FigMaker.AttrFile(attrFileName)
        opponent = getOpponentFromAttrFile(attrFile)
        analyzer = ModelAnalyzer(attrFileName, dataFileName, opponent, generator=moveGen)
        bestModels = analyzer.getBestModelsFromDataFile(analyzer.dataFile)
        print str(len(bestModels)) + " models to analyze for this file."
        for model in bestModels:
            analyzer.modelPlayer.model = model

            percentCorrect = analyzer.analyze(250)
            modelsPercentCorrects[model] = percentCorrect

        bestEntry = max(modelsPercentCorrects.items(), key = lambda x: x[1])
        print "Best model for the file was: " + str(bestEntry[0])
        print "Percent was: " + str(bestEntry[1])


def analyzeInternetPlayer():
    dataFileName = "data/fromInternet/data/data-2015-02-18 19_53_31.csv"
    attrFileName = "data/fromInternet/attr/attr-2015-02-18 19_53_31.csv"

    # attrFile = FigMaker.AttrFile(attrFileName)

    opponent = getOpponentFromOnlineAttrFile()
    analyzer = ModelAnalyzer(attrFileName, dataFileName, opponent)

    analyzer.analyze(1000)

def getOpponentFromOnlineAttrFile():
    opponent = gakonane.KOnane(6, 3)
    opponent.initialize("W")

    return opponent

def getOpponentFromAttrFile(attrFile):
    opponent = johnMinimaxEvolved.MinimaxPlayer(attrFile.boardSize, attrFile.oppDepth)
    opponent.initialize("W")

    opponent.myMovesWeight = attrFile.oppMyMovesWeight
    opponent.theirMovesWeight = attrFile.oppTheirMovesWeight
    opponent.myPiecesWeight = attrFile.oppMyPiecesWeight
    opponent.theirPiecesWeight = attrFile.oppTheirPiecesWeight
    opponent.myMovableWeight = attrFile.oppMyMovableWeight
    opponent.theirMovableWeight = attrFile.oppTheirMovableWeight

    return opponent


if __name__ == "__main__":
    folderAnalyzer("data/currEEA/")
    # analyzeInternetPlayer()