#!/usr/bin/env python

import random

from AI import AI

class RandomAI(AI):
	def __init__(self, me):
		AI.__init__(self, me)

	def move(self, **kwargs):
		state = kwargs['state']
		round = kwargs['round']
		validMoves = self.getValidMoves(state, round, self.me)
		return validMoves[random.randint(0,len(validMoves) - 1)]
