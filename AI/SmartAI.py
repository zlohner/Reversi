#!/usr/bin/env python

import heapq
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
	return [(i, j) for i in range(x - 1, x + 2) for j in range(y - 1, y + 2) if i >= 0 and i < 8 and j >= 0 and j < 8 and (i!=x or j!=y)]

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

class SmartAI(AI):
	def __init__(self, me, config=None):
		AI.__init__(self, me)

		self.config = {
			'timeFactor': 4,
			'positionalWeight': 7.0,
			'frontierWeight': 2.0,
			'mobilityWeight': 8.0,
			'stabilityWeight': 2.0,
			'r': 0.8, # corner
			'c': -0.2, # c-squares (between corner and edge)
			'x': -0.8, # x-squares (between center and corner)
			'a': 0.6, # a-squares (outer two edge squares)
			'b': 0.5, # b-squares (inner two edge squares)
			'm': 0.0, # m-squares (middle 4x4)
			't': -0.2 # t-squares (between middle 4x4 and edge)
		}
		if config != None:
			for key, val in config.iteritems():
				self.config[key] = val

		# positional score
		r = self.config['r'] # corner
		c = self.config['c'] # c-squares (between corner and edge)
		x = self.config['x'] # x-squares (between center and corner)
		a = self.config['a'] # a-squares (outer two edge squares)
		b = self.config['b'] # b-squares (inner two edge squares)
		m = self.config['m'] # m-squares (middle 4x4)
		t = self.config['t'] # t-squares (between middle 4x4 and edge)

		self.matrix = [
			[r, c, a, b, b, a, c, r],
			[c, x, t, t, t, t, x, c],
			[a, t, m, m, m, m, t, a],
			[b, t, m, m, m, m, t, b],
			[b, t, m, m, m, m, t, b],
			[a, t, m, m, m, m, t, a],
			[c, x, t, t, t, t, x, c],
			[r, c, a, b, b, a, c, r]
		]

	# evaluate a given board state
	# calculated on a zero-sum basis, positive is me, negative is opponent
	def heuristic(self, node):

		# after the pivot turn, just evaluate the current score
		pivotTurn = 10
		if TOTAL_MOVES - node.round < pivotTurn:
			myScore = countScore(node.state, self.me)
			oppScore = countScore(node.state, self.opp)
			return 2.0 * (float(myScore) / (myScore + oppScore) - 0.5)

		# positional score (see how good the current move is)
		positionalScore = 0
		for (i, j) in cross(range(0, 8), range(0, 8)):
			if node.state[i][j] == self.me:
				positionalScore += self.matrix[i][j]
			elif node.state[i][j] == self.opp:
				positionalScore -= self.matrix[i][j]
		if node.max:
			positionalScore += self.matrix[node.row][node.col]
		else:
			positionalScore -= self.matrix[node.row][node.col]
		# find a way to fix this to an interval later, since it's not on [-1, 1] anymore
		# also it certainly needs tweaking regardless

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
			# we want the opponent to have a big frontier
			frontierScore = 2.0 * (float(oppFrontier) / (myFrontier + oppFrontier) - 0.5)

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

		# stable discs cannot be flipped
		for (i, j) in cross(range(0, 8), range(0, 8)):
			stablePlayer = stable(node.state, i, j)
			if stablePlayer == self.me:
				myStability += 1
			if stablePlayer == self.opp:
				oppStability += 1

		if myStability + oppStability == 0:
			stabilityScore = 0
		else:
			stabilityScore = 2.0 * (float(myStability) / (myStability + oppStability) - 0.5)

		positionalWeight = self.config['positionalWeight']
		frontierWeight = self.config['frontierWeight']
		mobilityWeight = self.config['mobilityWeight']
		stabilityWeight = self.config['stabilityWeight']

		score = \
			positionalScore * positionalWeight + \
			frontierScore * frontierWeight + \
			mobilityScore * mobilityWeight + \
			stabilityScore * stabilityWeight

		score /= (positionalWeight + frontierWeight + mobilityWeight + stabilityWeight)

		return score

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
				# children.append((-self.heuristic(child), child))
				children.append(child)

			best = None
			# heapq.heapify(children)

			while len(children) > 0:
				# child = heapq.heappop(children)[1]
				child = children.pop()
				child.value = self.minimax(child).value
				if best == None or child.value > best.value:
					best = child
				node.alpha = max(node.alpha, child.value)
				if node.beta <= node.alpha:
					break

			if len(validMoves) > 0:
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
				# children.append((self.heuristic(child), child))
				children.append(child)

			best = None
			# heapq.heapify(children)

			while len(children) > 0:
				# child = heapq.heappop(children)[1]
				child = children.pop()
				child.value = self.minimax(child).value
				if best == None or child.value < best.value:
					best = child
				node.beta = min(node.beta, child.value)
				if node.beta <= node.alpha:
					break

			if len(validMoves) > 0:
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

		estimated_factor = self.config['timeFactor'] # i.e. it takes us x times as long to go one more depth
		depth = 0
		while depth < TOTAL_MOVES - round:
			depth += 1
			moveNode = self.minimax(Node(state, round, depth=depth))

			elapsed = time.clock() - startTime
			if elapsed * estimated_factor > myTimePerTurn:
				break

		if depth == TOTAL_MOVES - round:
			print 'Exhausted the entire tree in %f seconds' % (elapsed)
		else:
			print 'Calling it quits! Got to depth %d in %f seconds' % (depth, elapsed)

		print 'Move Heuristic Value: %s' % moveNode.value

		print ''
		return [moveNode.row, moveNode.col]
