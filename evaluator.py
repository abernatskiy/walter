#!/usr/bin/python2

import pyrosim
import assembler
import fleet
import parts

seconds = 15.0
dt = 0.05
camera_pos = [9,-12,12]
play_blind = True
play_paused = False
debug = False

def createEnvironment(sim):
	partList = []
	partList.append(parts.Cylinder(sim, (10.,0., 3.), (1.,0.,0.)))
	return partList

def addSingleRobot(sim, controllerStr):
	ass0 = assembler.Assembler(sim, [0,0,3])
	ass0.setController(controllerStr)
	return ass0

def addSingleRobotWithSwitch(sim, controllerStr):
	ass0 = assembler.AssemblerWithSwitch(sim, [0,0,3])
	ass0.setController(controllerStr)
	return ass0

def singleRobotFitness(ass0, env):
	assemblerSensorData = ass0.getSensorData()
	return sum(assemblerSensorData[3]) - sum(assemblerSensorData[0]) # integral of light minus integral of proximity

def addFleet(sim, controllerStr):
	myfleet = fleet.SixFleet(sim, pos=[0,0,0], kinds_of_light=[10,20,30])
	myfleet.setController(controllerStr)
	return myfleet

def fleetFitness(robot, env):
	return 0.

def evaluateController(controllerStr, robot_adder=addSingleRobot, environment_creator=createEnvironment, fitness=singleRobotFitness):
	global debug, play_blind, play_paused, camera_pos, dt, seconds
	eval_time = int(seconds/dt)
	sim = pyrosim.Simulator(eval_time=eval_time, dt=dt, gravity=0.,
	                        debug=debug, play_blind=play_blind, play_paused=play_paused, capture=False, use_textures=True,
	                        xyz=camera_pos)

	env = environment_creator(sim)
	robot = robot_adder(sim, controllerStr)

	sim.create_collision_matrix('all')
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

if __name__ == "__main__":
	# Parsing CLI
	import argparse
	cliParser = argparse.ArgumentParser(description='Evaluator of Walter system genomes', epilog='Genomes are in JSON format. The code is the documentation ATM.')
	cliParser.add_argument('genomesFileName', metavar='genomesFileName', type=str, help='file or pipe from which to read the genomes')
	cliParser.add_argument('evalsFileName', metavar='evalsFileName', type=str, help='file or pipe to which to write the evaluations')
	cliArgs = cliParser.parse_args()

	inPipe = cliArgs.genomesFileName
	outPipe = cliArgs.evalsFileName

	# Reading the genomes and evaluating them
	while True:
		genomes = readGenomes(inPipe)
		evals = {}
		for gid in sorted(genomes.keys()):
			evals[gid] = evaluateController(initial_conditions, genomes[gid])
		writeEvals(outPipe, evals)
