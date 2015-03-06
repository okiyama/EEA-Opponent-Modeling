## Figure generator for the data produced by EEA.py.
## Not generic.
##
## Author: Julian Jocque
## Date: 10/13/14

try:
    from pylab import *
    import matplotlib.lines as mlines
    import seaborn as sns
    import numpy as np
except:
    print "Unable to import things in FigMaker! Probably a pypy issue."
import datetime, os, re, sys

#TODO:
# Make it show a line where a new round starts on the generations graphs
class FigMaker:
    def __init__(self):
        self.USING_ATTR = False
        self.dataFolder = "data/currEEA/data/"
        self.attrFolder = "data/currEEA/attr/"
        self.outPutFile = "" + str(datetime.datetime.time(datetime.datetime.now())) + ".png"

        self.data = []
        self.attr = []
        self.timeTaken = []
        self.maxFitness = []

        if self.dataFolder is not None:
            # self.dataFileList = [sorted(os.listdir(self.dataFolder))[-1]]
            # self.attrFileList = [sorted(os.listdir(self.attrFolder))[-1]]
            self.dataFileList = sorted(os.listdir(self.dataFolder))
            self.attrFileList = sorted(os.listdir(self.attrFolder))
        else:
            self.dataFileList = None
            self.attrFileList = None

        self.getData()

    def getData(self):
        """
        Pulls the data from all of the EEA data files so we can work with it.
        """
        if self.USING_ATTR:
            for fileName in self.attrFileList:
                num_lines = sum(1 for line in open(self.attrFolder + fileName))
                if num_lines > 1: #Ignore empty files
                    attrFromFile = AttrFile(self.attrFolder + fileName)
                    self.attr.append(attrFromFile)
                else:
                    print fileName + " didn't contain any data."

        for i in range(len(self.dataFileList)):
            fileName = self.dataFileList[i]
            num_lines = sum(1 for line in open(self.dataFolder + fileName))
            if num_lines > 1: #Ignore empty files
                print fileName
                if self.USING_ATTR:
                    dataFromFile = DataFile(self.dataFolder + fileName, self.attr[i])
                else:
                    dataFromFile = DataFile(self.dataFolder + fileName, None)
                self.data.append(dataFromFile)
                self.timeTaken.append(dataFromFile.getTimeTaken())
                self.maxFitness.append(dataFromFile.getNMaxFitnessValues(5))
            else:
                print fileName + " didn't contain any data."



                #print self.maxFitness
                #print self.data
                #print self.timeTaken

    def outputToFile(self):
        """
        Outputs the data collected to a file.
        """
        outputFile = open(self.outPutFile, "w")
        for i in range(len(self.dataFileList)):
            outputFile.write("File: " + self.dataFileList[i] + "\n")
            outputFile.write("Time taken to generate: " + self.timeTaken[i] + "\n")
            outputFile.write("Number of generations: " + self.data[i].getNumGenerations() + "\n")
            outputFile.write("Best fitness values: \n")
            for value in self.data[i].getNMaxFitnessLines(5):
                outputFile.write("\t" + str(value) + "\n")
            outputFile.write("\n\n\n")

        outputFile.close()
        print "Outputted analysis to: " + self.outPutFile

    def generateAllGraphs(self):
        """
        Generates all the graph figures.
        """
        for dataFile in self.data:
            dataFile.generateMinMaxMedianFitnessOverTrials(showRoundBreaks = False)
            dataFile.generateMinMaxMedianDiversityOverTrials(showRoundBreaks = True)
            dataFile.generateMinMaxMedianPercentCorrectOverTrials(showRoundBreaks = True)
            # dataFile.generateFitnessOverTrials()
            # dataFile.generateFitnessOverTimes()
            # dataFile.generateAvgFitnessOverTrials()
            # dataFile.generateAvgFitnessOverTimes()
            # dataFile.generateAvgFitnessOverRounds()
            # dataFile.generateMaxFitnessOverTrials()
            # dataFile.generateMaxFitnessOverTimes()
            # dataFile.generateMaxFitnessOverRounds()
            # dataFile.generateDiversityOverTrials()
            # dataFile.generateMaxDiversityOverTrials()
            # dataFile.generateMaxDiversityOverRounds()
            # dataFile.generateAvgDiversityOverTrials()
            # dataFile.generateAvgDiversityOverRounds()
            dataFile.generateAvgPercentCorrectOverTrials(showRoundBreaks = True)


