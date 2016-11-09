#!/usr/bin/env python
import json
import os
import subprocess
import sys
import time

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print 'USAGE: python test.py [match_settings] [player_one] [player_two]'
		sys.exit()

	with open('config/match/%s.json' % (sys.argv[1])) as file:
		match_settings = json.load(file)
	#with open('config/player/%s.json' % (sys.argv[2])) as file:
	#	player_one = json.load(file)
	#with open('config/player/%s.json' % (sys.argv[3])) as file:
	#	player_two = json.load(file)

	err = 0
	one_wins = 0
	two_wins = 0
	for round in range(match_settings['rounds']):
		print "Round %d" % (round+1)

		serverp = subprocess.Popen(('java', 'Reversi', '%d' % match_settings['timelimit']), cwd='Server')
		time.sleep(3)	# make sure the server has bound the port before anyone connects
		onep = subprocess.Popen(('python', 'client.py', 'localhost', '1', '../config/player/%s.json'%(sys.argv[2])), cwd='AI')
		time.sleep(1)	# don't try to connect at the same time
		twop = subprocess.Popen(('python', 'client.py', 'localhost', '2', '../config/player/%s.json'%(sys.argv[3])), cwd='AI')

		while 1:
			time.sleep(1)
			serverp.poll()
			onep.poll()
			twop.poll()
			if serverp.returncode != None or onep.returncode != None or twop.returncode != None:
				break

		if onep.returncode != None:
			if twop.returncode != None and onep.returncode != twop.returncode:
				print 'Something went wrong'
				err = 1
			else:
				if onep.returncode == 1:
					print 'Player one wins'
					one_wins += 1
				elif onep.returncode == 2:
					print 'Player two wins'
					two_wins += 1
				elif onep.returncode == 0:
					print 'Draw'
				else:
					print 'Something went wrong'
					err = 1
		elif twop.returncode != None:
			if twop.returncode == 1:
				print 'Player one wins'
				one_wins += 1
			elif twop.returncode == 2:
				print 'Player two wins'
				two_wins += 1
			elif twop.returncode == 0:
				print 'Draw'
			else:
				print 'Something went wrong'
				err = 1
		else:
			print 'Something went wrong'
			err = 1

		try:
			serverp.terminate()
		except Exception as e:
			pass
		try:
			onep.terminate()
		except Exception as e:
			pass
		try:
			twop.terminate()
		except Exception as e:
			pass

		time.sleep(3)	# make sure the server releases the port

		print ''
		if err:
			break

	print 'Final Score: %d to %d' % (one_wins, two_wins)
	if one_wins > two_wins:
		print 'Player One Wins'
	elif two_wins > one_wins:
		print 'Player Two Wins'
	else:
		print 'Draw'
