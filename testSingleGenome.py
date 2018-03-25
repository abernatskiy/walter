#!/usr/bin/python

import evaluator
evaluator.play_blind = False
evaluator.play_paused = True
evaluator.debug = True

testGenomes = []
testGenomes.append('{"numHiddenNeurons": 2,'
                   '"motorNeuronsParams": {"tau": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],'
                                       '"alpha": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],'
                                '"initialState": [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0]},'
                   '"hiddenNeuronsParams": {"tau": [1.0, 1.0], "alpha": [0.0, 0.0], "initialState": [0.0, 0.0]},'
                   '"synapsesParams": '
                   '{"sensorToHidden": [[0, 1, 1.0], [0, 2, 1.0], [1, 1, 1.0], [1, 2, 1.0], [2, 1, 1.0], [2, 2, 1.0], [3, 1, 1.0], [3, 2, 1.0]],'
                   '"hiddenToMotor": [[0, 0, -2], [1, 0, 1.0], [2, 0, 1.0], [1, 1, 1.0], [2, 1, 1.0], [1, 2, 1.0], [2, 2, 1.0], [1, 3, 1.0], [2, 3, 1.0]],'
                   '"hiddenToHidden": [[1, 1, 0.1], [1, 2, 0.1], [2, 1, 0.1], [2, 2, 0.1]]}}') # codename genome 42

scores = [ evaluator.evaluateController(evaluator.initial_conditions, cs) for cs in testGenomes ]

print(scores)
