#!/usr/bin/env python

class AI(object):
	def __init__(self, me):
		self.me = me
		self.opp = 1 if me == 2 else 2

	def checkDirection(self, state, row, col, dx, dy, player):
		opp = 1 if player == 2 else 2
		sequence = []
		for i in range(1,8):
			r = row + dy * i
			c = col + dx * i

			if ((r < 0) or (r > 7) or (c < 0) or (c > 7)):
				break

			sequence.append(state[r][c])

		count = 0
		for i in range(len(sequence)):
			if (sequence[i] == opp):
				count += 1
			else:
				if ((sequence[i] == player) and (count > 0)):
					return True
				break

		return False

	def couldBe(self, state, row, col, player):
		for dx in range(-1, 2):
			for dy in range(-1, 2):
				if ((dx == 0) and (dy == 0)):
					continue

				if (self.checkDirection(state, row, col, dx, dy, player)):
					return True

		return False

	# generates the set of valid moves for the player; returns a list of valid moves (validMoves)
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
					if (state[i][j] == 0):
						if (self.couldBe(state, i, j, player)):
							validMoves.append([i, j])
		return validMoves

	def simMove(self, state, round, player, row, col):
		newState = [[state[x][y] for y in range(8)] for x in range(8)]

		toFlip = []
		for dx in range(-1, 2):
			for dy in range(-1, 2):
				if ((dx == 0) and (dy == 0)):
					continue

				if (self.checkDirection(state, row, col, dx, dy, player)):
					for i in range(1,8):
						r = row + dy * i
						c = col + dx * i

						if ((r < 0) or (r > 7) or (c < 0) or (c > 7)):
							break

						toFlip.append((r, c))

		for (r, c) in toFlip:
			newState[r][c] = player

		newState[row][col] = player
		return newState
