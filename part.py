class Part(object):
	def __init__(self, sim, pos, rot):
		x,y,z = pos
		r1,r2,r3 = rot
		self.sim = sim
		self.objects = []
		self.lights = {}
		cylinderID    =   sim.send_cylinder(x=x, y=y, z=z,
		                                      r1=r1, r2=r2, r3=r3,
		                                      length=10, radius=2.5, mass=1000., capped=False)
		self.objects.append(cylinderID)
		self.lights[cylinderID] = sim.send_light_source(cylinderID)

	def getPartTelemetry(self):
		return None
