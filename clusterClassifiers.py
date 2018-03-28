_indivClassParams = ['length', 'mutProbability', 'mutInsDelRatio', 'mutExploration',
                     'initLowerLimit', 'initUpperLimit', 'lowerCap', 'upperCap',
                     'initProbabilityOfConnection', 'mutationAmplitude',
                     'fleetSize', 'numSensorNeurons', 'numMotorNeurons', 'initNumBehavioralControllers',
                     'mutGoverning', 'governingMutAddBehavioralController', 'governingMutRemoveBehavioralController',
                     'governingNumHiddenNeurons', 'governingMutModifyNeuron', 'governingMutModifyConnection', 'governingMutAddRemRatio',
                     'behavioralNumHiddenNeurons', 'behavioralMutModifyNeuron', 'behavioralMutModifyConnection', 'behavioralMutAddRemRatio', 'weightScale']
_indivClassParamsRegexp = '(' + '|'.join(_indivClassParams) + ')'
_classSuffixRegexp = 'Class[0-9]+'


# Since EVS has supported composite Individuals, it now requires a regexp classifier
evsClassifier = {'classes': ['individual', 'communicator', 'evolver'],
             'indivParams': [ _indivClassParamsRegexp,
                              _indivClassParamsRegexp + _classSuffixRegexp,
                              '(composite|probabilityOfMutating)' + _classSuffixRegexp ],
              'evolParams': ['populationSize', 'genStopAfter', 'initialPopulationType', 'trackAncestry',
                             'secondObjectiveProbability', 'logPopulation', 'logPopulationPeriod',
                             'logBestIndividual', 'logBestIndividualPeriod', 'printBestIndividual',
                             'printBestIndividualPeriod', 'printParetoFront', 'printParetoFrontPeriod',
                             'printPopulation', 'printPopulationPeriod', 'printGeneration',
                             'printGenerationPeriod', 'backup', 'backupPeriod', 'logParetoFront',
                             'logParetoFrontPeriod', 'logParetoFrontKeepAllGenerations', 'logParetoSize',
                             'randomSeed', 'morphologyControlIndivs']}

evaluatorClassifier = {}

serverClientClassifier = {'server': sum(evsClassifier.values(), []), 'client': sum(evaluatorClassifier.values(), [])}
