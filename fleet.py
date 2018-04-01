import json
import assembler

class SixFleet(object):
	distance = 2.1
	def __init__(self, sim, pos=[0,0,0], kinds_of_light=[10,20,30]):
		x,y,z = pos
		self.assemblers = []
		for i in range(3):
#			self.assemblers.append(assembler.AssemblerWithSwitch(sim, [x, y+(i-1)*SixFleet.distance, z-SixFleet.distance], kind_of_light=kinds_of_light[i]))
#			self.assemblers.append(assembler.AssemblerWithSwitch(sim, [x, y+(i-1)*SixFleet.distance, z+SixFleet.distance], kind_of_light=kinds_of_light[i]))
			self.assemblers.append(assembler.Assembler(sim, [x, y+(i-1)*SixFleet.distance, z-SixFleet.distance], kind_of_light=kinds_of_light[i]))
			self.assemblers.append(assembler.Assembler(sim, [x, y+(i-1)*SixFleet.distance, z+SixFleet.distance], kind_of_light=kinds_of_light[i]))
			self.assemblers[-2].connectTetherToOther(self.assemblers[-1])

	def setController(self, controllerStr):
		controllers = json.loads(controllerStr)
		for ass, cont in zip(self.assemblers, controllers):
			ass._addController(cont)

	def getSensorData(self):
		sensorData = []
		for ass in self.assemblers:
			sensorData.append(ass.getSensorData())
		return sensorData
