import json

class gtopSimple(object):
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

class gtopWithSwitch(gtopSimple):
	def getPhenotype(self, controllerStr):
#		return super(gtopWithSwitch, self).getPhenotype(controllerStr)

		# Example return value for a fleet of robots with a switch and independent controllers
		return {'numBehavioralControllers': 2,
		        'behavioralControllers': [ \
						  {'numHiddenNeurons': 2, \
		           'motorNeuronsParams': {'initialState': [-1.,-1.,-1.,-1.,-1.,-1.], 'tau': [1.,1.,1.,1.,1.,1.], 'alpha': [0.,0.,0.,0.,0.,0.]}, \
		           'hiddenNeuronsParams': {'initialState': [0.,0.], 'tau': [1.,1.], 'alpha': [0.,0.]}, \
		           'synapsesParams': {'sensorToHidden': [[0,1,1.], [0,2,1.], [1,1,1.], [1,2,1.], [2,1,1.], [2,2,1.], [3,1,1.], [3,2,1.]], \
		                              'hiddenToHidden': [[1,1,0.1], [1,2,0.1], [2,1,0.1], [2,2,0.1]], \
		                              'hiddenToMotor' : [[0,0,-3.5], [1,0,1.], [2,0,1.], [1,1,1.], [2,1,1.], [1,2,1.], [2,2,1.], [1,3,1.], [2,3,1.]]} \
		          }, \
						  {'numHiddenNeurons': 2, \
		           'motorNeuronsParams': {'initialState': [-1.,-1.,-1.,-1.,-1.,-1.], 'tau': [1.,1.,1.,1.,1.,1.], 'alpha': [0.,0.,0.,0.,0.,0.]}, \
		           'hiddenNeuronsParams': {'initialState': [0.,0.], 'tau': [1.,1.], 'alpha': [0.,0.]}, \
		           'synapsesParams': {'sensorToHidden': [[0,1,-1.], [0,2,-1.], [1,1,-1.], [1,2,-1.], [2,1,-1.], [2,2,-1.], [3,1,-1.], [3,2,-1.]], \
		                              'hiddenToHidden': [[1,1,-0.1], [1,2,-0.1], [2,1,-0.1], [2,2,-0.1]], \
		                              'hiddenToMotor' : [[0,0,3.5], [1,0,-1.], [2,0,-1.], [1,1,-1.], [2,1,-1.], [1,2,-1.], [2,2,-1.], [1,3,-1.], [2,3,-1.]]} \
		          } \
		        ], \
		        'governingController':
		          {'numHiddenNeurons': 2, \
		           'hiddenNeuronsParams': {'initialState': [-1.,-1.], 'tau': [1.,1.], 'alpha': [0.,0.]}, \
		           'governingNeuronsParams': {'initialState': [-1.,-1.], 'tau': [1.,1.], 'alpha': [0.,0.]}, \
		           'synapsesParams': {'sensorToHidden'   : [[0,1,-1.], [0,2,-1.], [1,1,-1.], [1,2,-1.], [2,1,-1.], [2,2,-1.], [3,1,-1.], [3,2,-1.]], \
		                              'trueMotorToHidden'    : [[1,1,-0.1], [1,2,-0.1], [2,1,-0.1], [2,2,-0.1]], \
		                              'hiddenToHidden'   : [[0,1,3.5], [1,1,-1.], [2,1,-1.], [1,2,-1.]], \
		                              'hiddenToGoverning': [[0,0,1.], [1,1,1.]] \
		                              } \
		          }
		       }
