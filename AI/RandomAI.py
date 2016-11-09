#!/usr/bin/env python

import random

from AI import AI

class RandomAI(AI):
	def __init__(self, me, config=None):
		AI.__init__(self, me)
		# we don't actually use a config, at least for now

	# get move
	def move(self, **kwargs):
		state = kwargs['state']
		round = kwargs['round']
		validMoves = self.getValidMoves(state, round, self.me)
		# just choose a random valid move
		return validMoves[random.randint(0,len(validMoves) - 1)]
