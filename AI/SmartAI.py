#!/usr/bin/env python

from AI import AI

TOTAL_MOVES = 64

# class to represent a state and its relevant information
# TODO: implement memoization of previously computed nodes
class Node(object):
	def __init__(self, state, round, row, col, depth=5, max=True, alpha=-float('inf'), beta=float('inf')):
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
	def checkWinner(self, state):
		score = self.countScore(state, TOTAL_MOVES)
		if score > TOTAL_MOVES - score:
			return float('inf')
		else:
			return -float('inf')

	# sum a given score over the cross product of two ranges (used to shortcut valuation of cells in heuristic)
	def scoreRange(self, state, r1, r2, points):
		score = 0
		for i in r1:
			for j in r2:
				if state[i][j] == self.me:
					score += points
				elif state[i][j] == self.opp:
					score -= points
		return score

	# evaluate how good a given board state is
	# calculated on a zero-sum basis, positive is me, negative is opponent
	def heuristic(self, node):

		pivotTurn = 10

		if TOTAL_MOVES - node.round < pivotTurn:
			return self.countScore(node.state, node.round)

		score = 0

		"""
		valuations of various cell types
		cr  ceb e   e   e   e   ceb cr
		ceb ccb ecb ecb ecb ecb ccb ceb
		e   ecb c   c   c   c   ecb e
		e   ecb c   c   c   c   ecb e
		e   ecb c   c   c   c   ecb e
		e   ecb c   c   c   c   ecb e
		ceb ccb ecb ecb ecb ecb ccb ceb
		cr  ceb e   e   e   e   ceb cr
		"""

		corner = 5
		edge = 3
		center = 2
		edgeCenterBridge= -1
		cornerEdgeBridge = -3
		cornerCenterBridge= -5

		score += self.scoreRange(node.state, [0, 7], [0, 7], corner)
		score += self.scoreRange(node.state, [0, 7], range(2, 6), edge)
		score += self.scoreRange(node.state, range(2, 6), [0, 7], edge)
		score += self.scoreRange(node.state, range(2, 6), range(2, 6), center)
		score += self.scoreRange(node.state, [1, 6], range(2, 6), edgeCenterBridge)
		score += self.scoreRange(node.state, range(2, 6), [1, 6], edgeCenterBridge)
		score += self.scoreRange(node.state, [0, 7], [1, 6], cornerEdgeBridge)
		score += self.scoreRange(node.state, [1, 6], [0, 7], cornerEdgeBridge)
		score += self.scoreRange(node.state, [1, 6], [1, 6], cornerCenterBridge)

		# maximize moves available to me, minimize moves available to opponent
		myMoves = len(self.getValidMoves(node.state, node.round, self.me))
		oppMoves = len(self.getValidMoves(node.state, node.round, self.opp))
		optionAdvantage = (myMoves - oppMoves)
		score += optionAdvantage

		return score

	# explore a node using minimax adversarial search with limited depth and a heuristic function
	# TODO: implement alpha-beta pruning
	def minimax(self, node):
		if TOTAL_MOVES - node.round == 0:
			node.value = self.checkWinner(node.state)

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
					move[0],
					move[1],
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
					node.value = self.countScore(node.state)
					return node

		else:
			validMoves = self.getValidMoves(node.state, node.round, self.opp)
			for move in validMoves:
				newState = self.simMove(node.state, node.round, self.opp, move[0], move[1])
				child = Node(
					newState,
					node.round + 1,
					move[0],
					move[1],
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
					node.value = self.countScore(node.state)
					return node

	# get move (uses minimax)
	def move(self, **kwargs):
		state = kwargs['state']
		round = kwargs['round']
		node = Node(state, round, -1, -1)
		moveNode = self.minimax(node)
		return [moveNode.row, moveNode.col]
