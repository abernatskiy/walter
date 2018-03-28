from os.path import exists
import os

import pbsGridWalker.tools.algorithms as tal
import pbsGridWalker.tools.iniWriter as tiniw
import pbsGridWalker.tools.fsutils as tfs
#import pbsGridWalker.tools.fileIO as tfio # for writeColumns()

import clusterRoutes as cr
import clusterClassifiers as cl

def prepareEnvironment(experiment):
	if not exists(cr.simulatorExecutable):
		raise RuntimeError('Simulator executable not found at ' + cr.simulatorExecutable)
	if not exists(cr.evaluatorExecutable):
		raise RuntimeError('Evaluator executable not found at ' + cr.evaluatorExecutable)
	if not exists(cr.evsExecutable):
		raise RuntimeError('EVS executable not found at ' + cr.evsExecutable)

def runComputationAtPoint(worker, params, evsAdditionalParams, parallelClients=1):
	print('Running evs-arrowbots pair with the following parameters: ' + str(params))
	parsedParams = tal.classifyDictWithRegexps(params, cl.serverClientClassifier)
	serverParams = tal.sumOfDicts(parsedParams['server'], evsAdditionalParams)
	print('Server params: ' + str(serverParams))
	#clientParams = tal.sumOfDicts(parsedParams['client'], arrowbotsAdditionalParams)
	#print('Client params: ' + str(clientParams))
	tiniw.write(serverParams, cl.evsClassifier, 'evs.ini')
	#tiniw.write(clientParams, classifiers.arrowbotsClassifier, 'arrowbot.ini')
	#tfio.writeColumns(arrowbotInitialConditions, 'initialConditions.dat')
	#tfio.writeColumns(arrowbotTargetOrientations, 'targetOrientations.dat')

	geneFifos = []
	evalFifos = []
	for i in range(parallelClients):
		geneFifos.append(tfs.makeUniqueFifo('.', 'indiv' + str(i)))
		evalFifos.append(tfs.makeUniqueFifo('.', 'evals' + str(i)))

	clientProcs = []
	for gf, ef in zip(geneFifos, evalFifos):
		clientProcs.append(worker.spawnProcess([cr.evaluatorExecutable, gf, ef]))

	if not worker.runCommand([cr.evsExecutable, 'evals', 'indiv', str(serverParams['randomSeed']), 'evs.ini']):
		return False

	for cp in clientProcs:
		worker.killProcess(cp, label='client')

	for gf, ef in zip(geneFifos, evalFifos):
		os.remove(gf)
		os.remove(ef)

	# TODO: Validation of the obtained files here

	return True
