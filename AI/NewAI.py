#!/usr/bin/env python

import random
import time

from AI import AI

TOTAL_MOVES = 64



def printState(state):
	for i in range(8):
		print '%d%d%d%d%d%d%d%d' % (state[0][i], state[1][i], state[2][i], state[3][i], state[4][i], state[5][i], state[6][i], state[7][i])

class MoveOption(object):
	def __init__(self, move):
		self.move = move
		self.attempts = 0
		self.wins = 0
		self.draws = 0
		self.losses = 0

	def addWin(self):
		self.attempts += 1
		self.wins += 1

	def addDraw(self):
		self.attempts += 1
		self.draws += 1

	def addLoss(self):
		self.attempts += 1
		self.losses += 1

	def rate(self):
		if self.attempts == 0:
			return 0

		return (self.wins+0.5*self.draws)/self.attempts



class NewAI(AI):
	def __init__(self, me, config=None):
		AI.__init__(self, me)
		# we don't actually use a config, at least for now

	# increase time toward the midgame, decrease toward the endgame
	def distribution(self, round):
		return max(2 - abs((32.0 - (round - 2)) / 16.0), 0)

	# get move
	def move(self, **kwargs):
		startTime = time.clock()

		state = kwargs['state']
		round = kwargs['round']

		myTimer = kwargs['t1'] if self.me == 1 else kwargs['t2']
		myRemainingMoves = (TOTAL_MOVES - round + 1) / 2 # the +1 forces it to round up, so we can integer divide and get the right answer as either player
		myTimePerTurn = myTimer / (myRemainingMoves + 1) # this gives us enough time for one extra turn, just so we have breathing room
		myTimePerTurn *= self.distribution(round) # spend shorter in the beginning and endgame, longer in the midgame
		print 'I can spend %f this turn' % (myTimePerTurn)

		validMoves = self.getValidMoves(state, round, self.me)
		for i in range(0, len(validMoves)):
			validMoves[i] = MoveOption(validMoves[i])

		totalGoes = 0
		while (time.clock()-startTime) < myTimePerTurn*.9 and totalGoes < 100:
			totalGoes += 1
			for moveOption in validMoves:
				result = self.simulate(self.simMove(state, round, self.me, moveOption.move[0], moveOption.move[1]), round+1, 3-self.me)
				if result == self.me:
					moveOption.addWin()
				elif result == 0:
					moveOption.addDraw()
				else:
					moveOption.addLoss()

		bestRate = -1
		bestOption = None
		for moveOption in validMoves:
			rate = moveOption.rate()
			if rate > bestRate:
				bestRate = rate
				bestOption = moveOption

		print 'Chose option with %d/%d/%d after %d games' % (moveOption.wins, moveOption.draws, moveOption.losses, moveOption.attempts)

		return bestOption.move

	def simulate(self, state, round, player):
		while round < TOTAL_MOVES:
			validMoves = self.getValidMoves(state, round, player)
			if len(validMoves) == 0:
				player = 3-player
				validMoves = self.getValidMoves(state, round, player)
				if len(validMoves) == 0:
					print 'no one can move!'
					break

			move = validMoves[random.randint(0, len(validMoves) -1)]
			state = self.simMove(state, round, player, move[0], move[1])

			round += 1
			player = 3-player

		p1Count = 0
		p2Count = 0
		for col in state:
			for square in col:
				if square == 1:
					p1Count += 1
				elif square == 2:
					p2Count += 1
		if p1Count > p2Count:
			return 1
		elif p2Count > p1Count:
			return 2
		return 0
