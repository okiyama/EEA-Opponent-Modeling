## Figure generator for the data produced by EEA.py.
## Not generic.
##
## Author: Julian Jocque
## Date: 10/13/14

from pylab import *
import datetime, os, re
import numpy as np

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
            # dataFile.hackyFunction()
            # dataFile.generateFitnessOverTrials()
            # dataFile.generateFitnessOverTimes()
            dataFile.generateAvgFitnessOverTrials()
            # dataFile.generateAvgFitnessOverTimes()
            # dataFile.generateMaxFitnessOverTrials()
            # dataFile.generateMaxFitnessOverTimes()


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

        self.numTestsPerRound = matched.group(1)
        self.modelsDepth = matched.group(2)
        self.boardSize = matched.group(3)
        self.numModels = matched.group(4)

        regex = "Name: (.*)"
        dataFile.readline()
        oppName = dataFile.readline()
        matched = re.match(regex, oppName)
        self.opponentName = matched.group(1)

        dataFile.readline()
        opponentInfo = dataFile.readline()
        regex = "(.*), (.*), (.*), (.*), (.*), (.*), (.*)"
        matched = re.match(regex, opponentInfo)
        self.oppMyMovesWeight = matched.group(1)
        self.oppTheirMovesWeight = matched.group(2)
        self.oppMyPiecesWeight = matched.group(3)
        self.oppTheirPiecesWeight = matched.group(4)
        self.oppMyMovableWeight = matched.group(5)
        self.oppTheirMovableWeight = matched.group(6)

        dataFile.close()

