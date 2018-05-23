import json
from copy import copy

class Assembler(object):
	body_radius = 0.25
	body_mass = 1.0
	body_color = (0.,1.,0.)
	proximity_range = 1.0
	proximity_offset = (0.,0.,0.)
	max_thrust = 1.0
	thrust_threshold = -0.8
	momentum_budget = 10.
	max_torque = 0.1
	tether_force_coefficient = 1.
	tether_dampening_coefficient = 10.
	proximity_channels = [0,1,2] # colors (3,4,5) are not used for now
	adhesion_kind = 10

	default_motor_labels = ['thruster', 'rcwX', 'rcwY', 'rcwZ', 'adhesive']
	default_num_motors = 5
	default_sensor_labels = ['proximityR', 'proximityT', 'proximityP', 'light', 'adhesive']
	default_num_sensors = 5
	# FIXME: make maps from a string labels of to sensor/motor returning functions and facilities for calling these functions with any additional parameters needed

	def __init__(self, sim, initpos, kind_of_light=0, use_rcw_gauges=False, use_fuel_gauge=False):
		'''Creates an assembler robot at the geometrical position initpos'''

		self.sim = sim
		self._createBaselineAssemblerInSimulation(initpos, kind_of_light=kind_of_light)
		if use_rcw_gauges:
			self._addRCWGauges()
		if use_fuel_gauge:
			self._addFuelGauge()

	def _createBaselineAssemblerInSimulation(self, initpos, kind_of_light=0):
		x,y,z = initpos
		bcr,bcg,bcb = Assembler.body_color

		# Robot's body
		self.body = self.sim.send_sphere(x=x, y=y, z=z,
		                            radius=Assembler.body_radius,
		                            mass=Assembler.body_mass,
		                            r=bcr, g=bcg, b=bcb)

		# Motors
		self.motors = []

		thruster = self.sim.send_thruster(self.body,
		                             x=x, y=y, z=z-Assembler.body_radius,
		                             lo=0., hi=-1.*Assembler.max_thrust,
		                             threshold=Assembler.thrust_threshold, momentumBudget=momentum_budget)
		self.motors.append((thruster, 0))

		rcw = self.sim.send_reaction_control_wheel(self.body,
		                                      max_torque=Assembler.max_torque,
		                                      momentum_budgets=(0.05, 0.05, 0.05))
		for input_index in [0,1,2]:
			self.motors.append((rcw, input_index))

		sticky = self.sim.send_adhesive_joint(self.body, adhesion_kind=Assembler.adhesion_kind)
		self.motors.append((sticky, 0))

		self.numMotors = Assembler.default_num_motors
		self.motorLabels = Assembler.default_motor_labels

		# Sensors
		self.sensors = []

		proximitySensor = self.sim.send_proximity_sensor(body_id=self.body,
		                                            x=0, y=0, z=0,
		                                            max_distance=Assembler.proximity_range) # FIXME: add a realistic offset eventually
		for svi in Assembler.proximity_channels:
			self.sensors.append((proximitySensor, svi))

		lightSensor = self.sim.send_light_sensor(self.body,
		                                    kind_of_light=kind_of_light,
		                                    logarithmic=True) # FIXME: add a realistic offset eventually
		self.sensors.append((lightSensor, 0))

		stickinessSensor = self.sim.send_proprioceptive_sensor(joint_id=sticky)
		self.sensors.append((stickinessSensor, 0))

		self.numSensors = Assembler.default_num_sensors
		self.sensorLabels = Assembler.default_sensor_labels

	def connectTetherToOther(self, other):
		assert self.sim.id == other.sim.id, 'Robots must be in the same simulator to connect them with tethers'
		tether = self.sim.send_tether(self.body, other.body, force_coefficient=Assembler.tether_force_coefficient, dampening_coefficient=Assembler.tether_dampening_coefficient)
		tether_proprioception = self.sim.send_proprioceptive_sensor(joint_id=tether)
		self._addTether(tether, tether_proprioception, 0)
		other._addTether(tether, tether_proprioception, 1)

	def _addTether(self, tether_id, proprioceptive_sensor_id, index):
		self.motors.append((tether_id, index))
		self.motorLabels.append('tether')
		self.numMotors += 1
		self.sensors.append((proprioceptive_sensor_id, index))
		self.sensorLabels.append('tetherTension')
		self.numSensors += 1

	def _addRCWGauges(self):
		rcwid, _ = self.motors[self.motorLabels.index('rcwX')]
		gaugeid = self.sim.send_proprioceptive_sensor(joint_id=rcwid)
		self.sensors.append((gaugeid, 0))
		self.sensorLabels.append('rcwXgauge')
		self.sensors.append((gaugeid, 1))
		self.sensorLabels.append('rcwYgauge')
		self.sensors.append((gaugeid, 2))
		self.sensorLabels.append('rcwZgauge')
		self.numSensors += 3

	def _addFuelGauge(self):
		thrusterid, _ = self.motors[self.motorLabels.index('thruster')]
		gaugeid = self.sim.send_proprioceptive_sensor(joint_id=thrusterid)
		self.sensors.append((gaugeid, 0))
		self.sensorLabels.append('thrusterGauge')
		self.numSensors += 1

	def setController(self, controllerStr):
		annParams = json.loads(controllerStr)
		self._addController(annParams)

	def _addController(self, annParams):
		self.numHiddenNeurons = annParams['numHiddenNeurons']

		self.sensorNeurons = self._addSensorNeurons()
		self.hiddenNeurons = self._addHiddenNeurons(annParams['hiddenNeuronsParams'])
		if not self.numHiddenNeurons == len(self.hiddenNeurons)-1:
			raise ValueError('Declared number of hidden neurons ({}) is different from the number of hidden neurons supplied ({})'.format(self.numHiddenNeurons, len(self.hiddenNeurons)-1))
		self.motorNeurons = self._addMotorNeurons(annParams['motorNeuronsParams'])
		self._addSynapses(annParams['synapsesParams'])

	def _addSensorNeurons(self):
		'''Adds sensor neurons to all sensors'''
		sensorNeurons = []
		for sen, svi in self.sensors:
			sensorNeurons.append(self.sim.send_sensor_neuron(sensor_id=sen, svi=svi))
		return sensorNeurons

	def _addHiddenNeurons(self, hnParams, addBias=True):
		'''Adds hidden neurons'''
		hnInitialStates = hnParams['initialState']
		hnTaus = hnParams['tau']
		hnAlphas = hnParams['alpha']

		hiddenNeurons = []

		if addBias:
			hiddenNeurons.append(self.sim.send_bias_neuron())
		for i in range(len(hnTaus)):
			hiddenNeurons.append(self.sim.send_hidden_neuron(tau=hnTaus[i],
				                                                    alpha=hnAlphas[i],
			                                                      start_value=hnInitialStates[i]))
		return hiddenNeurons

	def _addMotorNeurons(self, mnParams):
		'''Adds motor neurons to all motors'''
		mnInitialStates = mnParams['initialState']
		mnTaus = mnParams['tau']
		mnAlphas = mnParams['alpha']

		motorNeurons = []
		for i in range(self.numMotors):
			mot, mii = self.motors[i]
			motorNeurons.append(self.sim.send_motor_neuron(joint_id=mot,
	                                                        start_value=mnInitialStates[i],
	                                                        tau=mnTaus[i],
	                                                        alpha=mnAlphas[i],
			                                                    input_index=mii))
		return motorNeurons

	def _addSynapses(self, synParams):
		self.synapses = {}
		self.synapses['sensorToHidden'] = self._wireALayer(self.sensorNeurons, self.hiddenNeurons, synParams['sensorToHidden'])
		self.synapses['hiddenToHidden'] = self._wireALayer(self.hiddenNeurons, self.hiddenNeurons, synParams['hiddenToHidden'])
		self.synapses['hiddenToMotor' ] = self._wireALayer(self.hiddenNeurons, self.motorNeurons,  synParams['hiddenToMotor'])

	def _wireALayer(self, ngroup1, ngroup2, synapses):
		return [ self.sim.send_synapse(ngroup1[i], ngroup2[j], w) for i,j,w in synapses ]

	def getSensorData(self):
		sensorData = []
		for sen, svi in self.sensors:
			sensorData.append(self.sim.get_sensor_data(sen, svi=svi))
		return sensorData

