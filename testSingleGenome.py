#!/usr/bin/python

import evaluator
evaluator.play_blind = False
evaluator.play_paused = True
evaluator.debug = True

testGenomes = {}
testGenomes['42'] = (
                    '{"numHiddenNeurons": 2,'
                    '"motorNeuronsParams": {"tau": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],'
                                         '"alpha": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],'
                                  '"initialState": [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0]},'
                    '"hiddenNeuronsParams": {"tau": [1.0, 1.0], "alpha": [0.0, 0.0], "initialState": [0.0, 0.0]},'
                    '"synapsesParams": '
                    '{"sensorToHidden": [[0, 1, 1.0], [0, 2, 1.0], [1, 1, 1.0], [1, 2, 1.0], [2, 1, 1.0], [2, 2, 1.0], [3, 1, 1.0], [3, 2, 1.0]],'
                    '"hiddenToMotor": [[0, 0, -2], [1, 0, 1.0], [2, 0, 1.0], [1, 1, 1.0], [2, 1, 1.0], [1, 2, 1.0], [2, 2, 1.0], [1, 3, 1.0], [2, 3, 1.0]],'
                    '"hiddenToHidden": [[1, 1, 0.1], [1, 2, 0.1], [2, 1, 0.1], [2, 2, 0.1]]}}'
)

testGenomes['420'] = (
                      '{"behavioralControllers": ['
#                         '{"motorNeuronsParams": {"tau": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], "initialState": [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0], "alpha": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},'
                          '{"motorNeuronsParams": {"tau": [1.0, 1.0, 1.0, 1.0, 1.0], "initialState": [-1.0, -1.0, -1.0, -1.0, -1.0], "alpha": [0.0, 0.0, 0.0, 0.0, 0.0]},'
                          '"hiddenNeuronsParams": {"tau": [1.0, 1.0], "initialState": [0.0, 0.0], "alpha": [0.0, 0.0]},'
                          '"numHiddenNeurons": 2,'
                          '"synapsesParams": {"hiddenToMotor": [[0, 0, -3.5], [1, 0, 1.0], [2, 0, 1.0], [1, 1, 1.0], [2, 1, 1.0], [1, 2, 1.0], [2, 2, 1.0], [1, 3, 1.0], [2, 3, 1.0]],'
                                           '"hiddenToHidden": [[1, 1, 0.1], [1, 2, 0.1], [2, 1, 0.1], [2, 2, 0.1]],'
                                           '"sensorToHidden": [[0, 1, 1.0], [0, 2, 1.0], [1, 1, 1.0], [1, 2, 1.0], [2, 1, 1.0], [2, 2, 1.0], [3, 1, 1.0], [3, 2, 1.0]]}},'
#                          '{"motorNeuronsParams": {"tau": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], "initialState": [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0], "alpha": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},'
                          '{"motorNeuronsParams": {"tau": [1.0, 1.0, 1.0, 1.0, 1.0], "initialState": [-1.0, -1.0, -1.0, -1.0, -1.0], "alpha": [0.0, 0.0, 0.0, 0.0, 0.0]},'
                          '"hiddenNeuronsParams": {"tau": [1.0, 1.0], "initialState": [0.0, 0.0], "alpha": [0.0, 0.0]},'
                          '"numHiddenNeurons": 2,'
                          '"synapsesParams": {"hiddenToMotor": [[0, 0, 3.5], [1, 0, -1.0], [2, 0, -1.0], [1, 1, -1.0], [2, 1, -1.0], [1, 2, -1.0], [2, 2, -1.0], [1, 3, -1.0], [2, 3, -1.0]],'
                          '"hiddenToHidden": [[1, 1, -0.1], [1, 2, -0.1], [2, 1, -0.1], [2, 2, -0.1]],'
                          '"sensorToHidden": [[0, 1, -1.0], [0, 2, -1.0], [1, 1, -1.0], [1, 2, -1.0], [2, 1, -1.0], [2, 2, -1.0], [3, 1, -1.0], [3, 2, -1.0]]}}'
                      '],'
                      '"numBehavioralControllers": 2,'
                      '"governingController": {'
                        '"governingNeuronsParams": {"tau": [1.0, 1.0], "initialState": [-1.0, -1.0], "alpha": [0.0, 0.0]},'
                        '"hiddenNeuronsParams": {"tau": [1.0, 1.0], "initialState": [-1.0, -1.0], "alpha": [0.0, 0.0]},'
                        '"numHiddenNeurons": 2,'
                        '"synapsesParams": {"hiddenToHidden": [[0, 1, 3.5], [1, 1, -1.0], [2, 1, -1.0], [1, 2, -1.0]],'
                                        '"trueMotorToHidden": [[1, 1, -0.1], [1, 2, -0.1], [2, 1, -0.1], [2, 2, -0.1]],'
                                        '"hiddenToGoverning": [[0, 0, 1.0], [1, 1, 1.0]],'
                                           '"sensorToHidden": [[0, 1, -1.0], [0, 2, -1.0], [1, 1, -1.0], [1, 2, -1.0], [2, 1, -1.0], [2, 2, -1.0], [3, 1, -1.0], [3, 2, -1.0]]}'
                      '}}'

)
#	                   '"motorNeuronsParams": {"initialState": [-1.,-1.,-1.,-1.,-1.,-1.], "tau": [1.,1.,1.,1.,1.,1.], "alpha": [0.,0.,0.,0.,0.,0.]},'
#		                 '"motorNeuronsParams": {"initialState": [-1.,-1.,-1.,-1.,-1.,-1.], "tau": [1.,1.,1.,1.,1.,1.], "alpha": [0.,0.,0.,0.,0.,0.]},'

import assembler

scores = [ evaluator.evaluateController(evaluator.initial_conditions, cs, assemblerType=assembler.AssemblerWithSwitch) for cs in [testGenomes['420']] ]

print(scores)