"""
Encapsulates the data from one EEA data file.
"""
class DataFile:
    
    def __init__(self, fileName, attrFile):
        self.genNum = []
        self.fitness = []
        self.myMovesWeight = []
        self.theirMovesWeight = []
        self.myPiecesWeight = []
        self.theirPiecesWeight = []
        self.myMovableWeight = []
        self.theirMovableWeight = []
        self.roundEndTime = []
        self.attrs = attrFile
        self.fileName = fileName
        
        self.createData()
        self.numDataPoints = len(self.genNum)
    
    def getDataNumber(self, i):
        """
        Gets the ith data as a tuple in the same format as in EEA data files.
        """
        return (self.genNum[i], self.fitness[i], self.myMovesWeight[i], self.theirMovesWeight[i], self.myPiecesWeight[i],
                self.theirPiecesWeight[i], self.myMovableWeight[i], self.theirMovableWeight[i], self.roundEndTime[i])
        
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
        return int(self.genNum[-1])
    
    def createData(self):
        """
        Pulls the data from all of the pop data files so we can work with it.
        """
        regex = "(.*), (.*), (.*), (.*), (.*), (.*), (.*), (.*), (.*)"
        dataFile = open(self.fileName, "r")
        #dataFile.readline()
        dataFile.readline()
        for line in dataFile:
            # print line
            matched = re.match(regex, line)
            if matched:
                self.appendData(matched)
        
        dataFile.close()
    
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
                
    def appendData(self, match):
        """
        Appends the given regex match to the data of this.
        """
        self.genNum.append(match.group(1))
        self.fitness.append(match.group(2))
        self.myMovesWeight.append(match.group(3))
        self.theirMovesWeight.append(match.group(4))
        self.myPiecesWeight.append(match.group(5))
        self.theirPiecesWeight.append(match.group(6))
        self.myMovableWeight.append(match.group(7))
        self.theirMovableWeight.append(match.group(8))
        self.roundEndTime.append(match.group(9))

    def generateFitnessOverTrials(self):
        """
        Generates a graph of the fitness of this pop data file over the trials.
        """
        X = np.array(range(self.numDataPoints))
        Y = np.array(self.fitness)
        plot(X, Y)

        xlabel("Trial Number")
        ylabel("Fitness Value")
        suptitle("Fitness Value of Each Trial Versus " + self.attrs.opponentName)

        show()

    def generateAvgFitnessOverTrials(self):
        """
        Generates a graph of the average fitness of a generation over the trials.
        """
        averages = []
        tempAvg = 0.0
        counter = 0
        for i in range(len(self.genNum)):
            tempAvg += float(self.fitness[i])
            counter += 1
            if i == len(self.genNum)-1:
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                break

            if self.genNum[i] != self.genNum[i+1]:
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                tempAvg = 0
                counter = 0

        #print averages

        plot(range(len(averages)+1)[1:], averages)
        xlim([1,self.getNumGenerations()])
        xlabel("Generation Number")
        ylabel("Generation's Average Fitness")
        if self.attrs:
            suptitle("Generational Average Fitness versus Generation Number Versus " + self.attrs.opponentName)
        else:
            suptitle("Generational Average Fitness versus Generation Number")

        show()

    def generateMaxFitnessOverTrials(self):
        """
        Generates a graph of the maximum fitness of a generation over the trials.
        """
        maxes = []
        tempMax = []
        for i in range(len(self.genNum)):
            tempMax.append(float(self.fitness[i]))
            if i == len(self.genNum)-1:
                maxes.append(max(tempMax))
                tempMax = []
                break

            if self.genNum[i] != self.genNum[i+1]:
                maxes.append(max(tempMax))
                tempMax = []

        #print averages

        plot(range(len(maxes)+1)[1:], maxes)
        xlim([1,self.getNumGenerations()])
        xlabel("Generation Number")
        ylabel("Generation's Maximum Fitness")
        suptitle("Generational Maximum Fitness versus Generation Number Versus " + self.attrs.opponentName)

        show()

    def generateAvgFitnessOverTimes(self):
        """
        Generates a graph of the average fitness of a generation over time.
        """
        timeDiffs = []
        averages = []
        tempAvg = 0.0
        counter = 0
        for i in range(len(self.genNum)):
            tempAvg += float(self.fitness[i])
            counter += 1
            if i == len(self.genNum)-1:
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                timeDiffs.append(self.getTimeDifference(self.roundEndTime[i],self.roundEndTime[0]).seconds)
                break

            if self.genNum[i] != self.genNum[i+1]:
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                tempAvg = 0
                counter = 0
                timeDiffs.append(self.getTimeDifference(self.roundEndTime[i],self.roundEndTime[0]).seconds)

        plot(timeDiffs, averages)
        #xlim([1,25])
        xlabel("Seconds Since Testing Began")
        ylabel("Generation's Average Fitness")
        suptitle("Generational Average Fitness versus Time Versus " + self.attrs.opponentName)

        show()

    def generateMaxFitnessOverTimes(self):
        """
        Generates a graph of the maximum fitness of a generation over time.
        """
        timeDiffs = []
        maxes = []
        tempMax = []
        for i in range(len(self.genNum)):
            tempMax.append(float(self.fitness[i]))
            if i == len(self.genNum)-1:
                maxes.append(max(tempMax))
                tempMax = []
                timeDiffs.append(self.getTimeDifference(self.roundEndTime[i],self.roundEndTime[0]).seconds)
                break

            if self.genNum[i] != self.genNum[i+1]:
                maxes.append(max(tempMax))
                tempMax = []
                timeDiffs.append(self.getTimeDifference(self.roundEndTime[i],self.roundEndTime[0]).seconds)

        plot(timeDiffs, maxes)
        #xlim([1,25])
        xlabel("Seconds Since Testing Began")
        ylabel("Generation's Maximum Fitness")
        suptitle("Generational Maximum Fitness versus Time Versus " + self.attrs.opponentName)

        show()

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
        title("Fitness of Trials Versus Time Since Testing Began Versus " + self.attrs.opponentName)

        show()
    
if __name__ == "__main__":
    maker = FigMaker()
    #analyzer.outputToFile()
    maker.generateAllGraphs()