class AssemblerWithSwitch(Assembler):
	def _addController(self, controllerParams):
		self.numBehavioralControllers = controllerParams['numBehavioralControllers']

		self.sensorNeurons = self._addSensorNeurons() # from base class
		self.trueMotorNeurons = self._addTrueMotorNeurons()

		self.behavioralControllers = []
		for bc in controllerParams['behavioralControllers']:
			self.behavioralControllers.append(self._addBehavioralController(bc))

		self.governingController = self._addGoverningController(controllerParams['governingController'])

		self._addParallelSwitch()

	def _addTrueMotorNeurons(self):
		trueMotorNeurons = []
		for mot, mii in self.motors:
			trueMotorNeurons.append(self.sim.send_motor_neuron(joint_id=mot,
	                                                            start_value=0.,
	                                                            tau=1.,
	                                                            alpha=0.,
			                                                        input_index=mii))
		# NOTE: start value is questionable
		return trueMotorNeurons

	def _addBehavioralController(self, bcparams):
		controller = {}
		controller['numHiddenNeurons'] = bcparams['numHiddenNeurons']

		controller['hiddenNeurons'] = self._addHiddenNeurons(bcparams['hiddenNeuronsParams'])
		controller['motorNeurons'] = self._addHiddenNeurons(bcparams['motorNeuronsParams'], addBias=False)

		synParams = bcparams['synapsesParams']
		controller['synapses'] = {}
		controller['synapses']['sensorToHidden'] = self._wireALayer(self.sensorNeurons, controller['hiddenNeurons'], synParams['sensorToHidden'])
		controller['synapses']['hiddenToHidden'] = self._wireALayer(controller['hiddenNeurons'], controller['hiddenNeurons'], synParams['hiddenToHidden'])
		controller['synapses']['hiddenToMotor' ] = self._wireALayer(controller['hiddenNeurons'], controller['motorNeurons'],  synParams['hiddenToMotor'])

		return controller

	def _addGoverningController(self, gcparams):
		controller = {}
		controller['numHiddenNeurons'] = gcparams['numHiddenNeurons']

		controller['hiddenNeurons'] = self._addHiddenNeurons(gcparams['hiddenNeuronsParams'])
		controller['governingNeurons'] = self._addHiddenNeurons(gcparams['governingNeuronsParams'], addBias=False)

		synParams = gcparams['synapsesParams']
		controller['synapses'] = {}
		controller['synapses']['sensorToHidden']     = self._wireALayer(self.sensorNeurons,          controller['hiddenNeurons'],    synParams['sensorToHidden'])
		controller['synapses']['trueMotorToHidden']  = self._wireALayer(self.trueMotorNeurons,       controller['hiddenNeurons'],    synParams['trueMotorToHidden'])
		controller['synapses']['hiddenToHidden']     = self._wireALayer(controller['hiddenNeurons'], controller['hiddenNeurons'],    synParams['hiddenToHidden'])
		controller['synapses']['hiddenToGoverning' ] = self._wireALayer(controller['hiddenNeurons'], controller['governingNeurons'], synParams['hiddenToGoverning'] )

		return controller

	def _addParallelSwitch(self):
		# We need to validate the controllers first before we place our gem :)
		numChannels = self.numMotors
		numOptions = self.numBehavioralControllers

		if not numOptions == len(self.behavioralControllers):
			raise ValueError('Declared number of behavioral controllers ({}) is different from the number of controllers supplied ({}). Cannot add parallel switch.'.format(numOptions, len(self.behavioralControllers)))
		for i,bc in enumerate(self.behavioralControllers):
			if not len(bc['motorNeurons']) == numChannels:
				raise ValueError('Number of outputs of {}th behavioral controller ({}) is different from the number of motors ({}). Cannot add parallel switch.'.format(i, len(bc['motorNeurons']),numChannels))

		self.parallelSwitch = {}

		psinputs = []
		for bc in self.behavioralControllers:
			psinputs.append(bc['motorNeurons'])

		if numOptions == 1:
			psoutputs = copy(psinputs[0])
		else:
			psoutputs = self.sim.send_parallel_switch(numChannels, numOptions, psinputs, self.governingController['governingNeurons'])

		pssynapses = []
		for i,out in enumerate(psoutputs):
			pssynapses.append(self.sim.send_synapse(out, self.trueMotorNeurons[i], 1.0))

		self.parallelSwitch['outputs'] = psoutputs
		self.parallelSwitch['synapses'] = pssynapses