"""
Encapsulates the attributes from one EEA data file.
"""
class AttrFile:
    def __init__(self, fileName):
        self.numTestsPerRound = 0
        self.modelsDepth = 0
        self.boardSize = 0
        self.numModels = 0
        self.opponentName = ""
        self.oppMyMovesWeight = 0.0
        self.oppTheirMovesWeight = 0.0
        self.oppMyPiecesWeight = 0.0
        self.oppTheirPiecesWeight = 0.0
        self.oppMyMovableWeight = 0.0
        self.oppTheirMovableWeight = 0.0
        self.oppDepth = 0
        self.fileName = fileName

        self.createData()

    def createData(self):
        """
        Pulls the data from one attribute file so we can work with it.
        """
        regex = "(.*), (.*), (.*), (.*)"
        dataFile = open(self.fileName, "r")
        #dataFile.readline()
        dataFile.readline()
        modelAttrs = dataFile.readline()
        matched = re.match(regex, modelAttrs)

        self.numTestsPerRound = int(matched.group(1))
        self.modelsDepth = int(matched.group(2))
        self.boardSize = int(matched.group(3))
        self.numModels = int(matched.group(4))

        regex = "Name: (.*)"
        dataFile.readline()
        oppName = dataFile.readline()
        matched = re.match(regex, oppName)
        self.opponentName = matched.group(1)

        dataFile.readline()
        opponentInfo = dataFile.readline()
        regex = "(.*), (.*), (.*), (.*), (.*), (.*), (.*)"
        matched = re.match(regex, opponentInfo)
        if matched:
            self.oppMyMovesWeight = float(matched.group(1))
            self.oppTheirMovesWeight = float(matched.group(2))
            self.oppMyPiecesWeight = float(matched.group(3))
            self.oppTheirPiecesWeight = float(matched.group(4))
            self.oppMyMovableWeight = float(matched.group(5))
            self.oppTheirMovableWeight = float(matched.group(6))
            self.oppDepth = int(matched.group(7))

        dataFile.close()

