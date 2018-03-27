#!/usr/bin/python3

import pyrosim
import assembler
import fleet
import parts

num_cores = 4 # doesn't really work for short simulations, and for long ones it overfills memory, but whatevs

seconds = 200.0
dt = 0.05
camera_pos = [9, -12, 12]
play_blind = True
play_paused = False
debug = False

def createEnvironment(sim):
	partList = []
	partList.append(parts.Cylinder(sim, (10.,10., 3.), (-1.,0.,0.), 1))
	partList.append(parts.Cylinder(sim, (-10.,10., 3.), (1.,0.,0.), -1))
	return partList

def addSingleRobot(sim, controllerStr):
	ass0 = assembler.Assembler(sim, [0,0,3])
	ass0.setController(controllerStr)
	return ass0

def addSingleRobotWithSwitch(sim, controllerStr):
	ass0 = assembler.AssemblerWithSwitch(sim, [0,0,3])
	ass0.setController(controllerStr)
	return ass0

def illuminationIntegral(ass0):
	assemblerSensorData = ass0.getSensorData()
	return sum(assemblerSensorData[3])

def proximityIntegral(ass0):
	assemblerSensorData = ass0.getSensorData()
	return sum(assemblerSensorData[0])

def wasStuckToStuff(ass0):
	assemblerSensorData = ass0.getSensorData()
	stickyTS = assemblerSensorData[4]
	return 1. if any([ n!=0 for n in stickyTS]) else 0.

def singleRobotFitness(ass0, env):
	return illuminationIntegral(ass0) - proximityIntegral(ass0)

def addFleet(sim, controllerStr):
	myfleet = fleet.SixFleet(sim, pos=[0,0,0], kinds_of_light=[10,20,30])
	myfleet.setController(controllerStr)
	return myfleet

def positioningError(twoParts):
	partsTelemetry = [ part.getPartTelemetry() for part in twoParts ]
	numPoints = len(partsTelemetry[0][0][0])
	def pointDist(pt, sid, i):
		return sum([ (pt[0][sid][j][i] - pt[1][sid][j][i])**2 for j in range(3) ])
	#lightSqDistances = [ [ pointDist(partsTelemetry, sid, i) for sid in range(3) ] for i in range(numPoints) ] # for integral of square distance over time
	lightSqDistances = [ [ pointDist(partsTelemetry, sid, i) for sid in range(3) ] for i in [-1] ] # for square distance at the last moment
	return sum([ sum(dists) for dists in lightSqDistances ])

def fleetIllumination(myfleet):
	return sum([ illuminationIntegral(ass) for ass in myfleet.assemblers ])

def fleetProximity(myfleet):
	return sum([ proximityIntegral(ass) for ass in myfleet.assemblers ])

def fleetStuck(myfleet):
	return sum([ wasStuckToStuff(ass) for ass in myfleet.assemblers ])

def fleetFitness(robot, env):
	pe = positioningError(env)
	ill = fleetIllumination(robot)
	prox = fleetProximity(robot)
	stuck = fleetStuck(robot)
	return -pe + ill - prox + stuck # didn't normalize lol

def setUpEvaluation(controllerStr, robot_adder=addSingleRobot, environment_creator=createEnvironment):
	global debug, play_blind, play_paused, camera_pos, dt, seconds
	eval_time = int(seconds/dt)
	sim = pyrosim.Simulator(eval_time=eval_time, dt=dt, gravity=0., disable_floor=True,
	                        debug=debug, play_blind=play_blind, play_paused=play_paused, capture=False, use_textures=True,
	                        xyz=camera_pos)

	env = environment_creator(sim)
	robot = robot_adder(sim, controllerStr)

	sim.create_collision_matrix('all')
	return sim, robot, env

def evaluateController(controllerStr, robot_adder=addSingleRobot, environment_creator=createEnvironment, fitness=singleRobotFitness):
	sim, robot, env = setUpEvaluation(controllerStr, robot_adder=robot_adder, environment_creator=environment_creator)

	sim.start()
	sim.wait_to_finish()

	return fitness(robot, env)

def readGenomes(inFile):
	genomes = {}
	with open(inFile, 'r') as input:
		for line in input:
			id, genome = line.split(' ', 1)
			id = int(id)
			genomes[id] = genome[:-1]
	return genomes

def writeEvals(outFile, evals):
	with open(outFile, 'w') as output:
		for gid in sorted(evals.keys()):
			output.write(str(gid) + ' ' + str(evals[gid]) + '\n')

def chunks(l, n):
	'''Yield successive n-sized chunks from l'''
	for i in range(0, len(l), n):
		yield l[i:i + n]


if __name__ == "__main__":
	# Parsing CLI
	import argparse
	cliParser = argparse.ArgumentParser(description='Evaluator of Walter system genomes', epilog='Genomes are in JSON format. The code is the documentation ATM.')
	cliParser.add_argument('genomesFileName', metavar='genomesFileName', type=str, help='file or pipe from which to read the genomes')
	cliParser.add_argument('evalsFileName', metavar='evalsFileName', type=str, help='file or pipe to which to write the evaluations')
	cliArgs = cliParser.parse_args()

	inPipe = cliArgs.genomesFileName
	outPipe = cliArgs.evalsFileName

	fitness=fleetFitness

	# Reading the genomes and evaluating them
	while True:
		genomes = readGenomes(inPipe)
		evals = {}
		for gidChunk in chunks(sorted(genomes.keys()), num_cores):
			materialsChunk = []
			for gid in gidChunk:
				materialsChunk.append(setUpEvaluation(genomes[gid],
				                                      robot_adder=addFleet,
				                                      environment_creator=createEnvironment))
#			print('evaluating genomes {}'.format(str(gidChunk)))

			for sim, _, _ in materialsChunk:
				sim.start()
#			print('simulations started')

			for sim, _, _ in materialsChunk:
				sim.wait_to_finish()
#			print('simulations done')

			for gid, (_, robot, env) in zip(gidChunk, materialsChunk):
				evals[gid] = fitness(robot, env)
#			print('fitness recorded')

		writeEvals(outPipe, evals)
