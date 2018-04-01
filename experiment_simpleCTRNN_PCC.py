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
numTrials = 20

# Optional definitions for pbsGridWalker that depend on run execution time
cores = 8
pointsPerJob = 1
maxJobs = 180
queue = 'workq'
expectedWallClockTime = '10:00:00'

# Constant hyperparameters
evsDefaults = \
{ 'individual': 'temporalFleetWithoutSwitches', 'evolver': 'cluneSimplified', 'communicator': 'parallelUnixPipe',
'fleetSize': 6, 'numSensorNeurons': 6, 'numMotorNeurons': 6, 'numHiddenNeurons': 12,
'mutModifyNeuron': 0.4, 'mutModifyConnection': 0.4, 'mutAddRemRatio': 1.,
'weightScale': 1.,
'populationSize': 100,
'genStopAfter': 5000,
'initialPopulationType': 'sparse', 'secondObjectiveProbability': 1.0, 'newIndividualsPerGeneration': 1,
'backup': 'yes', 'backupPeriod': 100, 'trackAncestry': 'no',
'logBestIndividual': 'yes', 'logPopulation': 'no',
'printGeneration': 'yes', 'printPopulation': 'no', 'printParetoFront': 'yes',
'logParetoFront': 'yes', 'logParetoFrontKeepAllGenerations': 'yes', 'logParetoFrontPeriod': 10,
'randomSeed': 42}

### Required pbsGridWalker definitions
computationName = 'pcc_simple'

nonRSGrid = gr.Grid1d('secondObjectiveProbability', [0.7, 0.9, 1.0])*gr.Grid1d('newIndividualsPerGeneration', [0,1,4])
parametricGrid = nonRSGrid*numTrials + gr.Grid1dFromFile('randomSeed', cr.randSeedFile, size=len(nonRSGrid)*numTrials)

for par in parametricGrid.paramNames():
	evsDefaults.pop(par)

def prepareEnvironment(experiment):
	ce.prepareEnvironment(experiment)

def runComputationAtPoint(worker, params):
	return ce.runComputationAtPoint(worker, params, evsDefaults, parallelClients=cores)

def processResults(experiment):
	import os
	import shutil
	import numpy as np
	import pbsGridWalker.tools.plotutils as tplt
	tfs.makeDirCarefully('results', maxBackups=100)
	def fitnessFileName(gp):
		return 'NI' + str(gp['newIndividualsPerGeneration']) + '_SO' + str(gp['secondObjectiveProbability']) + '_fitness'
	def columnExtractor(gp):
		outFile = fitnessFileName(gp)
		subprocess.call('cut -d \' \' -f 2 bestIndividual*.log | tail -n +4 | tr \'\n\' \' \' >> ../results/' + outFile, shell=True)
		subprocess.call('echo >> ../results/' + outFile, shell=True)
	experiment.executeAtEveryGridPointDir(columnExtractor)
	os.chdir('results')
	xlabel = 'Generations'
	ylimit = None
	yscale = 'lin'
	xscale = 'lin'
	margins = 0.5
	xlimit = None
	alpha = 0.3
	title = None

	def robustLoadTxt(ffn):
		arr0 = []
		with open(ffn, 'r') as ff:
			for line in ff:
				vals = map(float, line.split())
				arr0.append(vals)
		minlen = min([ len(vs) for vs in arr0 ])
		arr1 = []
		for vs in arr0:
			arr1.append(vs[:minlen])
		arr1 = np.array(arr1)
		return arr1

#	dataDict = { str(mg): np.loadtxt(fitnessFileName(mg)) for mg in [0.1, 0.3, 0.5, 0.7, 0.9] }
#	dataDict = { str(mg): robustLoadTxt(fitnessFileName(mg)) for mg in [0.1, 0.3, 0.5, 0.7, 0.9] }

#	tplt.plotAverageTimeSeries(dataDict, 'Error', 'mg.png',
#	                           title=title, legendLocation=None, xlabel=xlabel,
#	                           xlimit=xlimit, ylimit=ylimit, figsize=(2.5,4), xscale=xscale, yscale=yscale, margins=margins)

	for so in [0.7, 0.9, 1.0]:
		dataDict = { ('SO='+str(so)): robustLoadTxt(fitnessFileName({'secondObjectiveProbability': so, 'newIndividualsPerGeneration': ni})) for ni in [0,1,4] }

		tplt.plotAllTimeSeries(dataDict, 'Fitness', 'tu_SO' + str(so) + '.png',
		                           title=title, legendLocation=1, xlabel=xlabel,
	  	                         xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, alpha=alpha)

#	def plotAllTSForInitalPopulationType(initPopType):
#		title = None
#		dataDict = {attachments[x]: -1.*np.loadtxt(fitnessFileName(x, initPopType)) for x in attachments.keys()}
#		tplt.plotAverageTimeSeries(dataDict, 'Error', 'errorComparison_GENS50_IP' + initPopType + '.png', title=title, legendLocation=None, xlabel=xlabel, xlimit=50, ylimit=ylimit, figsize=(2.5,4), xscale=xscale, yscale=yscale, margins=margins)
#		tplt.plotAllTimeSeries(dataDict, 'Error', 'errorAllTrajectories_GEN50_IP' + initPopType + '.png', title=title, legendLocation=None, xlabel=xlabel, xlimit=50, ylimit=ylimit, figsize=(2.5,4), xscale=xscale, yscale=yscale, margins=margins, alpha=alpha)
#		tplt.plotAverageTimeSeries(dataDict, 'Error', 'errorComparison_IP' + initPopType + '.png', title=title, legendLocation=1, xlabel=xlabel, xlimit=500, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins)
#		tplt.plotAllTimeSeries(dataDict, 'Error', 'errorAllTrajectories_IP' + initPopType + '.png', title=title, legendLocation=1, xlabel=xlabel, xlimit=500, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, alpha=alpha)
#	for ip in initialPopulationTypes:
#		plotAllTSForNew(ip)
	os.chdir('..')
