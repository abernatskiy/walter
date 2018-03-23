import genotypeToPhenotype as g2p

class Assembler(object):
	body_radius = 0.5
	body_mass = 1.0
	body_color = (0.,1.,0.)
	proximity_range = 2.0
	proximity_offset = (0.,0.,0.)
	max_thrust = 1.0
	thrust_threshold = -0.8
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

	def __init__(self, sim, initpos):
		'''Creates an assembler robot at the geometrical position initpos'''
		x,y,z = initpos
		bcr,bcg,bcb = Assembler.body_color

		self.sim = sim

		# Robot's body
		self.body = sim.send_sphere(x=x, y=y, z=z,
		                            radius=Assembler.body_radius,
		                            mass=Assembler.body_mass,
		                            r=bcr, g=bcg, b=bcb)

		# Motors
		self.motors = []

		thruster = sim.send_thruster(self.body,
		                             x=x, y=y, z=z-Assembler.body_radius,
		                             lo=0., hi=-1.*Assembler.max_thrust, threshold=Assembler.thrust_threshold)
		self.motors.append((thruster, 0))

		rcw = sim.send_reaction_control_wheel(self.body,
		                                      max_torque=Assembler.max_torque)
		for input_index in [0,1,2]:
			self.motors.append((rcw, input_index))

		sticky = sim.send_adhesive_joint(self.body, adhesion_kind=Assembler.adhesion_kind)
		self.motors.append((sticky, 0))

		self.numMotors = Assembler.default_num_motors
		self.motorLabels = Assembler.default_motor_labels

		# Sensors
		self.sensors = []

		proximitySensor = sim.send_proximity_sensor(body_id=self.body,
		                                            x=0, y=0, z=0,
		                                            max_distance=Assembler.proximity_range) # FIXME: add a realistic offset eventually
		for svi in Assembler.proximity_channels:
			self.sensors.append((proximitySensor, svi))

		lightSensor = sim.send_light_sensor(self.body) # FIXME: add a realistic offset eventually
		self.sensors.append((lightSensor, 0))

		stickinessSensor = sim.send_proprioceptive_sensor(joint_id=sticky)
		self.sensors.append((stickinessSensor, 0))

		self.numSensors = Assembler.default_num_sensors
		self.sensorLabels = Assembler.default_sensor_labels

		self._addGToPMap()

	def _addGToPMap(self):
		self.gtop = g2p.GenotypeToPhenotypeMap(self.numSensors, self.numMotors)

	def connectTetherToOther(self, other):
		assert self.sim.id == other.sim.id, 'Robots must be in the same simulator to connect them with tethers'
		tether = sim.send_tether(self.body, other.body, force_coefficient=Assembler.tether_force_coefficient, dampening_coefficient=Assembler.tether_dampening_coefficient)
		tether_proprioception = sim.send_proprioceptive_sensor(joint_id=tether)
		self._addTether(tether, tether_proprioception, 0)
		other._addTether(tether, tether_proprioception, 1)

	def _addTether(self, tether_id, proprioceptive_sensor_id, index):
		self.motors.append = (tether_id, index)
		self.motorLabels.append('tether')
		self.numMotors += 1
		self.sensors.append = (proprioceptive_sensor_id, index)
		self.sensorLabels.append('tetherTension')
		self.numSensors += 1

		self._addGToPMap()

	def setController(self, controllerStr):
		annParams = self.gtop.getPhenotype(controllerStr)

		self.numHiddenNeurons = annParams['numHiddenNeurons']

		self._addSensorNeurons()
		self._addHiddenNeurons(annParams['hiddenNeuronParams'])
		self._addMotorNeurons(annParams['motorNeuronParams'])
		self._addSynapses(annParams['synapsesParams'])

	def _addSensorNeurons(self):
		'''Adds sensor neurons to all sensors'''
		self.sensorNeurons = []
		for sen, svi in self.sensors:
			self.sensorNeurons.append(self.sim.send_sensor_neuron(sensor_id=sen, svi=svi))

	def _addHiddenNeurons(self, hnParams):
		'''Adds hidden neurons'''
		hnInitialStates = hnParams['initialState']
		hnTaus = hnParams['tau']
		hnAlphas = hnParams['alpha']

		self.hiddenNeurons = []

		self.hiddenNeurons.append(self.sim.send_bias_neuron())
		for i in range(self.numHiddenNeurons):
			self.hiddenNeurons.append(self.sim.send_hidden_neuron(tau=hnTaus[i],
				                                                    alpha=hnAlphas[i],
			                                                      start_value=hnInitialStates[i]))

	def _addMotorNeurons(self, mnParams):
		'''Adds motor neurons to all motors'''
		mnInitialStates = mnParams['initialState']
		mnTaus = mnParams['tau']
		mnAlphas = mnParams['alpha']

		self.motorNeurons = []
		for i in range(self.numMotors):
			mot, mii = self.motors[i]
			self.motorNeurons.append(self.sim.send_motor_neuron(joint_id=mot,
	                                                        start_value=mnInitialStates[i],
	                                                        tau=mnTaus[i],
	                                                        alpha=mnAlphas[i],
			                                                    input_index=mii))

	def _addSynapses(self, synParams):
		self.synapses = {}
		self.synapses['sensorToHidden'] = [ self.sim.send_synapse(self.sensorNeurons[i],self.hiddenNeurons[j],w) for i,j,w in synParams['sensorToHidden'] ]
		self.synapses['hiddenToHidden'] = [ self.sim.send_synapse(self.hiddenNeurons[i],self.hiddenNeurons[j],w) for i,j,w in synParams['hiddenToHidden'] ]
		self.synapses['hiddenToMotor'] = [ self.sim.send_synapse(self.hiddenNeurons[i],self.motorNeurons[j],w) for i,j,w in synParams['hiddenToMotor'] ]

	def getSensorData(self):
		sensorData = []
		for sen, svi in self.sensors:
			sensorData.append(self.sim.get_sensor_data(sen, svi=svi))
		return sensorData
