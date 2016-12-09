#!/usr/bin/env python

import random
import time

from AI import AI

TOTAL_MOVES = 64



# return an int value describing how much the player should desire the given move
# should be really quick, rough and dirty
cor = 32
edg = 16
mid = 4
bad = 1
HEURISTIC_POS_VALS = [
	[cor, edg, edg, edg, edg, edg, edg, cor],
	[edg, bad, bad, bad, bad, bad, bad, edg],
	[edg, bad, mid, mid, mid, mid, bad, edg],
	[edg, bad, mid, mid, mid, mid, bad, edg],
	[edg, bad, mid, mid, mid, mid, bad, edg],
	[edg, bad, mid, mid, mid, mid, bad, edg],
	[edg, bad, bad, bad, bad, bad, bad, edg],
	[cor, edg, edg, edg, edg, edg, edg, cor]
]
def heuristic(newState, round, move, player):
	if round < 4:		# setup - doesn't matter
		return 1
	elif round < 32:	# early game - stay in middle unless someone messes up
		return HEURISTIC_POS_VALS[move[0]][move[1]]
	else:	# late game - get interior pieces, not frontiers
		myInterior = 0
		myFrontier = 0
		theirInterior = 0
		theirFrontier = 0
		for i in range(8):
			for j in range(8):
				if newState[i][j] == player:
					if surrounded(newState, i, j):
						myInterior += 1
					else:
						myFrontier += 1
				elif newState[i][j] != 0:
					if surrounded(newState, i, j):
						theirInterior += 1
					else:
						theirFrontier += 1
		return myInterior + theirFrontier/2
	# else:				# late game - get stable pieces
	# 	myStable = 0
	# 	theirStable = 0
	# 	unstable = 0
	# 	for i in range(8):
	# 		for j in range(8):
	# 			if newState[i][j] == 0:
	# 				unstable += 1
	# 			else:
	# 				stableFor = stable(newState, i, j)
	# 				if stableFor == player:
	# 					myStable += 1
	# 				elif stableFor == 0:
	# 					unstable += 1
	# 				else:
	# 					theirStable += 1
	# 	return myStable + unstable/2

# check whether a position is surrounded
def surrounded(state, x, y):
	neighbors = [(i, j) for i in range(x - 1, x + 2) for j in range(y - 1, y + 2) if i >= 0 and i < 8 and j >= 0 and j < 8 and (i!=x or j!=y)]
	for (i, j) in neighbors:
		if state[i][j] == 0:
			return False
	return True

# check whether a position is stable
def stable(state, x, y):
	# we are stable if either of these is true, for all four vectors (two orthogonal, two diagonal):
		# A) we can travel in one of the two directions and hit a wall without hitting any empty or opponent squares
		# B) we can travel in both directions without hitting any empty squares

	owner = state[x][y]
	if owner == 0:
		return 0

	for direction in [(1, 0), (0, 1), (1, 1), (1, -1)]:
		if not stableOnAngle(state, x, y, direction, owner):
			return 0

	return owner

def stableOnAngle(state, x, y, angle, player):
	neitherHasEmpty = True

	for forwardBackward in range(2):
		thisHasNoEnemyOrEmpty = True
		i = x
		j = y
		while i >= 0 and i < 8 and j >= 0 and j < 8:
			if state[i][j] == 0:
				neitherHasEmpty = False
				thisHasNoEnemyOrEmpty = False
			elif state[i][j] != player:
				thisHasNoEnemyOrEmpty = False
			i += angle[0]
			j += angle[1]

		if thisHasNoEnemyOrEmpty:
			return True
		# reverse ray
		angle = (-angle[0], -angle[1])

	if neitherHasEmpty:
		return True
	return False



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

		self.config = {
			'timeUsage': 0.95,	# don't start loops after 90% of time has been used
			'maxIterations': 1000,
			'heuristicWeight': 0.02
		}
		if config != None:
			for key, val in config.iteritems():
				self.config[key] = val

	# increase time toward the midgame, decrease toward the endgame
	def distribution(self, round):
		# return max(2 - abs((32.0 - (round - 2)) / 16.0), 0)
		if round < 4:
			return 0.1
		else:
			return 1.5

	# get move
	def move(self, **kwargs):
		print ''

		startTime = time.clock()
		random.seed(startTime)

		state = kwargs['state']
		round = kwargs['round']

		myTimer = kwargs['t1'] if self.me == 1 else kwargs['t2']
		myRemainingMoves = (TOTAL_MOVES - round + 1) / 2 # the +1 forces it to round up, so we can integer divide and get the right answer as either player
		myTimePerTurn = myTimer / (myRemainingMoves + 1) # this gives us enough time for one extra turn, just so we have breathing room
		myTimePerTurn *= self.distribution(round) # spend shorter in the beginning and endgame, longer in the midgame
		print 'I can spend %f this turn' % (myTimePerTurn)

		validMoves = self.getValidMoves(state, round, self.me)
		if len(validMoves) == 1:
			return validMoves[0]
		for i in range(0, len(validMoves)):
			validMoves[i] = MoveOption(validMoves[i])

		remIterations = self.config['maxIterations']
		while (time.clock()-startTime) < myTimePerTurn*self.config['timeUsage'] and remIterations != 0:
			remIterations -= 1
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

		print 'Move score: %f over %d games (%d total)' % (bestRate, moveOption.attempts, moveOption.attempts*len(validMoves))

		return bestOption.move

	def simulate(self, state, round, player):
		while round < TOTAL_MOVES:
			validMoves = self.getValidMoves(state, round, player)
			if len(validMoves) == 0:
				player = 3-player
				validMoves = self.getValidMoves(state, round, player)
				if len(validMoves) == 0:
					# no one can move; the player that put it in this state gets empty tiles
					for i in range(8):
						for j in range(8):
							state[i][j] = player
					break

			move = None
			if random.random() < self.config['heuristicWeight']:
				# we care about heuristic
				weights = [heuristic(self.simMove(state, round, player, validMoves[i][0], validMoves[i][1]), round, validMoves[i], player) for i in range(len(validMoves))]
				totalWeight = 0
				for weight in weights:
					totalWeight += weight

				pick = random.randint(0, totalWeight-1)
				for i in range(len(validMoves)):
					pick -= weights[i]
					if pick <= 0:
						move = validMoves[i]
						break
			if move == None:
				# we don't care about the heuristic
				move = validMoves[random.randint(0, len(validMoves) -1)]

			state = self.simMoveInPlace(state, round, player, move[0], move[1])

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
