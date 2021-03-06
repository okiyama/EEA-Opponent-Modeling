## Attempts to be as generic as possible at making figures from CSV data.
## Aimed at working with results from a GA, but doesn't need to be with a bit of workarounds.
## Because of the nature of this, it won't work from command line easily and will need minor code edits
## to get exactly what you want out of it. These edits should be as minor as possible.
##
## Author: Julian Jocque
## Date: 10/13/14

from prettyplotlib import *

class FigMaker:

    def __init__(self, folder=None, fileName):
        self.dataFolder = folder
        self.outPutFile = "Konane" + str(datetime.datetime.time(datetime.datetime.now())) + ".png"
        self.data = []
        self.timeTaken = []
        if self.dataFolder is not None:
            self.fileList = sorted(os.listdir(self.dataFolder))
        else:
            self.fileList = None
        self.maxFitness = []

        self.getData()
        
    def getData(self):
        """
        Pulls the data from all of the pop data files so we can work with it.
        """
        for fileName in self.fileList:
            #print fileName
            dataFromFile = DataFile(self.dataFolder + fileName)
            self.data.append(dataFromFile)
            self.timeTaken.append(dataFromFile.getTimeTaken())
            self.maxFitness.append(dataFromFile.getNMaxFitnessValues(5))
        
        #print self.maxFitness
        #print self.data
        #print self.timeTaken
        
    def outputToFile(self):
        """
        Outputs the data collected to a file.
        """
        outputFile = open(self.outPutFile, "w")
        for i in range(len(self.fileList)):
            outputFile.write("File: " + self.fileList[i] + "\n")
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
            dataFile.hackyFunction()
#             dataFile.generateFitnessOverTrials()
#             dataFile.generateFitnessOverTimes()
#             dataFile.generateAvgFitnessOverTrials()
#             dataFile.generateAvgFitnessOverTimes()
#             dataFile.generateMaxFitnessOverTrials()
#             dataFile.generateMaxFitnessOverTimes()

class DataFile():
    """
    Encapsulates the data from one data file.
    """
    
    def __init__(self, fileName):
        self.genNum = []
        self.id = []
        self.myMovesWeight = []
        self.theirMovesWeight = []
        self.myPiecesWeight = []
        self.theirPiecesWeight = []
        self.myMovableWeight = []
        self.theirMovableWeight = []
        self.fitness = []
        self.time = []
        self.fileName = fileName
        
        self.createData()
    
    def getDataNumber(self, i):
        """
        Gets the ith data as a tuple in the same format as in pop data files.
        GenerationNum, ID, Loc1, Loc2, Loc3, Distance, Fitness, Time 
        """
        return (self.genNum[i], self.id[i], self.myMovesWeight[i], self.theirMovesWeight[i], 
                self.myPiecesWeight[i]self.theirPiecesWeght[i], self.myMovableWeight[i]self.theirMovableWeight[i], self.fitness[i], self.time[i])

    def getNMaxFitnessValues(self, N):
        """
        Gets the N max fitness values
        """
        #print sorted(self.fitness)[:-N:-1]
        return sorted(self.fitness)[:-N-1:-1]
    
    def getNMaxFitnessLines(self, N):
        """
        Gets the full data of the N best fitness values from this file as a tuple in the format:
        (GenerationNum, ID, Loc1, Loc2, Loc3, Distance, Fitness, Time)
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
        regex = "(.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*)"
        file = open(self.fileName, "r")
        file.readline()
        file.readline()
        for line in file:
            #print line
            matched = re.match(regex, line)
            self.appendData(matched)
        
        file.close()
    
    def appendData(self, match):
        """
        Appends the given regex match to the data of this.
        """
        self.genNum.append(match.group(1))
        self.id.append(match.group(2))
        self.loc1.append(match.group(3))
        self.loc2.append(match.group(4))
        self.loc3.append(match.group(5))
        self.distance.append(match.group(6))
        self.fitness.append(match.group(7))
        self.time.append(match.group(8))

    def getTimeTaken(self):
        """
        Gets the absolute amount of time taken for this pop data file to be created
        """
        #print self.time
        timeSorted = sorted(self.time)
        #print "End: " + timeSorted[-1] + ", start: " + timeSorted[0]
        return str(self.getTimeDifference(timeSorted[-1], timeSorted[0]))

    def getTimeDifference(self, time1, time2):
        """
        Gets difference between two times of format:
        Hour:Minute:Second.Microseconds
        Does time1 - time2.
        """
        format = "%H:%M:%S.%f"
        endTime = datetime.datetime.strptime(time1, format)
        startTime = datetime.datetime.strptime(time2, format)
        return endTime - startTime
                

    def generateFitnessOverTrials(self):
        """
        Generates a graph of the fitness of this pop data file over the trials.
        """
        X = np.array(self.id)
        Y = np.array(self.fitness)
        plot(X, Y)

        xlabel("Trial Number")
        ylabel("Fitness Value")
        suptitle("Fitness Value of Each Trial")

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

            if (self.genNum[i] != self.genNum[i+1]):
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                tempAvg = 0
                counter = 0

        #print averages

        plot(range(len(averages)+1)[1:], averages)
        xlim([1,self.getNumGenerations()])
        xlabel("Generation Number")
        ylabel("Generation's Average Fitness")
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

            if (self.genNum[i] != self.genNum[i+1]):
                maxes.append(max(tempMax))
                tempMax = []

        #print averages

        plot(range(len(maxes)+1)[1:], maxes)
        xlim([1,self.getNumGenerations()])
        xlabel("Generation Number")
        ylabel("Generation's Maximum Fitness")
        suptitle("Generational Maximum Fitness versus Generation Number")

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
                timeDiffs.append(self.getTimeDifference(self.time[i],self.time[0]).seconds)
                break

            if (self.genNum[i] != self.genNum[i+1]):
                tempAvg = tempAvg / counter
                averages.append(tempAvg)
                tempAvg = 0
                counter = 0
                timeDiffs.append(self.getTimeDifference(self.time[i],self.time[0]).seconds)

        plot(timeDiffs, averages)
        #xlim([1,25])
        xlabel("Seconds Since Testing Began")
        ylabel("Generation's Average Fitness")
        suptitle("Generational Average Fitness versus Time")

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
                timeDiffs.append(self.getTimeDifference(self.time[i],self.time[0]).seconds)
                break

            if (self.genNum[i] != self.genNum[i+1]):
                maxes.append(max(tempMax))
                tempMax = []
                timeDiffs.append(self.getTimeDifference(self.time[i],self.time[0]).seconds)

        plot(timeDiffs, maxes)
        #xlim([1,25])
        xlabel("Seconds Since Testing Began")
        ylabel("Generation's Maximum Fitness")
        suptitle("Generational Maximum Fitness versus Time")

        show()

    def generateFitnessOverTimes(self):
        """
        Generates a graph of the fitness of this pop data file over the time taken to generate it.
        """
        timeDiffs = []
        for timeVal in self.time:
            timeDiffs.append(self.getTimeDifference(timeVal,self.time[0]).seconds)
        plot(timeDiffs, self.fitness)

        xlabel("Seconds Since Testing Began")
        ylabel("Fitness of Trial")
        title("Fitness of Trials Versus Time Since Testing Began")

        show()
    
if __name__ == "__main__":
    maker = FigMaker(folder=argv[1])
    #analyzer.outputToFile()
    maker.generateAllGraphs()
