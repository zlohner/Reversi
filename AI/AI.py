#!/usr/bin/env python

class AI(object):
	def __init__(self, me):
		self.me = me
		self.opp = 1 if me == 2 else 2

	# check if player can play on a square based on given direction (combination of dx and dy)
	def checkDirection(self, state, row, col, dx, dy, player):
		oppFound = False
		r = row+dx
		c = col+dy

		while r >= 0 and r < 8 and c >= 0 and c < 8:
			if state[r][c] == 0:
				return False	# we never found our existing piece
			elif state[r][c] == player:
				return oppFound	# playable only if we found an enemy
			else:
				oppFound = True
				r += dx
				c += dy
		return False	# we hit the edge of the map

	# check all directions
	def isValid(self, state, row, col, player):
		for dx in range(-1, 2):
			for dy in range(-1, 2):
				if ((dx == 0) and (dy == 0)):
					continue

				if (self.checkDirection(state, row, col, dx, dy, player)):
					return True

		return False

	# generates the set of valid moves for the player
	def getValidMoves(self, state, round, player):
		validMoves = []

		if (round < 4):
			if (state[3][3] == 0):
				validMoves.append([3, 3])
			if (state[3][4] == 0):
				validMoves.append([3, 4])
			if (state[4][3] == 0):
				validMoves.append([4, 3])
			if (state[4][4] == 0):
				validMoves.append([4, 4])
		else:
			for i in range(8):
				for j in range(8):
					if state[i][j] == 0 and self.isValid(state, i, j, player):
						validMoves.append([i, j])
		return validMoves

	# simulate the new state after making a move at (row, col)
	def simMove(self, state, round, player, row, col):
		newState = [[state[x][y] for y in range(8)] for x in range(8)]

		# in each direction...
		for dx in range(-1, 2):
			for dy in range(-1, 2):
				if ((dx == 0) and (dy == 0)):
					continue

				# we flip all the opponents we find, if we find our existing piece
				toFlip = []
				r = row+dx
				c = col+dy
				while r >= 0 and r < 8 and c >= 0 and c < 8:
					if state[r][c] == 0:
						break
					elif state[r][c] == player:
						for square in toFlip:
							newState[square[0]][square[1]] = player
						break
					else:
						toFlip.append([r, c])
						r += dx
						c += dy

		# also give us our new piece
		newState[row][col] = player

		return newState
