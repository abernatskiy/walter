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
numTrials = 25

# Optional definitions for pbsGridWalker that depend on run execution time
cores = 8
pointsPerJob = 1
maxJobs = 25
queue = 'shortq'
expectedWallClockTime = '03:00:00'

# Constant hyperparameters
evsDefaults = \
{ 'individual': 'temporalFleetWithoutSwitches', 'evolver': 'temporalUnrollingVer0', 'communicator': 'parallelUnixPipe',
'fleetSize': 6, 'numSensorNeurons': 6, 'numMotorNeurons': 6, 'numHiddenNeurons': 12,
'mutModifyNeuron': 0.4, 'mutModifyConnection': 0.4, 'mutAddRemRatio': 1.,
'weightScale': 1.,
'populationSize': 50,
'genStopAfter': 4000,
'initialPopulationType': 'sparse', 'secondObjectiveProbability': 1.0, 'newIndividualsPerGeneration': 1,
'backup': 'yes', 'backupPeriod': 100, 'trackAncestry': 'no',
'logBestIndividual': 'yes', 'logPopulation': 'no',
'printGeneration': 'yes', 'printPopulation': 'no', 'printParetoFront': 'yes',
'logParetoFront': 'yes', 'logParetoFrontKeepAllGenerations': 'yes', 'logParetoFrontPeriod': 10,
'randomSeed': 42}

### Required pbsGridWalker definitions
computationName = 'temporal_pool_cont'
nonRSGrid = gr.Grid1d('initialPopulationType', ['random', 'sparse'])*gr.Grid1d('newIndividualsPerGeneration', [0,1,5])*gr.Grid1d('evolver', ['temporalUnrolling', 'temporalUnrollingVer0'])
parametricGrid = nonRSGrid*numTrials + gr.Grid1dFromFile('randomSeed', cr.randSeedFile, startAt=300, size=len(nonRSGrid)*numTrials) # + 300

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
#	tfs.makeDirCarefully('results', maxBackups=100)
	def fitnessFileName(gp):
		return 'EV' + str(gp['evolver']) + '_NI' + str(gp['newIndividualsPerGeneration']) + '_IP' + gp['initialPopulationType'] + '_fitness'
	def columnExtractor(gp):
		outFile = fitnessFileName(gp)
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

	ni = 0

	for ip in ['sparse', 'random']:
		dataDict = { 'with SRS' if ev == 'temporalUnrolling' else 'without SRS': robustLoadTxt(fitnessFileName({'initialPopulationType': ip, 'newIndividualsPerGeneration': ni, 'evolver': ev})) for ev in ['temporalUnrolling', 'temporalUnrollingVer0'] }

		tplt.plotAllTimeSeries(dataDict, 'Fitness', 'ev_IP' + ip + '.png',
		                           title=title, legendLocation=4, xlabel=xlabel,
	  	                         xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, alpha=alpha)
		tplt.plotAverageTimeSeries(dataDict, 'Fitness', 'ev_IP' + ip + '_NI' + str(ni) + '_avg.png',
		                           title=title, legendLocation=4, xlabel=xlabel,
	  	                         xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins)

	ni = 5

	for ip in ['sparse', 'random']:
		dataDict = { 'with SRS' if ev == 'temporalUnrolling' else 'without SRS' : robustLoadTxt(fitnessFileName({'initialPopulationType': ip, 'newIndividualsPerGeneration': ni, 'evolver': ev})) for ev in ['temporalUnrolling', 'temporalUnrollingVer0'] }

		tplt.plotAllTimeSeries(dataDict, 'Fitness', 'ev_IP' + ip + '_NI' + str(ni) + '.png',
		                           title=title, legendLocation=4, xlabel=xlabel,
	  	                         xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, alpha=alpha)
		tplt.plotAverageTimeSeries(dataDict, 'Fitness', 'ev_IP' + ip + '_NI' + str(ni) + '_avg.png',
		                           title=title, legendLocation=4, xlabel=xlabel,
	  	                         xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins)

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
