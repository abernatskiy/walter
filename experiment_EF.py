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
cores = 12
pointsPerJob = 1
maxJobs = 100
queue = 'workq'
expectedWallClockTime = '30:00:00'

# Constant hyperparameters
evsDefaults = \
{ 'individual': 'ctrnnDiscreteWeightsFleetOfIdenticalsEvolvableFitness', 'evolver': 'evolvableFitnessFunction', 'communicator': 'parallelUnixPipe',
'fleetSize': 6, 'numSensorNeurons': 10, 'numMotorNeurons': 6, 'initNumBehavioralControllers': 1,
'numHiddenNeurons': 6, 'mutModifyNeuron': 0.3, 'mutModifyConnection': 0.4, 'mutAddRemRatio': 1.,
'weightScale': 1.,
'populationSize': 500,
'genStopAfter': 3000,
'numFitnessParams': 5,
'fitnessParamsUpdatePeriod': 50,
'fitnessGroupsNumber': 10,
'initialPopulationType': 'random',
'backup': 'yes', 'backupPeriod': 100, 'trackAncestry': 'yes',
'logBestIndividual': 'yes', 'logPopulation': 'yes', 'logPopulationPeriod': 100,
'printGeneration': 'yes', 'printPopulation': 'no', 'printParetoFront': 'yes',
'logParetoFront': 'yes', 'logParetoFrontKeepAllGenerations': 'yes', 'logParetoFrontPeriod': 10,
'randomSeed': 42}

### Required pbsGridWalker definitions
computationName = 'evolvableFitness'

nonRSGrid = gr.Grid1d('fitnessParamsUpdatePeriod', [25,50,100])*gr.Grid1d('evolver', ['evolvableFitnessFunction', 'evolvableFitnessFunctionSparsityBiased'])
parametricGrid = nonRSGrid*numTrials + gr.Grid1dFromFile('randomSeed', cr.randSeedFile, size=len(nonRSGrid)*numTrials)

for par in parametricGrid.paramNames():
	evsDefaults.pop(par)

def prepareEnvironment(experiment):
	ce.prepareEnvironment(experiment)

def runComputationAtPoint(worker, params):
	return ce.runComputationAtPoint(worker, params, evsDefaults, parallelClients=cores)

def processResults(experiment):
	return
	import os
	import shutil
	import numpy as np
	import pbsGridWalker.tools.plotutils as tplt
#	tfs.makeDirCarefully('results', maxBackups=100)
	def fitnessFileName(mutGoverning, newIndivs=1):
		return 'NI' + str(newIndivs) + '_MG' + str(mutGoverning) + '_fitness'
	def columnExtractor(gp):
		outFile = fitnessFileName(gp['mutGoverning'])
		subprocess.call('cut -d \' \' -f 2 bestIndividual*.log | tail -n +4 | tr \'\n\' \' \' >> ../results/' + outFile, shell=True)
		subprocess.call('echo >> ../results/' + outFile, shell=True)
#	experiment.executeAtEveryGridPointDir(columnExtractor)
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

	for mgg in [0.1, 0.3, 0.5, 0.7, 0.9]:
		dataDict = { str(mg): robustLoadTxt(fitnessFileName(mg)) for mg in [mgg] }

		tplt.plotAllTimeSeries(dataDict, 'Error', 'mgall' + str(mgg) + '.png',
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
