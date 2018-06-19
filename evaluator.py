#!/usr/bin/python3

import sys, glob, os, json, time
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
use_rcw_gauges = True
use_fuel_gauge = True
use_switching_controllers = False
plot_sensor_data = False
evolvable_evaluation_time = False
evolvable_fitness_coefficients = True

_low_fitness = -1.0 # equal to epsilons, so that probability is exactly zero

_system_wait = 0.1 # time given to the system to generate a core dump for a crashed simulation

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

class TimeSeries(object):
	def max(self):
		return max(self.data)
	def avg(self):
		return sum(self.data)/len(self.data)
	def min(self):
		return min(self.data)
	def any(self):
		return 1. if any([ n!=0 for n in self.data]) else 0.

class IlluminationTS(TimeSeries):
	threshold = -2.
	def __init__(self, robot):
		rid = robot.getSensorData()[3]
		self.data = [ v-IlluminationTS.threshold if v>IlluminationTS.threshold else 0. for v in rid ]

class ProximityTS(TimeSeries):
	max_reading = 1.
	def __init__(self, robot):
		rpd = robot.getSensorData()[0]
		self.data = [ ProximityTS.max_reading-v for v in rpd ]

class FuelGaugeTS(TimeSeries):
	def __init__(self, robot):
		rfd = robot.getSensorData()[8]
		self.data = [ 1.+v for v in rfd ]

class StucknessTS(TimeSeries):
	def __init__(self, robot):
		self.data = robot.getSensorData()[4]

def singleRobotFitness(ass0, env):
	raise NotImplementedError

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
	rawFitness = 375. - min([ sum(dists) for dists in lightSqDistances ])
	return 0. if rawFitness<0 else rawFitness

def fleetIllumination(myfleet):
	return sum([ IlluminationTS(ass).avg() for ass in myfleet.assemblers ])

def fleetProximity(myfleet):
	return sum([ ProximityTS(ass).avg() for ass in myfleet.assemblers ])

def fleetStuck(myfleet):
	return sum([ StucknessTS(ass).any() for ass in myfleet.assemblers ])

def fleetFuel(myfleet):
	return sum([ FuelGaugeTS(ass).min() for ass in myfleet.assemblers ])

def fleetFitness(fleet, env, showFitnessComponents=False):
	if fleet is None or env is None:
		return _low_fitness

	pf = positioningFitness(env)
	ill = fleetIllumination(fleet)
	prox = fleetProximity(fleet)
	stuck = fleetStuck(fleet)
	fuel = fleetFuel(fleet)
	if showFitnessComponents:
		print('pf={} ill={} prox={} stuck={} fuel={}'.format(pf, ill, prox, stuck, fuel))

	ultimateFitness = pf

	fc = fleet._fitness_coefficients
	if fc is None:
		currentFitness = pf + ill + prox + stuck + fuel
	else:
		currentFitness = pf + fc[0]*ill + fc[1]*prox + fc[2]*stuck + fc[3]*fuel

	return (ultimateFitness, currentFitness)

def setUpEvaluation(controllerStr, robot_adder=addSingleRobot, environment_creator=createEnvironment):
	global debug, play_blind, play_paused, camera_pos, dt, seconds

	genome = json.loads(controllerStr)
	eval_time = int(seconds/dt) if not evolvable_evaluation_time else int(genome['evaluationTime']/dt)
	fitness_coefficients = None if not evolvable_fitness_coefficients else genome['fitnessCoefficients']
	pureCS = controllerStr if (not evolvable_evaluation_time) and (not evolvable_fitness_coefficients) else json.dumps(genome['controller'])

	sim = pyrosim.Simulator(eval_time=eval_time, dt=dt, gravity=0., disable_floor=True,
	                        debug=debug, play_blind=play_blind, play_paused=play_paused, capture=capture, use_textures=True,
	                        xyz=camera_pos)

	env = environment_creator(sim)
	robot = robot_adder(sim, pureCS)

	sim.create_collision_matrix('all')

	robot._fitness_coefficients = fitness_coefficients

	valid, error = sim.is_a_valid_simulation()
	if valid:
		return sim, robot, env
	else:
		print('Invalid simulation: {}'.format(error))
		return sim, None, None

