from os.path import join, expanduser
from time import sleep
import subprocess
import sys
sys.path.append(join(expanduser('~'), 'walter'))

import pbsGridWalker.grid as gr
import pbsGridWalker.tools.algorithms as tal
import pbsGridWalker.tools.fsutils as tfs

import clusterRoutes as cr
import clusterClassifiers as cl
import clusterExperiment as ce

# Tunable hyperparameters
numTrials = 10

# Optional definitions for pbsGridWalker that depend on run execution time
cores = 8
pointsPerJob = 1
maxJobs = 50
queue = 'workq'
expectedWallClockTime = '10:00:00'

# Constant hyperparameters
evsDefaults = \
{ 'individual': 'ctrnnWithSwitchFleetOfIdenticals', 'evolver': 'cluneSimplified', 'communicator': 'parallelUnixPipe',
'fleetSize': 6, 'numSensorNeurons': 6, 'numMotorNeurons': 6, 'initNumBehavioralControllers': 1,
'mutGoverning': 0.2,
'governingMutAddBehavioralController': 0.1, 'governingMutRemoveBehavioralController': 0.1,
'governingNumHiddenNeurons': 12, 'governingMutModifyNeuron': 0.3, 'governingMutModifyConnection': 0.4, 'governingMutAddRemRatio': 1.,
'behavioralNumHiddenNeurons': 6, 'behavioralMutModifyNeuron': 0.3, 'behavioralMutModifyConnection': 0.4, 'behavioralMutAddRemRatio': 1.,
'weightScale': 1.,
'populationSize': 100,
'genStopAfter': 5000,
'initialPopulationType': 'sparse', 'secondObjectiveProbability': 1.0, 'newIndividualsPerGeneration': 0,
'backup': 'yes', 'backupPeriod': 100, 'trackAncestry': 'no',
'logBestIndividual': 'yes', 'logPopulation': 'no',
'printGeneration': 'yes', 'printPopulation': 'no', 'printParetoFront': 'yes',
'logParetoFront': 'yes', 'logParetoFrontKeepAllGenerations': 'yes', 'logParetoFrontPeriod': 10,
'randomSeed': 42}

### Required pbsGridWalker definitions
computationName = 'pcc_with_numNewIndiv_and_secondObjProb'

nonRSGrid = gr.Grid1d('secondObjectiveProbability', [0.7, 0.9, 1.0])*gr.Grid1d('newIndividualsPerGeneration', [0,1,4,16])
parametricGrid = nonRSGrid*numTrials + gr.Grid1dFromFile('randomSeed', cr.randSeedFile, size=len(nonRSGrid)*numTrials)

for par in parametricGrid.paramNames():
	evsDefaults.pop(par)

def prepareEnvironment(experiment):
	ce.prepareEnvironment(experiment)

def runComputationAtPoint(worker, params):
	return ce.runComputationAtPoint(worker, params, evsDefaults, parallelClients=cores)

def processResults(experiment):
	with open('resultsProcessed.txt', 'w') as rpf:
		rpf.write('Result processing has been called!')