"""
Encapsulates the data from one EEA data file.
"""
class DataFile:
    def __init__(self, fileName, attrFile, outputToFile = True):
        self.roundNum = []
        self.fitness = []
        self.myMovesWeight = []
        self.theirMovesWeight = []
        self.myPiecesWeight = []
        self.theirPiecesWeight = []
        self.myMovableWeight = []
        self.theirMovableWeight = []
        self.roundEndTime = []
        self.generationNum = []
        self.diversity = []
        self.percentCorrect = []
        self.attrs = attrFile
        self.fileName = fileName
        self.figFolder = "figures/currEEA/"
        self.outputToFile = outputToFile

        self.createData()
        self.numDataPoints = len(self.roundNum)

    def getDataNumber(self, i):
        """
        Gets the ith data as a tuple in the same format as in EEA data files.
        """
        return (self.roundNum[i], self.fitness[i], self.myMovesWeight[i], self.theirMovesWeight[i], self.myPiecesWeight[i],
                self.theirPiecesWeight[i], self.myMovableWeight[i], self.theirMovableWeight[i],
                self.roundEndTime[i], self.generationNum[i], self.diversity[i])

    def getNMaxFitnessValues(self, N):
        """
        Gets the N max fitness values
        """
        #print sorted(self.fitness)[:-N:-1]
        return sorted(self.fitness)[:-N-1:-1]

    def getNMaxFitnessLines(self, N):
        """
        Gets the full data of the N best fitness values from this file as a tuple.
        """
        toRet = []
        bestFitness = self.getNMaxFitnessValues(N)
        for i in range(len(bestFitness)):
            currIndex = self.fitness.index(bestFitness[i])
            toRet.append(self.getDataNumber(currIndex))

        return toRet

    def getNumGenerations(self):
        """
        Gives the number of generations that this pop data file contains.
        """
        return int(self.roundNum[-1])

    def createData(self):
        """
        Pulls the data from all of the pop data files so we can work with it.
        """
        regex = "(.*), (.*), (.*), (.*), (.*), (.*), (.*), (.*), (.*), (.*), (.*), (.*)"
        dataFile = open(self.fileName, "r")
        #dataFile.readline()
        dataFile.readline()
        for line in dataFile:
            # print line
            matched = re.match(regex, line)
            if matched:
                self.appendData(matched)

        dataFile.close()

    def appendData(self, match):
        """
        Appends the given regex match to the data of this.
        """
        try:
            self.roundNum.append(int(match.group(1)))
            self.fitness.append(float(match.group(2)))
            self.myMovesWeight.append(float(match.group(3)))
            self.theirMovesWeight.append(float(match.group(4)))
            self.myPiecesWeight.append(float(match.group(5)))
            self.theirPiecesWeight.append(float(match.group(6)))
            self.myMovableWeight.append(float(match.group(7)))
            self.theirMovableWeight.append(float(match.group(8)))
            self.roundEndTime.append(match.group(9))
            self.generationNum.append(int(match.group(10)))
            self.diversity.append(float(match.group(11)))
            self.percentCorrect.append(float(match.group(12)))
        except:
            print match.groups()
            sys.exit(0)

    def getTimeTaken(self):
        """
        Gets the absolute amount of time taken for this pop data file to be created
        """
        #print self.time
        timeSorted = sorted(self.roundEndTime)
        #print "End: " + timeSorted[-1] + ", start: " + timeSorted[0]
        return str(self.getTimeDifference(timeSorted[-1], timeSorted[0]))

    def getTimeDifference(self, time1, time2):
        """
        Gets difference between two times of format:
        Hour:Minute:Second.Microseconds
        Does time1 - time2.
        """
        timeFormat = "%H:%M:%S.%f"
        endTime = datetime.datetime.strptime(time1, timeFormat)
        startTime = datetime.datetime.strptime(time2, timeFormat)
        return endTime - startTime

    def generateFeatureOverX(self, feature, xAxis, xLabel, yLabel, title, filename = None):
        """
        Generates a graph of the given feature, using the given variable for the xAxis.
        xAxis will be generationNum, roundNum or time.
        """
        X = np.array(range(len(xAxis)))
        Y = np.array(feature)
        plot(X, Y)

        xlabel(xLabel)
        ylabel(yLabel)
        if self.attrs:
            title = title + " versus " + self.attrs.opponentName
        suptitle(title)

        if not self.outputToFile:
            show()
        else:
            savefig(self.figFolder + self.fileName[23:len(self.fileName)-4] + filename + ".png", format="png")
        clf()

    def generateAvgFeatureOverX(self, feature, xAxis, xLabel, yLabel, title, showRoundBreaks = True, filename = None):
        """
        Generates a graph of the average for the given feature over the given xAxis.
        xAxis is something like self.generationNum, self.roundNum
        fature is something like self.fitness
        """
        averages = []
        absoluteMax = max(feature)
        roundBreaks = self.getRoundBreaks()
        breakPlots = []
        tempAvg = 0.0
        currGenNum = 1
        counter = 0
        for i in range(len(xAxis)):
            tempAvg += float(feature[i])
            counter += 1

            if showRoundBreaks and i in roundBreaks:
                breakPlots.append([currGenNum, currGenNum])
                breakPlots.append([0, absoluteMax])

            if i == len(xAxis)-1:
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                currGenNum += 1
                break

            if xAxis[i] != xAxis[i+1]:
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                tempAvg = 0
                counter = 0
                currGenNum += 1

        #print averages

        plot(range(len(averages)+1)[1:], averages)

        if breakPlots != []:
            print "plotting" + str(breakPlots)
            plot(breakPlots[0], breakPlots[1], "k-", lw=2, label="New EEA Round Begins")

            for i in range(2, len(breakPlots), 2):
                plot(breakPlots[i], breakPlots[i+1], "k-", lw=2)

        # print xAxis[-1]
        xlim([1,xAxis[-1]])
        xlabel(xLabel)
        ylabel(yLabel)
        legend()

        if self.attrs:
            title += " versus " + self.attrs.opponentName
        suptitle(title)

        if not self.outputToFile:
            show()
        else:
            savefig(self.figFolder + self.fileName[23:len(self.fileName)-4] + filename + ".png", format="png")
        clf()

    def generateMaxFeatureOverX(self, feature, xAxis, xLabel, yLabel, title, filename = None):
        """
        Generates a graph of the maximum of the given feature over the given xAxis feature.
        xAxis is something like self.generationNum, self.roundNum
        fature is something like self.fitness
        """
        maxes = []
        tempMax = []
        for i in range(len(xAxis)):
            tempMax.append(float(feature[i]))
            if i == len(xAxis)-1:
                maxes.append(max(tempMax))
                tempMax = []
                break

            if xAxis[i] != xAxis[i+1]:
                maxes.append(max(tempMax))
                tempMax = []

        #print averages

        plot(range(len(maxes)+1)[1:], maxes)
        xlim([1,xAxis[-1]])
        xlabel(xLabel)
        ylabel(yLabel)

        if self.attrs:
            title += " " + self.attrs.opponentName
        suptitle(title)

        if not self.outputToFile:
            show()
        else:
            savefig(self.figFolder + self.fileName[23:len(self.fileName)-4] + filename + ".png", format="png")
        clf()

    def generateMinMaxMedianFeatureOverX(self, feature, xAxis, xLabel, yLabel, title, showRoundBreaks = True, filename = None):
        """
        Generates a graph of the maximum, minimum and median of the given feature over the given xAxis feature.
        xAxis is something like self.generationNum, self.roundNum
        feature is something like self.fitness, self.diversity, self.percentCorrect
        """

        absoluteMax = max(feature)
        maxes = []
        mins = []
        medians = []
        currGen = []
        currGenNum = 1
        roundBreaks = self.getRoundBreaks()
        breakPlots = []
        for i in range(len(xAxis)):
            currGen.append(feature[i])

            if showRoundBreaks and i in roundBreaks:
                breakPlots.append([currGenNum, currGenNum])
                breakPlots.append([0, absoluteMax])

            if i == len(xAxis)-1:
                sortedGen = sorted(currGen)
                maxes.append(sortedGen[-1])
                mins.append(sortedGen[0])
                medians.append(sortedGen[len(sortedGen) / 2])
                currGen = []
                currGenNum += 1
                break

            if xAxis[i] != xAxis[i+1]:
                sortedGen = sorted(currGen)
                maxes.append(sortedGen[-1])
                mins.append(sortedGen[0])
                medians.append(sortedGen[len(sortedGen) / 2])
                currGen = []
                currGenNum += 1

        xMax = range(len(maxes)+1)[1:]
        plot(xMax, medians, label="Median")
        plot(xMax, mins, label="Min")
        plot(xMax, maxes, label="Max")

        if breakPlots != []:
            plot(breakPlots[0], breakPlots[1], "k-", lw=2, label="New EEA Round Begins")

            for i in range(2, len(breakPlots), 2):
                plot(breakPlots[i], breakPlots[i+1], "k-", lw=2)

        xlim([1,xAxis[-1]])
        if showRoundBreaks:
            ylim([0, absoluteMax])
        xlabel(xLabel)
        ylabel(yLabel)
        legend(loc=4)

        if self.attrs:
            title += " " + self.attrs.opponentName
        suptitle(title)

        if not self.outputToFile:
            show()
        else:
            savefig(self.figFolder + self.fileName[23:len(self.fileName)-4] + filename + ".png", format="png")
        clf()

    def getRoundBreaks(self):
        """
        Returns what indices are the start of a new round.
        """
        breaks = []
        for i in range(len(self.roundNum) - 1):
            if self.roundNum[i + 1] != self.roundNum[i]:
                breaks.append(i + 1)

        print "num rounds: " + str(self.roundNum[-1])
        print breaks
        return breaks

    def generateFitnessOverTrials(self):
        """
        Generates a graph of the fitness of this pop data file over the trials.
        """
        self.generateFeatureOverX(self.fitness, self.roundNum,
                                  "Model number", "Fitness value", "Individual model fitness throughout experiment"
                                  ,"fitnessOverTrials")

    def generateAvgFitnessOverTrials(self):
        """
        Generates a graph of the average fitness of a generation over the trials.
        """
        self.generateAvgFeatureOverX(self.fitness, self.generationNum,
                                     "Generation Number", "Average Fitness", "Average fitness of each generation",
                                     "avgFitnessOverTrials")

    def generateAvgFitnessOverRounds(self):
        """
        Generates a graph of the average fitness of a round over the trials.
        """
        self.generateAvgFeatureOverX(self.fitness, self.roundNum,
                                     "Round Number", "Average Fitness", "Average fitness of each round",
                                     "avgFitnessOverRounds")

    def generateMaxFitnessOverTrials(self):
        """
        Generates a graph of the maximum fitness of a generation over the trials.
        """
        self.generateMaxFeatureOverX(self.fitness, self.generationNum,
                                     "Generation Number", "Generation Max Fitness",
                                     "Generation Max Fitness for each generation",
                                     "maxFitnessOverTrials")

    def generateMaxFitnessOverRounds(self):
        """
        Generates a graph of the maximum fitness of a generation over the trials.
        """
        self.generateMaxFeatureOverX(self.fitness, self.roundNum,
                                     "Round Number", "Round Max Fitness",
                                     "Round Max Fitness for each generation",
                                     "maxFitnessOverRounds")

    def generateMinMaxMedianFitnessOverTrials(self, showRoundBreaks = True):
        """
        Generates a graph of the maximum fitness of a generation over the trials.
        """
        self.generateMinMaxMedianFeatureOverX(self.fitness, self.generationNum,
                                              "Generation Number", "Fitness",
                                              "Fitness for each generation", showRoundBreaks,
                                              "minMaxMedFitnessOverTrials")

    def generateMinMaxMedianFitnessOverRounds(self, showRoundBreaks = True):
        """
        Generates a graph of the maximum fitness of a generation over the trials.
        """
        self.generateMinMaxMedianFeatureOverX(self.fitness, self.roundNum,
                                              "Round Number", "Fitness",
                                              "Fitness for each round", showRoundBreaks,
                                              "minMaxMedFitnessOverRounds")

    def generateDiversityOverTrials(self):
        """
        Generates a graph of the diversity of this pop data file over the trials.
        """
        self.generateFeatureOverX(self.diversity, self.roundNum,
                                  "Model number", "Diversity Value", "Individual model diversity throughout experiment",
                                  filename="diversityOverTrials")

    def generateAvgDiversityOverTrials(self):
        """
        Generates a graph of the average diversity of the models of a generation over the trials.
        """
        self.generateAvgFeatureOverX(self.diversity, self.generationNum,
                                     "Generation Number", "Average Diversity", "Average diversity of each generation",
                                     filename="avgDiversityOverTrials")

    def generateAvgDiversityOverRounds(self):
        """
        Generates a graph of the average diversity of the models of a round over the trials.
        """
        self.generateAvgFeatureOverX(self.diversity, self.roundNum,
                                     "Round Number", "Average Diversity", "Average diversity of each round",
                                     filename="avgDiversityOverRounds")

    def generateMaxDiversityOverTrials(self):
        """
        Generates a graph of the maximum fitness of a generation over the trials.
        """
        self.generateMaxFeatureOverX(self.diversity, self.generationNum,
                                     "Generation Number", "Generation Max Diversity",
                                     "Generation Max Diversity for each generation",
                                     filename="maxDiversityOverTrials")

    def generateMaxDiversityOverRounds(self):
        """
        Generates a graph of the maximum fitness of a generation over the trials.
        """
        self.generateMaxFeatureOverX(self.diversity, self.roundNum,
                                     "Round Number", "Round Max Diversity",
                                     "Round Max Diversity for each generation",
                                     filename="maxDivOverRounds")

    def generateMinMaxMedianDiversityOverTrials(self, showRoundBreaks = True):
        """
        Generates a graph of the min/max/median fitness of a generation over the trials.
        """
        self.generateMinMaxMedianFeatureOverX(self.diversity, self.generationNum,
                                              "Generation Number", "Diversity",
                                              "Diversity for each generation", showRoundBreaks,
                                              filename="minxMaxMedDivOverTrials")

    def generateMinMaxMedianDiversityOverRounds(self, showRoundBreaks = True):
        """
        Generates a graph of the min/max/median of a generation over the trials.
        """
        self.generateMinMaxMedianFeatureOverX(self.diversity, self.roundNum,
                                              "Round Number", "Diversity",
                                              "Diversity for each round", showRoundBreaks,
                                              filename="minMaxMedDivOverRounds")

    def generatePercentCorrectOverTrials(self):
        """
        Generates a graph of the percent correct of this pop data file over the trials.
        """
        self.generateFeatureOverX(self.percentCorrect, self.roundNum,
                                  "Model number", "Percent Correct", "Individual model percent correct throughout experiment",
                                  filename="percentCorrOverTrials")

    def generateAvgPercentCorrectOverTrials(self, showRoundBreaks = True):
        """
        Generates a graph of the average percent correct of the models of a generation over the trials.
        """
        self.generateAvgFeatureOverX(self.percentCorrect, self.generationNum,
                                     "Generation Number", "Average Percent Correct",
                                     "Average percent correct of each generation", showRoundBreaks,
                                     filename="avgPercentCorrOverTrials")

    def generateAvgPercentCorrectOverRounds(self, showRoundBreaks = True):
        """
        Generates a graph of the average percent of the models of a round over the trials.
        """
        self.generateAvgFeatureOverX(self.percentCorrect, self.roundNum,
                                     "Round Number", "Average Percent Correct",
                                     "Average percent correct of each round", showRoundBreaks,
                                     filename="avgPercentCorrectOverRounds")

    def generateMaxPercentCorrectOverTrials(self, showRoundBreaks = True):
        """
        Generates a graph of the maximum percent correct of a generation over the trials.
        """
        self.generateMaxFeatureOverX(self.percentCorrect, self.generationNum,
                                     "Generation Number", "Generation Max Percent Correct",
                                     "Generation Max percent correct for each generation", showRoundBreaks,
                                     filename="maxPercentCorrectOverTrials")

    def generateMaxPercentCorrectOverRounds(self):
        """
        Generates a graph of the maximum percent correct of a generation over the trials.
        """
        self.generateMaxFeatureOverX(self.percentCorrect, self.roundNum,
                                     "Round Number", "Round Max Percent Correct",
                                     "Round Max Percent Correct for each generation",
                                     filename="maxPercentCorrectOverRounds")

    def generateMinMaxMedianPercentCorrectOverTrials(self, showRoundBreaks = True):
        """
        Generates a graph of the min/max/median percent correct of a generation over the trials.
        """
        self.generateMinMaxMedianFeatureOverX(self.percentCorrect, self.generationNum,
                                              "Generation Number", "Percent Correct",
                                              "Generation percent correct for each generation", showRoundBreaks,
                                              filename="minMaxMedPercentCorrOverTrials")

    def generateMinMaxMedianPercentCorrectOverRounds(self, showRoundBreaks = True):
        """
        Generates a graph of the min/max/median percent correct of a generation over the trials.
        """
        self.generateMinMaxMedianFeatureOverX(self.percentCorrect, self.roundNum,
                                              "Round Number", "Percent Correct",
                                              "Round Percent Correct for each generation", showRoundBreaks,
                                              filename="minMaxMedPercentCorrOverRounds")

    def generateAvgFitnessOverTimes(self):
        """
        Generates a graph of the average fitness of a generation over time.
        """
        timeDiffs = []
        averages = []
        tempAvg = 0.0
        counter = 0
        for i in range(len(self.roundNum)):
            tempAvg += float(self.fitness[i])
            counter += 1
            if i == len(self.roundNum)-1:
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                timeDiffs.append(self.getTimeDifference(self.roundEndTime[i],self.roundEndTime[0]).seconds)
                break

            if self.roundNum[i] != self.roundNum[i+1]:
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                tempAvg = 0
                counter = 0
                timeDiffs.append(self.getTimeDifference(self.roundEndTime[i],self.roundEndTime[0]).seconds)

        plot(timeDiffs, averages)
        #xlim([1,25])
        xlabel("Seconds Since Testing Began")
        ylabel("Generation's Average Fitness")

        title = "Generational Average Fitness versus Time"
        if self.attrs:
            title += " versus " + self.attrs.opponentName
        suptitle(title)

        if not self.outputToFile:
            show()
        else:
            savefig(self.figFolder + self.fileName + "avgFitOverTimes")

    def generateMaxFitnessOverTimes(self):
        """
        Generates a graph of the maximum fitness of a generation over time.
        """
        timeDiffs = []
        maxes = []
        tempMax = []
        for i in range(len(self.roundNum)):
            tempMax.append(float(self.fitness[i]))
            if i == len(self.roundNum)-1:
                maxes.append(max(tempMax))
                tempMax = []
                timeDiffs.append(self.getTimeDifference(self.roundEndTime[i],self.roundEndTime[0]).seconds)
                break

            if self.roundNum[i] != self.roundNum[i+1]:
                maxes.append(max(tempMax))
                tempMax = []
                timeDiffs.append(self.getTimeDifference(self.roundEndTime[i],self.roundEndTime[0]).seconds)

        plot(timeDiffs, maxes)
        #xlim([1,25])
        xlabel("Seconds Since Testing Began")
        ylabel("Generation's Maximum Fitness")

        title = "Generational Maximum Fitness versus Time"
        if self.attrs:
            title += " versus " + self.attrs.opponentName

        suptitle(title)

        if not self.outputToFile:
            show()
        else:
            savefig(self.figFolder + self.fileName + "maxFitOverTime")

    def generateFitnessOverTimes(self):
        """
        Generates a graph of the fitness of this pop data file over the time taken to generate it.
        """
        timeDiffs = []
        for timeVal in self.roundEndTime:
            timeDiffs.append(self.getTimeDifference(timeVal,self.roundEndTime[0]).seconds)
        plot(timeDiffs, self.fitness)

        xlabel("Seconds Since Testing Began")
        ylabel("Fitness of Trial")

        title = "Fitness of Trials Versus Time Since Testing Began"
        if self.attrs:
            title += " versus " + self.attrs.opponentName

        suptitle(title)

        if not self.outputToFile:
            show()
        else:
            savefig(self.figFolder + self.fileName + "maxFitOverTime")

if __name__ == "__main__":
    maker = FigMaker()
    #analyzer.outputToFile()
    maker.generateAllGraphs()