#!/usr/bin/env python

import random

from AI import AI

TOTAL_SLOTS = 64

class Node(object):
	def __init__(self, state, round, row, col, depth=2, max=True, alpha=-float('inf'), beta=float('inf')):
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

	def countScore(self, state):
		score = 0
		for row in state:
			for slot in row:
				if slot == self.me:
					score += 1
		if score > TOTAL_SLOTS - score:
			return float('inf')
		else:
			return -float('inf')

	def scoreRange(self, state, r1, r2, points):
		score = 0
		for i in r1:
			for j in r2:
				if state[i][j] == self.me:
					score += points
				elif state[i][j] == self.opp:
					score -= points
		return score

	# maximize moves available to me, minimize moves available to opponent
	def heuristic(self, node):
		score = 0

		"""
		valuations of various cell types
		c   ceb e   e   e   e   ceb c
		ceb ccb ecb ecb ecb ecb ccb ceb
		e   ecb c   c   c   c   ecb e
		e   ecb c   c   c   c   ecb e
		e   ecb c   c   c   c   ecb e
		e   ecb c   c   c   c   ecb e
		ceb ccb ecb ecb ecb ecb ccb ceb
		c   ceb e   e   e   e   ceb c
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

		myMoves = len(self.getValidMoves(node.state, node.round, self.me))
		oppMoves = len(self.getValidMoves(node.state, node.round, self.opp))
		optionAdvantage = (myMoves - oppMoves)
		score += optionAdvantage

		return score

	def minimax(self, node):
		if TOTAL_SLOTS - node.round == 0:
			node.value = self.countScore(node.state)

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
					max=False
				)
				child.value = self.minimax(child).value
				children.append(child)
			if len(validMoves) > 0:
				best = max(children, key=lambda node: node.value)
				node.value = best.value
				return best
			else:
				node.max = False
				return self.minimax(node)
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
					max=False
				)
				child.value = self.minimax(child).value
				children.append(child)
			if len(validMoves) > 0:
				best = min(children, key=lambda node: node.value)
				node.value = best.value
				return best
			else:
				node.max = True
				return self.minimax(node)

	def move(self, **kwargs):
		state = kwargs['state']
		round = kwargs['round']
		node = Node(state, round, -1, -1)
		moveNode = self.minimax(node)
		return [moveNode.row, moveNode.col]
