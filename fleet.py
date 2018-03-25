import json
import assembler

class SixFleet(object):
	def __init__(self, sim, pos=[0,0,0], kinds_of_light=[10,20,30]):
		x,y,z = pos
		self.assemblers = []
		for i in range(3):
			assemblers.append(assembler.AssemblerWithSwitch(sim, [x+0, y+i-1, z-1], kind_of_light=kinds_of_light[i]))
			assemblers.append(assembler.AssemblerWithSwitch(sim, [x+0, y+i-1, z+1], kind_of_light=kinds_of_light[i]))
			assemblers[-2].connectTetherToOther(assemblers[-1])

	def setController(self, controllerStr):
		controllers = json.loads(controllerStr)
		for ass, cont in zip(assemblers, controllers):
			ass.setController(cont)