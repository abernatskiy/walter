from abc import ABC, abstractmethod

class Part(ABC):
	def __init__(self, sim, pos, rot):
		self.pos = pos
		self.rot = rot
		self.sim = sim
		self.objects = []
		self.lights = {}

	@abstractmethod
	def getPartTelemetry(self):
		return None

class Cylinder(Part):
	def __init__(self, sim, pos, rot, length=10., radius=2.5, mass=1000., capped=False):
		Part.__init__(self, sim, pos, rot)
		cylinderID    =   sim.send_cylinder(x=pos[0], y=pos[1], z=pos[2],
		                                      r1=rot[0], r2=rot[1], r3=rot[2],
		                                      length=length, radius=radius,
		                                      mass=mass, capped=capped)
		self.objects.append(cylinderID)
		self.lights[cylinderID] = sim.send_light_source(cylinderID)

	def getPartTelemetry(self):
		return None
