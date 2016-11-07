#!/usr/bin/env python

import time

from AI import AI

TOTAL_MOVES = 64

# class to represent a state and its relevant information
# TODO: implement memoization of previously computed nodes
class Node(object):
	def __init__(self, state, round, row=-1, col=-1, depth=5, max=True, alpha=-float('inf'), beta=float('inf')):
		self.state = state
		self.round = round
		self.value = -1
		self.row = row
		self.col = col
		self.max = max
		self.depth = depth
		self.alpha = alpha
		self.beta = beta

# sum a given score over a set of squares (used to shortcut valuation of squares in heuristic)
def scoreRange(state, squares, player, points):
	return sum([points for (i, j) in squares if state[i][j] == player])

# count the current score for a player
def countScore(state, player):
	score = 0
	for row in state:
		for slot in row:
			if slot == player:
				score += 1
	return score

# count the final score of a finished game; used when few moves remain to explore the whole tree
def winner(state):
	score = countScore(state, TOTAL_MOVES)
	if score > TOTAL_MOVES - score:
		return float('inf')
	else:
		return -float('inf')

# get the neighbors of a position within the board
def neighbors(x, y):
	return [(i, j) for i in range(x - 1, x + 2) for j in range(y - 1, y + 2) if i > 0 and i < 8 and j > 0 and j < 8]

# check whether a square is surrounded
def surrounded(state, x, y):
	for (i, j) in neighbors(x,y):
		if state[i][j] == 0:
			return False
	return True

# the cross product of two ranges
def cross(l1, l2):
	return [(i,j) for j in l2 for i in l1]

# check whether a position is stable
def stable(mem, state, x, y, player=None):
	if (x, y) not in mem:
		mem[(x, y)] = -1 # don't revisit a square
		if x < 0 or x >= 8 or y < 0 or y >= 8:
			mem[(x, y)] = player
		else:
			if player == None:
				player = state[x][y]
				if player == 0:
					mem[(x, y)] = 0
					return mem[(x, y)]

			if state[x][y] == player:
				N = stable(mem, state, x - 1, y, player) == player
				E = stable(mem, state, x, y + 1, player) == player
				S = stable(mem, state, x + 1, y, player) == player
				W = stable(mem, state, x, y - 1, player) == player
				NW = stable(mem, state, x - 1, y - 1, player) == player
				NE = stable(mem, state, x - 1, y + 1, player) == player
				SE = stable(mem, state, x + 1, y + 1, player) == player
				SW = stable(mem, state, x + 1, y - 1, player) == player

				if (W and NW and N) or (N and NE and E) or (E and SE and S) or (S and SW and W):
					mem[(x, y)] = player
				else:
					mem[(x, y)] = 0
			else:
				mem[(x, y)] = 0

	return mem[(x, y)]

# check whether a position is unstable
def unstable(mem, state, x, y, direction, player=None):
	if (x, y, direction) not in mem:
		if x < 0 or x >= 8 or y < 0 or y >= 8:
			mem[(x, y, direction)] = 0
		else:
			if player == None:
				player = state[x][y]
				if player == 0:
					mem[(x, y, direction)] = 0
					return mem[(x, y, direction)]
			if state[x][y] == player:
				if direction == (0, 0):
					isUnstable = False
					for (i, j) in neighbors(x, y):
						if state[i][j] == 0:
							dx = x - i
							dy = y - j
							isUnstable = isUnstable or unstable(mem, state, x - dx, y - dy, (-dx, -dy), player) == player
					if isUnstable:
						mem[(x, y, direction)] = player
					else:
						mem[(x, y, direction)] = 0
				else:
					mem[(x, y, direction)] = unstable(mem, state, x + direction[0], y + direction[1], direction, player)
			else:
				if state[x][y] == 0:
					mem[(x, y, direction)] = 0
				else:
					mem[(x, y, direction)] = player
	return mem[(x, y, direction)]

