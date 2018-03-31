from os.path import join, expanduser
walterPath = join(expanduser('~'), 'walter')
import sys
sys.path.append(walterPath)
import pbsGridWalker.routes as rt

involvedGitRepositories = {'evs': join(walterPath, 'evs'),
                           'pyrosim': join(walterPath, 'pyrosim'),
                           'pbsGridWalker': join(walterPath, 'pbsGridWalker'),
                           'walter': walterPath}
randSeedFile = join(involvedGitRepositories['pbsGridWalker'], 'seedFiles', 'randints1501268598.dat')
evsExecutable = join(involvedGitRepositories['evs'], 'evsServer.py')
simulatorExecutable = join(involvedGitRepositories['pyrosim'], 'pyrosim', 'simulator', 'simulator')
evaluatorExecutable = join(walterPath, 'evaluator.py')

import imp
pbsEnv = imp.load_source('pbsEnv', rt.pbsEnv)
python3 = pbsEnv.python3
python2 = pbsEnv.python2
