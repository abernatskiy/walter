#!/usr/bin/python3

import pyrosim
import assembler
import parts
import math

seconds = 10.0
dt = 0.05
eval_time = int(seconds/dt)
camera_pos = [9, -12, 12]
play_blind = False
play_paused = True
debug = True
capture = False
use_rcw_gauges = True
use_fuel_gauge = True
use_switching_controllers = False
plot_sensor_data = True
evolvable_evaluation_time = False
evolvable_fitness_coefficients = True

_low_fitness = -10000.

class TestEnvironment(object):
	def __init__(self, sim, use_rcw_gauges=True, use_fuel_gauge=True):
		# We begin by adding cylinders
		self.parts = []
		self.parts.append(parts.Cylinder(sim, (10.,10., 3.), (-1.,0.,0.), 1))
		self.parts.append(parts.Cylinder(sim, (-10.,10., 3.), (1.,0.,0.), -1))

		# Then we add assemblers at the points where their corresponding light sources are
		self.assemblers = []
		radius = 2.5 + 0.25/2
		for i in range(3):
			pos = [[ 5.*chirality, radius*math.cos(chirality*2.*math.pi*i/3) + 10.,
			         3.+radius*math.sin(2.*math.pi*i/3)] for chirality in [1,-1] ] # actually, just at the fringe for now

			robofun = assembler.Assembler
			kinds_of_light = [10, 20, 30]
			self.assemblers.append(robofun(sim, pos[0], kind_of_light=kinds_of_light[i], use_rcw_gauges=use_rcw_gauges, use_fuel_gauge=use_fuel_gauge))
			self.assemblers.append(robofun(sim, pos[1], kind_of_light=kinds_of_light[i], use_rcw_gauges=use_rcw_gauges, use_fuel_gauge=use_fuel_gauge))
			self.assemblers[-2].connectTetherToOther(self.assemblers[-1])
		self._fitness_coefficients = None
		self.setController()

	def setController(self):
		for ass in self.assemblers:
			mns = ass._addMotorNeurons({'alpha': [1000.] + [0.]*5, 'tau': [1.]*6, 'initialState': [-1.]*6})
			bias = ass.sim.send_bias_neuron()
			synapses = [ ass.sim.send_synapse(bias, mns[4], 1.0), ass.sim.send_synapse(bias, mns[5], 1.0) ]

	def getSensorData(self):
		sensorData = []
		for ass in self.assemblers:
			sensorData.append(ass.getSensorData())
		return sensorData

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

	fc = fleet._fitness_coefficients
	if fc is None:
		return pf + ill + prox + stuck + fuel
	else:
		return pf + fc[0]*ill + fc[1]*prox + fc[2]*stuck + fc[3]*fuel

if __name__ == '__main__':
	sim = pyrosim.Simulator(eval_time=eval_time, dt=dt, gravity=0., disable_floor=True,
	                        debug=debug, play_blind=play_blind, play_paused=play_paused, capture=capture, use_textures=True,
	                        xyz=camera_pos)

	te = TestEnvironment(sim)

	sim.create_collision_matrix('all')

	valid, error = sim.is_a_valid_simulation()
	if not valid:
		print('Invalid simulation: {}'.format(error))

	sim.start()

	sim.wait_to_finish()

	if plot_sensor_data:
		fleetSensorData = te.getSensorData()
		from tools.robotSensorAnalyzer import plot_encephalogram
		plot_encephalogram(fleetSensorData, te.assemblers[0].sensorLabels)

	print(fleetFitness(te, te.parts, showFitnessComponents=True))
