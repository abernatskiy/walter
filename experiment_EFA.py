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
numTrials = 100

# Optional definitions for pbsGridWalker that depend on run execution time
cores = 12
pointsPerJob = 1
maxJobs = 800
queue = 'workq'
expectedWallClockTime = '15:00:00'

# Constant hyperparameters
evsDefaults = \
{ 'individual': 'ctrnnDiscreteWeightsFleetOfIdenticalsEvolvableFitness', 'evolver': 'ageFunction', 'communicator': 'parallelUnixPipe',
'fleetSize': 6, 'numSensorNeurons': 10, 'numMotorNeurons': 6, 'initNumBehavioralControllers': 1,
'numHiddenNeurons': 6, 'mutModifyNeuron': 0.3, 'mutModifyConnection': 0.4, 'mutAddRemRatio': 1.,
'weightScale': 1.,
'populationSize': 100,
'lineageInjectionPeriod': 50, 'mutatedLineagesFraction': 0.,
'genStopAfter': 3000,
'numFitnessParams': 5,
'initialPopulationType': 'random',
'backup': 'yes', 'backupPeriod': 100, 'trackAncestry': 'yes',
'logBestIndividual': 'yes', 'logPopulation': 'yes', 'logPopulationPeriod': 100,
'printGeneration': 'yes', 'printPopulation': 'no', 'printParetoFront': 'yes',
'logParetoFront': 'yes', 'logParetoFrontKeepAllGenerations': 'yes', 'logParetoFrontPeriod': 10,
'randomSeed': 42}

### Required pbsGridWalker definitions
computationName = 'ageFitness'

nonRSGrid = (
             (
              gr.Grid1d('lineageInjectionPeriod', [30000])*
              gr.Grid1d('mutatedLineagesFraction', [0.])*
              gr.Grid1d('initialPopulationType', ['random'])*
              gr.Grid1d('evolver', ['ageFunction'])*
              gr.Grid1d('individual', ['ctrnnDiscreteWeightsFleetOfIdenticalsFixedFitness', 'ctrnnDiscreteWeightsFleetOfIdenticalsEvolvableFitness'])
             ).concatenate(

              gr.Grid1d('individual', ['ctrnnDiscreteWeightsFleetOfIdenticalsEvolvableFitness'])*
              gr.Grid1d('lineageInjectionPeriod', [50])*
              (
               gr.Grid1d('mutatedLineagesFraction', [0.5])*
               gr.Grid1d('initialPopulationType', ['random'])*
               gr.Grid1d('evolver', ['ageFunction'])).concatenate(

               gr.Grid1d('mutatedLineagesFraction', [0.])*
               gr.Grid1d('initialPopulationType', ['sparse', 'random'])*
               gr.Grid1d('evolver', ['ageFunction', 'ageFunctionSparsityBiased'])
              )

             )
            )

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

#	tfs.makeDirCarefully('results', maxBackups=100)

	def fitnessFileName(paramsDict):
		gid = 'NOGID'
		if paramsDict['lineageInjectionPeriod'] == 30000:
			if paramsDict['individual'] == 'ctrnnDiscreteWeightsFleetOfIdenticalsFixedFitness':
				gid = '1'
			elif paramsDict['individual'] == 'ctrnnDiscreteWeightsFleetOfIdenticalsEvolvableFitness':
				gid = '2'
		elif paramsDict['lineageInjectionPeriod'] == 50:
			if paramsDict['mutatedLineagesFraction'] == 0.:
				if paramsDict['evolver'] == 'ageFunction':
					if paramsDict['initialPopulationType'] == 'random':
						gid = '3'
					elif paramsDict['initialPopulationType'] == 'sparse':
						gid = '6'
				elif paramsDict['evolver'] == 'ageFunctionSparsityBiased':
					if paramsDict['initialPopulationType'] == 'random':
						gid = '4'
					elif paramsDict['initialPopulationType'] == 'sparse':
						gid = '5'
			elif paramsDict['mutatedLineagesFraction'] == 0.5:
				gid = '7'
		if gid == 'NOGID':
			raise ValueError('Unclassified parameter dictionary {}'.format(paramsDict))
		return 'gid{}'.format(gid)

	def columnExtractor(gp):
		print('Extracting fitness times series to {}...'.format(fitnessFileName(gp)))
		outFile = fitnessFileName(gp)
		subprocess.call('cut -d \' \' -f 2 bestIndividual*.log | tail -n +4 | tr \'\n\' \' \' >> ../results/' + outFile, shell=True)
		subprocess.call('echo >> ../results/' + outFile, shell=True)

#	experiment.executeAtEveryGridPointDir(columnExtractor)


	def plotAll():
		os.chdir('results')
		xlabel = 'Generations'
		ylimit = None
		yscale = 'lin'
		xscale = 'lin'
		margins = 0.5
		xlimit = 3000
		alpha = 0.3
		title = None
#		figsize = (2.5,4)
		figsize = None
		striptype = 'conf95'

		filenames = [ 'gid{}'.format(x) for x in range(1,8) ]
		dataDict = { fn: np.loadtxt(fn) for fn in filenames }

		comp1 = { tsn: dataDict[fn] for tsn,fn in {'manual scaffolding': 'gid1', 'random scaffolding': 'gid2', 'evolvable scaffolding': 'gid3'}.items() }
		comp2 = { tsn: dataDict[fn] for tsn,fn in {'no bias (RIP)': 'gid3', 'RIP+CC': 'gid4', 'SIP+CC': 'gid5', 'SIP only': 'gid6'}.items() }
		comp3 = { tsn: dataDict[fn] for tsn,fn in {'no scaffolding mutation': 'gid3', 'mutatable scaffolding': 'gid7'}.items() }

		comparisons = { 'comp1': comp1, 'comp2': comp2, 'comp3': comp3 }

		for e,d in comparisons.items():
			tplt.plotAverageTimeSeries(d, 'Fitness', e + '-avg.png',
			                           title=title, legendLocation=4, xlabel=xlabel,
			                           xlimit=xlimit, ylimit=ylimit, figsize=figsize, xscale=xscale, yscale=yscale, margins=margins, strips=striptype)
			tplt.plotAllTimeSeries(d, 'Fitness', e + '-all.png', alpha=alpha,
			                       title=title, legendLocation=4, xlabel=xlabel,
			                       xlimit=xlimit, ylimit=ylimit, figsize=figsize, xscale=xscale, yscale=yscale, margins=margins)

		os.chdir('..')

	plotAll()

#	def robustLoadTxt(ffn):
#		arr0 = []
#		with open(ffn, 'r') as ff:
#			for line in ff:
#				vals = map(float, line.split())
#				arr0.append(vals)
#		minlen = min([ len(vs) for vs in arr0 ])
#		arr1 = []
#		for vs in arr0:
#			arr1.append(vs[:minlen])
#		arr1 = np.array(arr1)
#		return arr1

