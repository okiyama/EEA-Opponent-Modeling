## Hill Climb some static evaluators for konane
## Author: Julian Jocque
## Date: 10/6/14

from StaticEvalModel import *
from updatedKonane import *
from minimaxEvolved import *
from time import strftime
from copy import copy
from datetime import datetime

## Make (3/5?) minimax players, all with default static evaluators that then get evolved once (bit of randomness)
## Play 10 games with each, updating the fitness and # games played versus # wins
## After each round, take the best one and make new minimax players that use that model and evolve them once.
## Rinse and repeat, need to keep getting data continuously

class HillClimb(Konane):

    def __init__(self):
        self.numPlayers = 5
        self.numGames = 20 
        self.size = 6
        self.depthLimit = 3
        self.models = []
        self.initModels()
        self.currPlayers = []
        self.logfile = open("data/hillClimber/depth" + str(self.depthLimit) + "-" + strftime("%Y-%m-%d %H:%M:%S") + ".csv", "w")

    def initModels(self):
        """ Initializes the models that we'll evolve """
        for i in range(self.numPlayers):
            currModel = StaticEvalModel(self.size)
            currModel.mutate()
            self.models.append(currModel)

    def hillClimb(self):
        self.logfile.write("%roundNum, %playerNum, %fitness, " + self.models[0].dumpFeatures() + " , %gamesPerRound, %timeIndividualFinished\n")
        running = True
        roundNum = 0
        try:
            while(running):
                for playerNum in range(self.numPlayers):
                    player1 = MinimaxPlayer(self.size, self.depthLimit)
                    player1.model = self.models[playerNum]
                    self.currPlayers.append(player1)
                    player2 = RandomPlayer(self.size)

                    for gameNum in range(self.numGames):
                        #print "On game num", gameNum
                        winner = self.playOneGame(player1, player2)
                        player1.gamesPlayed += 1
                        if winner == player1:
                            player1.gamesWon += 1
                    self.log(player1, playerNum, roundNum, datetime.time(datetime.now()))
                self.logfile.flush()
                roundNum += 1
                parent = max(self.currPlayers, key = lambda player: player.getFitness())
                self.evolveModels(parent)
                self.currPlayers = []
        except KeyboardInterrupt:
            self.logfile.close()

    def evolveModels(self, parent):
        """ Evolves the models in self.models based on the given parent. """
        for i in range(self.numPlayers):
            curr = copy(parent.model)
            curr.mutate()
            self.models[i] = curr


    def playOneGame(self, p1, p2):
        """
        Given two instances of players, will play out a game
        between them.  Returns the instance of the player than won.
        """
        self.reset()
        p1.initialize('B')
        p2.initialize('W')
        while True:
            try:
                move = p1.getMove(self.board)
            except TimedOutException:
                print p1.name, "move took too long!"
                move = self.randomMove(self.board, p1.side)
            if move == []:
                return p2
            try: 
                self.makeMove('B', move)
            except KonaneError:
                print "Game over: Invalid move by", p1.name
                print move
                print self
                return p2
            try:
                move = p2.getMove(self.board)
            except TimedOutException:
                print p2.name, "move took too long!"
                move = self.randomMove(self.board, p2.side)
            if move == []:
                return p1
            try:
                self.makeMove('W', move)
            except KonaneError:
                print "Game over: Invalid move by", p2.name
                print move
                print self
                return p1

    def log(self, player, playerNum, roundNum, time):
        """ 
        Logs the results of hill climbing to the log file.
        Each line is this format:
        %roundNum, %playerNum, %fitness, %myMovesWeight, %theirMovesWeight, %myPiecesWeight, %theirPiecesWeight, %gamesPerRound
        """
        self.logfile.write(str(roundNum) + ", " + str(playerNum) + ", " + str(player.getFitness())
                + ", " + player.model.dumpModel() + ", " + str(self.numGames) + ", " + str(time) + "\n")

if __name__ == "__main__":
    climber = HillClimb()
    climber.hillClimb()
