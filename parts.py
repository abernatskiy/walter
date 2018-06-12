from abc import ABC, abstractmethod
import math

class Part(ABC):
	def __init__(self, sim):
		self.sim = sim
		self.objects = []
		self.lights = []
		self.lightSensors = []

	@abstractmethod
	def getPartTelemetry(self):
		return None

class Cylinder(Part):
	susceptible_to_adhesion_type = 10
	def __init__(self, sim, pos, rot, chirality, length=10., radius=2.5, mass=1000., capped=False, kinds_of_light=[10,20,30]):
		'''Chirality can be 1 and -1'''
		Part.__init__(self, sim)
		cylinderID    =   self.sim.send_cylinder(x=pos[0], y=pos[1], z=pos[2],
		                                    r1=rot[0], r2=rot[1], r3=rot[2],
		                                    length=length, radius=radius,
		                                    mass=mass, capped=capped)
		self.objects.append(cylinderID)
		self.sim.send_adhesion_susceptibility(self.objects[-1], Cylinder.susceptible_to_adhesion_type)

		for lid in range(3):
			x = radius*math.cos(chirality*2.*math.pi*lid/3)
			y = radius*math.sin(chirality*2.*math.pi*lid/3)
			light, sens = sim.send_light_source(cylinderID, x=x, y=y, z=length/2, kind_of_light=kinds_of_light[lid], send_position_sensor=True)
			self.lights.append(light)
			self.lightSensors.append(sens)

	def getPartTelemetry(self):
		sensorData = []
		for sen in self.lightSensors:
			sensorData.append([ self.sim.get_sensor_data(sen, svi=svi) for svi in range(3) ])
		return sensorData
