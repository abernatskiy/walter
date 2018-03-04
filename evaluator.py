import pyrosim
import assembler

if __name__ == "__main__":
	seconds = 15.0
	dt = 0.05
	eval_time = int(seconds/dt)
	sim = pyrosim.Simulator(eval_time=eval_time, dt=dt, gravity=0.,
	                        debug=True, play_blind=False, play_paused=False, capture=False, use_textures=True,
	                        xyz=[9,-12,12])
	ass0 = assembler.Assembler(sim, (0,0,3))
	ass0.setController('')

	cyl0 = sim.send_cylinder(x=10., y=0., z=3., r1=1., r2=0., r3=0., length=10, radius=2.5, mass=1000., capped=False)
	ls0 = sim.send_light_source(cyl0)

	sim.create_collision_matrix('all')
	sim.start()
	sim.wait_to_finish()





