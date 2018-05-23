import json
import assembler

class SixFleet(object):
	distance = 2.1
	def __init__(self, sim, pos=[0,0,0], kinds_of_light=[10,20,30], use_rcw_gauges=False, use_fuel_gauge=False, use_switching_controllers=False):
		x,y,z = pos
		self.assemblers = []
		for i in range(3):
			if use_switching_controllers:
				robofun = assembler.AssemblerWithSwitch
			else:
				robofun = assembler.Assembler
			pos0 = [x, y+(i-1)*SixFleet.distance, z-SixFleet.distance]
			pos1 = [x, y+(i-1)*SixFleet.distance, z+SixFleet.distance]
			self.assemblers.append(robofun(sim, pos0, kind_of_light=kinds_of_light[i], use_rcw_gauges=use_rcw_gauges, use_fuel_gauge=use_fuel_gauge))
			self.assemblers.append(robofun(sim, pos1, kind_of_light=kinds_of_light[i], use_rcw_gauges=use_rcw_gauges, use_fuel_gauge=use_fuel_gauge))
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
