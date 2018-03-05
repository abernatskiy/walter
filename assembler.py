from genotypeToPhenotype import GenotypeToPhenotypeMap

class Assembler(object):
	body_radius = 0.5
	body_mass = 1.0
	body_color = (0.,1.,0.)
	proximity_range = 2.0
	proximity_offset = (0.,0.,0.)
	max_thrust = 1.0
	thrust_threshold = -0.8
	max_torque = 0.1

	proximity_channels = [0,1,2] # colors (3,4,5) are not used for now

	def __init__(self, sim, initpos):
		'''Creates an assembler robot at the geometrical position initpos'''
		x,y,z = initpos
		bcr,bcg,bcb = Assembler.body_color

		self.sim = sim
		self.body = sim.send_sphere(x=x, y=y, z=z,
		                            radius=Assembler.body_radius,
		                            mass=Assembler.body_mass,
		                            r=bcr, g=bcg, b=bcb)

		self.proximitySensor = sim.send_proximity_sensor(body_id=self.body,
		                                                  x=0, y=0, z=0,
		                                                  max_distance=Assembler.proximity_range) # FIXME: add a realistic offset eventually
		self.lightSensor = sim.send_light_sensor(self.body) # FIXME: add a realistic offset eventually
		self.numSensors = 4 # three channels of proximity, one channel of light

		self.thruster = sim.send_thruster(self.body,
		                                  x=x, y=y, z=z-Assembler.body_radius,
		                                  lo=0., hi=-1.*Assembler.max_thrust, threshold=Assembler.thrust_threshold)
		self.rcw = sim.send_reaction_control_wheel(self.body,
		                                           max_torque=Assembler.max_torque)
		self.numMotors = 4 # thruster + three DoF of the reaction control wheel

		self.gtop = GenotypeToPhenotypeMap(self.numSensors, self.numMotors)

	def setController(self, controllerStr):
		annParams = self.gtop.getPhenotype(controllerStr)

		self.numHiddenNeurons = annParams['numHiddenNeurons']

		self._addSensorNeurons()
		self._addHiddenNeurons(annParams['hiddenNeuronsParams'])
		self._addMotorNeurons(annParams['motorNeuronsParams'])
		self._addSynapses(annParams['synapsesParams'])

	def _addSensorNeurons(self):
		'''Adds sensor neurons to all sensors'''
		self.sensorNeurons = []

		self.sensorNeurons.append(self.sim.send_sensor_neuron(sensor_id=self.lightSensor))
		for pc in Assembler.proximity_channels:
			self.sensorNeurons.append(self.sim.send_sensor_neuron(sensor_id=self.proximitySensor, svi=pc))

	def _addHiddenNeurons(self, hnParams):
		'''Adds hidden neurons'''
		# hnInitialStates = hnParams['initialState'] # ignored for now, no support in pyrosim
		hnTaus = hnParams['tau']
		hnAlphas = hnParams['alpha']

		self.hiddenNeurons = []

		self.hiddenNeurons.append(self.sim.send_bias_neuron())
		for i in range(self.numHiddenNeurons):
			self.hiddenNeurons.append(self.sim.send_hidden_neuron(tau=hnTaus[i],
		  	                                                    alpha=hnAlphas[i]))
			#                                                  start_value=hnInitialStates[i+1]

	def _addMotorNeurons(self, mnParams):
		'''Adds motor neurons to all motors'''
		mnInitialStates = mnParams['initialState']
		mnTaus = mnParams['tau']
		mnAlphas = mnParams['alpha']

		self.motorNeurons = []

		self.motorNeurons.append(self.sim.send_motor_neuron(joint_id=self.thruster,
		                                                    start_value=mnInitialStates[0],
		                                                    tau=mnTaus[0],
		                                                    alpha=mnAlphas[0]))
		for i in range(3):
			self.motorNeurons.append(self.sim.send_motor_neuron(joint_id=self.rcw,
			                                                    start_value=mnInitialStates[i+1],
			                                                    tau=mnTaus[i+1],
		  	                                                  alpha=mnAlphas[i+1],
			                                                    input_index=i))

	def _addSynapses(self, synParams):
		self.synapses = {}
		self.synapses['sensorToHidden'] = [ self.sim.send_synapse(self.sensorNeurons[i],self.hiddenNeurons[j],w) for i,j,w in synParams['sensorToHidden'] ]
		self.synapses['hiddenToHidden'] = [ self.sim.send_synapse(self.hiddenNeurons[i],self.hiddenNeurons[j],w) for i,j,w in synParams['hiddenToHidden'] ]
		self.synapses['hiddenToMotor'] = [ self.sim.send_synapse(self.hiddenNeurons[i],self.motorNeurons[j],w) for i,j,w in synParams['hiddenToMotor'] ]





