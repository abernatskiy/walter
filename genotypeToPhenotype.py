class GenotypeToPhenotypeMap(object):
	def __init__(self, numSensors, numMotors):
		self.numSensors = numSensors
		self.numMotors = numMotors

	def getPhenotype(self, controllerStr):
		'''Takes the string that desribes the controller and returns a dictionary of neural network params'''
		self.numHiddenNeurons = 2
		# Example return value
		return self.numHiddenNeurons, \
		       {'motorNeuronsParams': {'initialState': [0.,0.,0.,0.], 'tau': [1.,1.,1.,1.], 'alpha': [0.,0.,0.,0.]}, \
		        'hiddenNeuronsParams': {'initialState': [0.]*self.numHiddenNeurons, 'tau': [1.]*self.numHiddenNeurons, 'alpha': [0.]*self.numHiddenNeurons}, \
		        'synapsesParams': {'sensorToHidden': [(0,0,1.), (0,1,1.), (1,0,1.), (1,1,1.), (2,0,1.), (2,1,1.), (3,0,1.), (3,1,1.)], \
		                           'hiddenToHidden': [(0,0,0.1), (0,1,0.1), (1,0,0.1), (1,1,0.1)], \
		                           'hiddenToMotor': [(0,0,1.), (1,0,1.), (0,1,1.), (1,1,1.), (0,2,1.), (1,2,1.), (0,3,1.), (1,3,1.)]}}




