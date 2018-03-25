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

class gtopWithSwitch(gtopSimple):
	def getPhenotype(self, controllerStr):
		return super(gtopWithSwitch, self).getPhenotype(controllerStr)
