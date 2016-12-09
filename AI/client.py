#!/usr/bin/env python

import sys
import socket
import time
import json
from random import randint

from SmartAI import SmartAI
from RandomAI import RandomAI
from NewAI import NewAI

END_TURN = -999

state = [[0 for x in range(8)] for y in range(8)]

# establish a connection with the server
def initClient(me, host):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_address = (host, 3333 + me)
	print >> sys.stderr, 'starting up on %s port %s' % server_address
	sock.connect(server_address)

	info = sock.recv(1024)

	return sock

# read a message from the server
def readMessage(sock):
	message = sock.recv(1024).split('\n')

	turn = int(message[0]) # update turn

	if turn == END_TURN:
		return (turn, -1, -1, -1)

	round = int(message[1]) # update round
	t1 = float(message[2]) # update amount of time available to player 1
	t2 = float(message[3]) # update amount of time available to player 2

	count = 4
	for i in range(8):
		for j in range(8):
			state[i][j] = int(message[count])
			count += 1

	return (turn, round, t1, t2)

def winner(state):
	score = 0
	for row in state:
		for slot in row:
			if slot == 1:
				score += 1
			if slot == 2:
				score -= 1
	if score > 0:
		return 1
	if score < 0:
		return 2
	return 0

# establish a connection with the server and play whenever it is this player's turn
def playGame(me, host, AI):
	sock = initClient(me, host)
	turn = 0
	while (turn != END_TURN):
		(turn, round, t1, t2) = readMessage(sock)
		if (turn == me):
			myMove = AI.move(turn=turn, round=round, state=state, t1=t1, t2=t2)
			print myMove
			sock.send(str(myMove[0]) + '\n' + str(myMove[1]) + '\n')
	time.sleep(1)
	return winner(state)

# call: python client.py [ipaddress] [player_number] [AIType]
#   ipaddress is the ipaddress on the computer the server was launched on.  Enter 'localhost' if it is on the same computer
#   player_number is 1 (for the black player) and 2 (for the white player)
#	AIType is the type of AI to use (smart or random)
if __name__ == '__main__':
	me = int(sys.argv[2])
	host = sys.argv[1]
	AIType = sys.argv[3]

	if AIType == 'smart':
		AI = SmartAI(me)
	elif AIType == 'random':
		AI = RandomAI(me)
	elif AIType == 'new' or not len(AIType):
		AI = NewAI(me)
	else:
		with open(AIType) as file:
			config = json.load(file)
		if not 'ai' in config:
			print 'No AI type specified'
			print config
			sys.exit(-999)
		if config['ai'] == 'smart':
			AI = SmartAI(me, config)
		elif config['ai'] == 'random':
			AI = RandomAI(me, config)
		elif config['ai'] == 'new':
			AI = NewAI(me, config)
		else:
			print 'Unknown AI type'
			sys.exit(-999)

	sys.exit(playGame(me, host, AI))