class SmartAI(AI):
	def __init__(self, me):
		AI.__init__(self, me)

	# evaluate a given board state
	# calculated on a zero-sum basis, positive is me, negative is opponent
	def heuristic(self, node):

		# after the pivot turn, just evaluate the current score
		pivotTurn = 10
		if TOTAL_MOVES - node.round < pivotTurn:
			myScore = countScore(node.state, self.me)
			oppScore = countScore(node.state, self.opp)
			return 2.0 * (float(myScore) / (myScore + oppScore) - 0.5)

		# positional score
		r = 20 # corner
		c = -3 # c-squares (between corner and edge)
		x = -7 # x-squares (between center and corner)
		a = 11 # a-squares (outer two edge squares)
		b = 8 # b-squares (inner two edge squares)
		s = 3 # s-squares (corners of inner 4 x 4)

		myPosition = 0
		myPosition += scoreRange(node.state, cross([0, 7], [0, 7]), self.me, r)
		myPosition += scoreRange(node.state, cross([1, 6], [0, 7]), self.me, c)
		myPosition += scoreRange(node.state, cross([0, 7], [1, 6]), self.me, c)
		myPosition += scoreRange(node.state, cross([1, 6], [1, 6]), self.me, x)
		myPosition += scoreRange(node.state, cross([0, 7], [2, 5]), self.me, a)
		myPosition += scoreRange(node.state, cross([2, 5], [0, 7]), self.me, a)
		myPosition += scoreRange(node.state, cross([0, 7], [3, 4]), self.me, b)
		myPosition += scoreRange(node.state, cross([3, 4], [0, 7]), self.me, b)
		myPosition += scoreRange(node.state, cross([2, 5], [2, 5]), self.me, s)

		oppPosition = 0
		oppPosition += scoreRange(node.state, cross([0, 7], [0, 7]), self.opp, r)
		oppPosition += scoreRange(node.state, cross([1, 6], [0, 7]), self.opp, c)
		oppPosition += scoreRange(node.state, cross([0, 7], [1, 6]), self.opp, c)
		oppPosition += scoreRange(node.state, cross([1, 6], [1, 6]), self.opp, x)
		oppPosition += scoreRange(node.state, cross([0, 7], [2, 5]), self.opp, a)
		oppPosition += scoreRange(node.state, cross([2, 5], [0, 7]), self.opp, a)
		oppPosition += scoreRange(node.state, cross([0, 7], [3, 4]), self.opp, b)
		oppPosition += scoreRange(node.state, cross([3, 4], [0, 7]), self.opp, b)
		oppPosition += scoreRange(node.state, cross([2, 5], [2, 5]), self.opp, s)

		if myPosition + oppPosition == 0:
			positionalScore = 0
		else:
			positionalScore = 2.0 * (float(myPosition) / (myPosition + oppPosition) - 0.5)

		# frontier discs (discs with at least one open neighbor)
		myFrontier = 0
		oppFrontier = 0
		for (i, j) in cross(range(0, 8), range(0, 8)):
			if not surrounded(node.state, i, j):
				if node.state[i][j] == self.me:
					myFrontier += 1
				elif node.state[i][j] == self.opp:
					oppFrontier += 1

		if myFrontier + oppFrontier == 0:
			frontierScore = 0
		else:
			frontierScore = 2.0 * (float(myFrontier) / (myFrontier + oppFrontier) - 0.5)

		# mobility, calculated relatively to opponent with value from -1 to 1
		myMobility = len(self.getValidMoves(node.state, node.round, self.me))
		oppMobility = len(self.getValidMoves(node.state, node.round, self.opp))

		if myMobility + oppMobility == 0:
			mobilityScore = 0
		else:
			mobilityScore = 2.0 * (float(myMobility) / (myMobility + oppMobility) - 0.5)

		# stability
		myStability = 0
		oppStability = 0
		stableMem = {}
		unstableMem = {}

		# stable discs cannot be flipped
		# unstable discs can be flipped this turn
		# semi-stable discs can be flipped, but not this turn
		for (i, j) in cross(range(0, 8), range(0, 8)):

			stablePlayer = stable(stableMem, node.state, i, j)
			unstablePlayer = unstable(unstableMem, node.state, i, j, (0, 0))

			if stablePlayer != 0 and unstablePlayer != 0:
				print 'ERROR: stable = %d, unstable = %d' % (stablePlayer, unstablePlayer)
				for row in node.state:
					print row
				print (i, j)
				time.sleep(1)

			if stablePlayer == self.me:
				myStability += 1
			elif unstablePlayer == self.me:
				myStability -= 1

			if stablePlayer == self.opp:
				oppStability += 1
			elif unstablePlayer == self.opp:
				oppStability -= 1

		if myStability + oppStability == 0:
			stabilityScore = 0
		else:
			stabilityScore = 2.0 * (float(myStability) / (myStability + oppStability) - 0.5)

		# print 'position: %.2f frontier: %.2f mobility: %.2f stability: %.2f' % (positionalScore, frontierScore, mobilityScore, stabilityScore)

		positionalWeight = 10
		frontierWeight = 10
		mobilityWeight = 10
		stabilityWeight = 10

		return \
			positionalScore * positionalWeight + \
			frontierScore * frontierWeight + \
			mobilityScore * mobilityWeight + \
			stabilityScore * stabilityWeight

	# explore a node using minimax adversarial search with limited depth and a heuristic function
	def minimax(self, node):
		if TOTAL_MOVES - node.round == 0:
			node.value = winner(node.state)
			return node

		if node.depth == 0:
			node.value = self.heuristic(node)
			return node

		children = []
		if node.max:
			validMoves = self.getValidMoves(node.state, node.round, self.me)
			for move in validMoves:
				newState = self.simMove(node.state, node.round, self.me, move[0], move[1])
				child = Node(
					newState,
					node.round + 1,
					row=move[0],
					col=move[1],
					depth=(node.depth - 1),
					max=False,
					alpha=node.alpha,
					beta=node.beta
				)
				child.value = self.minimax(child).value
				children.append(child)

				node.alpha = max(node.alpha, child.value)
				if node.beta <= node.alpha:
					break

			if len(validMoves) > 0:
				best = max(children, key=lambda node: node.value)
				node.value = best.value
				return best
			else:
				oppValidMoves = self.getValidMoves(node.state, node.round, self.opp)
				if len(oppValidMoves) > 0:
					node.max = False
					return self.minimax(node)
				else:
					node.value = winner(node.state)
					return node

		else:
			validMoves = self.getValidMoves(node.state, node.round, self.opp)
			for move in validMoves:
				newState = self.simMove(node.state, node.round, self.opp, move[0], move[1])
				child = Node(
					newState,
					node.round + 1,
					row=move[0],
					col=move[1],
					depth=(node.depth - 1),
					max=True,
					alpha=node.alpha,
					beta=node.beta
				)
				child.value = self.minimax(child).value
				children.append(child)

				node.beta = min(node.beta, child.value)
				if node.beta <= node.alpha:
					break

			if len(validMoves) > 0:
				best = min(children, key=lambda node: node.value)
				node.value = best.value
				return best
			else:
				oppValidMoves = self.getValidMoves(node.state, node.round, self.me)
				if len(oppValidMoves) > 0:
					node.max = True
					return self.minimax(node)
				else:
					node.value = winner(node.state)
					return node

	# increase time toward the midgame, decrease toward the endgame
	def distribution(self, round):
		return max(2 - abs((32.0 - (round - 2)) / 16.0), 0)

	# get move (uses minimax)
	def move(self, **kwargs):
		startTime = time.clock()

		state = kwargs['state']
		round = kwargs['round']

		myTimer = kwargs['t1'] if self.me == 1 else kwargs['t2']
		myRemainingMoves = (TOTAL_MOVES - round + 1) / 2 # the +1 forces it to round up, so we can integer divide and get the right answer as either player
		myTimePerTurn = myTimer / (myRemainingMoves + 1) # this gives us enough time for one extra turn, just so we have breathing room
		myTimePerTurn *= self.distribution(round) # spend shorter in the beginning and endgame, longer in the midgame
		print 'I can spend %f this turn' % (myTimePerTurn)

		estimated_factor = 2 # i.e. it takes us 2 times as long to go one more depth
		depth = 0
		while depth < TOTAL_MOVES - round:
			depth += 1
			moveNode = self.minimax(Node(state, round, depth=depth))

			elapsed = time.clock() - startTime
			if elapsed * estimated_factor + elapsed > myTimePerTurn:
				break

		if depth == TOTAL_MOVES - round:
			print 'Exhausted the entire tree in %f seconds' % (elapsed)
		else:
			print 'Calling it quits! Got to depth %d in %f seconds' % (depth, elapsed)

		print 'Move Heuristic Value: %s' % moveNode.value

		if moveNode.value > 0:
			print 'I\'m winning!'
		else:
			print 'I\'m losing :('

		print ''
		return [moveNode.row, moveNode.col]
