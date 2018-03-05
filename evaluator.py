#!/usr/bin/python2

import pyrosim
import assembler
import part

seconds = 15.0
dt = 0.05
camera_pos = [9,-12,12]
play_blind = False
debug = False

def evaluateController(initialConditions, controllerStr):
	eval_time = int(seconds/dt)
	sim = pyrosim.Simulator(eval_time=eval_time, dt=dt, gravity=0.,
	                        debug=debug, play_blind=play_blind, play_paused=False, capture=False, use_textures=True,
	                        xyz=camera_pos)
	ass0 = assembler.Assembler(sim, initialConditions)
	ass0.setController(controllerStr)

	part0 = part.Part(sim, (10.,0., 3.), (1.,0.,0.))

	sim.create_collision_matrix('all')
	sim.start()
	sim.wait_to_finish()

	assemblerSensorData = ass0.getSensorData()

	return sum(assemblerSensorData['light']) - sum(assemblerSensorData['proximity'][0])

def readGenomes(inFile):
	genomes = {}
	with open(inFile, 'r') as input:
		for line in input:
			id, genome = line.split(' ', 1)
			genomes[id] = genome[:-1]
	return genomes

def writeEvals(outFile, evals):
	with open(outFile, 'w') as output:
		for gid, geval in evals.iteritems():
			output.write(str(gid) + ' ' + str(geval) + '\n')

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
		for gid, genome in genomes.iteritems():
			evals[gid] = evaluateController([0,0,3], genome)
		writeEvals(outPipe, evals)
