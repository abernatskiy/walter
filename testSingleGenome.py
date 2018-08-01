#!/usr/bin/python3.5

import evaluator
evaluator.play_blind = False
evaluator.play_paused = False
evaluator.debug = True
evaluator.capture = False
evaluator.plot_sensor_data = True
evaluator.evolvable_fitness_coefficients = True
# evaluator.use_switching_controllers = True

from sys import argv
import importlib.util

testGenomesFiles = argv[1:]
genomes = []

for tgf in testGenomesFiles:
	try:
		spec = importlib.util.spec_from_file_location('module.name', tgf)
		foo = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(foo)
		genomes.append(foo.testGenome)
	except:
		with open(tgf, 'r') as tgff:
			for line in tgff:
				genomes.append(line.split(maxsplit=3)[3].rstrip())
				print(genomes)

scores = [ evaluator.evaluateController(cs, robot_adder=evaluator.addFleet, fitness=evaluator.fleetFitness, showFitnessComponents=True) for cs in genomes ]

print(scores)
