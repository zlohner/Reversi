#!/usr/bin/env python

import time
import math

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

class SmartAI(AI):
	def __init__(self, me):
		AI.__init__(self, me)

	# count my current score
	def countScore(self, state, round):
		score = 0
		for row in state:
			for slot in row:
				if slot == self.me:
					score += 1
		return score - (TOTAL_MOVES - round)

	# count the final score of a finished game; used when few moves remain to explore the whole tree
	def winner(self, state):
		score = self.countScore(state, TOTAL_MOVES)
		if score > TOTAL_MOVES - score:
			return float('inf')
		else:
			return -float('inf')

	# sum a given score over the cross product of two ranges (used to shortcut valuation of cells in heuristic)
	def scoreRange(self, state, cells, points):
		score = 0
		for (i,j) in cells:
			if state[i][j] == self.me:
				score += points
			elif state[i][j] == self.opp:
				score -= points
		return score

	def neighbors(self, x, y):
		neighbors = []
		for i in range(x - 1, x + 2):
			for j in range(y - 1, y + 2):
				if x > 0 and x < 8 and y > 0 and y < 8:
					neighbors.append((x,y))
		return neighbors

	def surrounded(self, state, x, y):
		neighbors = self.neighbors(x,y)
		for i in neighbors:
			if i == 0:
				return False
		return True

	def cross(self, r1, r2):
		return [(i,j) for j in r2 for i in r1]

	def edgeEval(self, state, edge, row, col, points):
		value = 0
		owner = 0
		for (i, j) in edge:
			if state[i][j] == 0:
				pass
			else:
				if owner == 0:
					owner = state[i][j]
				else:
					owner = -1

		if owner == self.me:
			value = points
		elif owner == self.opp:
			value = -points

		if (row, col) in edge:
			value = 2 * value
		return value

	# evaluate how good a given board state is
	# calculated on a zero-sum basis, positive is me, negative is opponent
	def heuristic(self, node):
		# at a certain turn, just evaluate the current score
		pivotTurn = 10
		corner = 5
		edge = 4
		surrounded = 1
		bridge = -1
		curb = -3

		if TOTAL_MOVES - node.round < pivotTurn:
			return self.countScore(node.state, node.round)

		score = 0

		score += self.scoreRange(node.state, self.cross([0, 7], [0, 7]), corner)

		score += self.edgeEval(node.state, self.cross([0],range(1,7)), node.row, node.col, edge)
		score += self.edgeEval(node.state, self.cross([7],range(1,7)), node.row, node.col, edge)
		score += self.edgeEval(node.state, self.cross(range(1,7),[0]), node.row, node.col, edge)
		score += self.edgeEval(node.state, self.cross(range(1,7),[7]), node.row, node.col, edge)

		for (i, j) in self.cross([0, 7], [0, 7]):
			if node.state[i][j] == 0:
				if (node.row, node.col) in self.neighbors(i, j):
					score += curb

		for (i, j) in self.cross(range(2, 6), range(2, 6)):
			if self.surrounded(node.state, i, j):
				score += surrounded

		score += self.scoreRange(node.state, self.cross([1, 6], range(2, 6)), bridge)
		score += self.scoreRange(node.state, self.cross(range(2, 6), [1, 6]), bridge)

		# maximize moves available to me, minimize moves available to opponent
		myMoves = len(self.getValidMoves(node.state, node.round, self.me))
		oppMoves = len(self.getValidMoves(node.state, node.round, self.opp))
		optionAdvantage = (myMoves - oppMoves)
		score += optionAdvantage

		return score

	# explore a node using minimax adversarial search with limited depth and a heuristic function
	def minimax(self, node):
		if TOTAL_MOVES - node.round == 0:
			node.value = self.winner(node.state)
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
					node.value = self.winner(node.state)
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
					node.value = self.winner(node.state)
					return node

	# maths
	def distribution(self, round):
		return 2 - abs((32.0 - round) / 16.0)

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

		estimated_factor = 2 # ie, it takes us 2 times as long to go one more depth
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
		return [moveNode.row, moveNode.col]
