import json

class GenotypeToPhenotypeMap(object):
	def __init__(self, numSensors, numMotors):
		self.numSensors = numSensors
		self.numMotors = numMotors

	def _validateANNParams(self, params):
		pass

	def getPhenotype(self, controllerStr):
		'''Takes the string that desribes the controller and returns a dictionary of neural network params'''
		annParams = json.loads(controllerStr)
		self._validateANNParams(annParams)
		return annParams

		# Example return value of getPhenotype()
#		return {'numHiddenNeurons': 2,
#		        'motorNeuronsParams': {'initialState': [-1.,-1.,-1.,-1.], 'tau': [1.,1.,1.,1.], 'alpha': [0.,0.,0.,0.]}, \
#		        'hiddenNeuronsParams': {'initialState': [0.]*self.numHiddenNeurons, 'tau': [1.]*self.numHiddenNeurons, 'alpha': [0.]*self.numHiddenNeurons}, \
#		        'synapsesParams': {'sensorToHidden': [[0,1,1.], [0,2,1.], [1,1,1.], [1,2,1.], [2,1,1.], [2,2,1.], [3,1,1.], [3,2,1.]], \
#		                           'hiddenToHidden': [[1,1,0.1], [1,2,0.1], [2,1,0.1], [2,2,0.1]], \
#		                           'hiddenToMotor': [[0,0,-3.5], [1,0,1.], [2,0,1.], [1,1,1.], [2,1,1.], [1,2,1.], [2,2,1.], [1,3,1.], [2,3,1.]]}}