def evaluateController(controllerStr, robot_adder=addSingleRobot, environment_creator=createEnvironment, fitness=singleRobotFitness, showFitnessComponents=False):
	sim, robot, env = setUpEvaluation(controllerStr, robot_adder=robot_adder, environment_creator=environment_creator)

	sim.start()
	sim.wait_to_finish()

	if plot_sensor_data:
		fleetSensorData = robot.getSensorData()
		#print(fleetSensorData)
		from tools.robotSensorAnalyzer import plot_encephalogram
		plot_encephalogram(fleetSensorData, robot.assemblers[0].sensorLabels)

	return fitness(robot, env, showFitnessComponents=showFitnessComponents)

def readGenomes(inFile):
	genomes = {}
	#sys.stdout.write('IDs to evaluate:')
	with open(inFile, 'r') as input:
		for line in input:
			# print('Read genome ' + line)
			id, genome = line.split(' ', 1)
			id = int(id)
			genomes[id] = genome[:-1]
			#sys.stdout.write(' {}'.format(id))
	#sys.stdout.write('\n')
	#sys.stdout.flush()
	return genomes

def writeEvals(outFile, evals):
	#sys.stdout.write('IDs evaluated  :')
	with open(outFile, 'w') as output:
		for gid in sorted(evals.keys()):
			output.write(str(gid) + ' ' + ' '.join(map(str, evals[gid])) + '\n')
			#sys.stdout.write(' {}'.format(gid))
	#sys.stdout.write('\n')
	#sys.stdout.flush()

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
	cliParser.add_argument('configFileName', nargs='?', metavar='configFileName', type=str, help='INI file containing the configuration')
	cliArgs = cliParser.parse_args()

	inPipe = cliArgs.genomesFileName
	outPipe = cliArgs.evalsFileName
	configFile = cliArgs.configFileName

	# Parsing the config
	if not configFile is None:
		import configparser
		conf = configparser.RawConfigParser()
		conf.optionxform = str # required to keep the uppercase-containing fields working
		conf.read(configFile)

		seconds = conf.getfloat('simulation', 'seconds', fallback=seconds)
		dt = conf.getfloat('simulation', 'dt', fallback=dt)
		use_rcw_gauges = conf.getboolean('robot', 'use_rcw_gauges', fallback=use_rcw_gauges)
		use_fuel_gauge = conf.getboolean('robot', 'use_fuel_gauge', fallback=use_fuel_gauge)
		use_switching_controllers = conf.getboolean('robot', 'use_switching_controllers', fallback=use_switching_controllers)
		evolvable_evaluation_time = conf.getboolean('evaluation', 'evolvable_evaluation_time', fallback=evolvable_evaluation_time)
		evolvable_fitness_coefficients = conf.getboolean('evaluation', 'evolvable_fitness_coefficients', fallback=evolvable_fitness_coefficients)

	# Reading the genomes and evaluating them
	fitness = fleetFitness

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

			for gid, (sim, _, _) in zip(gidChunk, materialsChunk):
				try:
					sim.wait_to_finish()
				except RuntimeError:
					with open('offending_genome', 'a') as ogf:
						ogf.write(genomes[gid] + '\n')
					evals[gid] = (_low_fitness, _low_fitness)
					print('Simulation caught a runtime error. Offending genome {} is written offending_genome file'.format(gid))

					time.sleep(_system_wait)
					coredumps = glob.glob('core.*')
					for cd in coredumps:
						try:
							os.remove(cd)
						except OSError:
							pass
						print('Attempted removal of the following core dump file: {}'.format(cd))

#			print('simulations done')

			for gid, (_, robot, env) in zip(gidChunk, materialsChunk):
				if not gid in evals.keys():
					evals[gid] = fitness(robot, env)
#			print('fitness recorded')

		if capture:
			for sim, _, _ in materialsChunk:
				sim.make_movie()

		writeEvals(outPipe, evals)
