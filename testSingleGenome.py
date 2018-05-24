#!/usr/bin/python3.5

import evaluator
evaluator.play_blind = False
evaluator.play_paused = False
evaluator.debug = True
evaluator.capture = False
evaluator.plot_sensor_data = True

from sys import argv
import importlib.util

testGenomesFiles = argv[1:]
genomes = []

for tgf in testGenomesFiles:
	spec = importlib.util.spec_from_file_location('module.name', tgf)
	foo = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(foo)
	genomes.append(foo.testGenome)

scores = [ evaluator.evaluateController(cs, robot_adder=evaluator.addFleet, fitness=evaluator.fleetFitness) for cs in genomes ]

print(scores)
