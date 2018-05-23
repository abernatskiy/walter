#!/usr/bin/python3

import json
import pyrosim
import assembler
import fleet
import parts

num_cores = 1 # doesn't really work for short simulations, and for long ones it overfills memory, but whatevs

seconds = 52.0
dt = 0.05
camera_pos = [9, -12, 12]
play_blind = True
play_paused = False
debug = False
capture = False
use_rcw_gauges = False
use_fuel_gauge = False
use_switching_controllers = False

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

def illuminationAvg(ass0):
	assemblerSensorData = ass0.getSensorData()
	return sum(assemblerSensorData[3])/len(assemblerSensorData[3])

def illuminationMax(ass0):
	assemblerSensorData = ass0.getSensorData()
	return max(assemblerSensorData[3])

def proximityAvg(ass0):
	assemblerSensorData = ass0.getSensorData()
	return sum(assemblerSensorData[0])/len(assemblerSensorData[0])

def proximityMax(ass0):
	assemblerSensorData = ass0.getSensorData()
	return max(assemblerSensorData[0])

def wasStuckToStuff(ass0):
	assemblerSensorData = ass0.getSensorData()
	stickyTS = assemblerSensorData[4]
	#print(stickyTS)
	return 1. if any([ n!=0 for n in stickyTS]) else 0.

def singleRobotFitness(ass0, env):
	return illuminationIntegral(ass0) - proximityIntegral(ass0)

def addFleet(sim, controllerStr):
	myfleet = fleet.SixFleet(sim, pos=[0,0,0], kinds_of_light=[10,20,30], use_rcw_gauges=use_rcw_gauges, use_fuel_gauge=use_fuel_gauge, use_switching_controllers=use_switching_controllers)
	myfleet.setController(controllerStr)
	return myfleet

def positioningFitness(twoParts):
	partsTelemetry = [ part.getPartTelemetry() for part in twoParts ]
	numPoints = len(partsTelemetry[0][0][0])
	def pointDist(pt, sid, i):
		return sum([ (pt[0][sid][j][i] - pt[1][sid][j][i])**2 for j in range(3) ])
	#lightSqDistances = [ [ pointDist(partsTelemetry, sid, i) for sid in range(3) ] for i in range(numPoints) ] # for integral of square distance over time
	lightSqDistances = [ [ pointDist(partsTelemetry, sid, i) for sid in range(3) ] for i in [-1] ] # for square distance at the last moment
	return 375. - min([ sum(dists) for dists in lightSqDistances ])

def fleetIllumination(myfleet):
	#print([ illuminationMax(ass) for ass in myfleet.assemblers ])
	return sum([ illuminationAvg(ass) for ass in myfleet.assemblers ])

def fleetProximity(myfleet):
	return sum([ proximityAvg(ass) for ass in myfleet.assemblers ])

def fleetStuck(myfleet):
	return sum([ wasStuckToStuff(ass) for ass in myfleet.assemblers ])

def fleetFitness(robot, env):
	if robot is None or env is None:
		return -100000.
	pf = positioningFitness(env)
	ill = fleetIllumination(robot)
	prox = fleetProximity(robot)
	stuck = fleetStuck(robot)
	#print('pf={} ill={} prox={} stuck={}'.format(pf, ill, prox, stuck))
	return pf + ill - prox + stuck

def setUpEvaluation(controllerStr, robot_adder=addSingleRobot, environment_creator=createEnvironment):
	global debug, play_blind, play_paused, camera_pos, dt, seconds

	genome = json.loads(controllerStr)
	eval_time = int(seconds/dt) if type(genome) is list else int(genome['evaluationTime']/dt)
	pureCS = controllerStr if type(genome) is list else json.dumps(genome['controller'])

	sim = pyrosim.Simulator(eval_time=eval_time, dt=dt, gravity=0., disable_floor=True,
	                        debug=debug, play_blind=play_blind, play_paused=play_paused, capture=capture, use_textures=True,
	                        xyz=camera_pos)

	env = environment_creator(sim)
	robot = robot_adder(sim, pureCS)

	sim.create_collision_matrix('all')

	valid, error = sim.is_a_valid_simulation()
	if valid:
		return sim, robot, env
	else:
		print('Invalid simulation: {}'.format(error))
		return sim, None, None

def evaluateController(controllerStr, robot_adder=addSingleRobot, environment_creator=createEnvironment, fitness=singleRobotFitness):
	sim, robot, env = setUpEvaluation(controllerStr, robot_adder=robot_adder, environment_creator=environment_creator)

	sim.start()
	sim.wait_to_finish()

	return fitness(robot, env)

def readGenomes(inFile):
	genomes = {}
	with open(inFile, 'r') as input:
		for line in input:
			# print('Read genome ' + line)
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

		if capture:
			for sim, _, _ in materialsChunk:
				sim.make_movie()

		writeEvals(outPipe, evals)
