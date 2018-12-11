from multiprocessing import Process, Manager, Pool, cpu_count
from math import floor
import os
from multi_functions import *
from functools import partial
import pickle

os.system('taskset -p -c 0-55 %s' % os.getpid())
# avoid task affinity being messed up. ONLY WORKS ON LINUX.

if __name__ == '__main__':
	info('main line')
	print 'Reading files...'
	manager = Manager()
	lst_bact = manager.list()
	dict_bact_ec = manager.dict()
	dict_ec_pairs = manager.dict()
	
	file1 = open(r'lst_bact.pkl', 'rb')
	lst_bact = pickle.load(file1)
	file1.close()

	file2 = open(r'dict_bact_ec.pkl', 'rb')
	dict_bact_ec = pickle.load(file2)
	file2.close()

	file3 = open(r'dict_ec_pairs.pkl', 'rb')
	dict_ec_pairs = pickle.load(file3)
	file3.close()

	print 'Printing pairs to file...'
	MAXCPU = cpu_count()
	pool_pairs = Pool(MAXCPU)
	print '>>> number of processes to use: ' + str(MAXCPU)
	pairs_par = partial(obtain_pairs, dict_bact_ec=dict_bact_ec, dict_ec_pairs=dict_ec_pairs)
	pool_pairs.map(pairs_par, lst_bact)
	pool_pairs.close()
	pool_pairs.join()
	print '...Done.'
	
	print 'Calculating modularity using directed Louvain...'
	cp = int(floor(MAXCPU*1))
	# avoid memory full issue
	print 'number of processes to use: ' + str(cp)
	pool_louvain = Pool(cp)
	pool_louvain.map(DiLouvain, lst_bact)
	pool_louvain.close()
	pool_louvain.join()
	print '...Done'
	
	print 'Start graphing (and remove isolates)...'
	pool_graph = Pool(cp)
	pool_graph.map(create_graph, lst_bact)
	pool_graph.close()
	pool_graph.join()
	print '...Done'

	print 'Calculating modularity using directed louvain (after)...'
	cp = int(floor(MAXCPU*1))
	# avoid memory full issue
	print 'number of processes to use: ' + str(cp)
	pool_louvain = Pool(cp)
	pool_louvain.map(DiLouvain_after, lst_bact)
	pool_louvain.close()
	pool_louvain.join()
	print '...Done'

	print 'Start graphing (after)...'
	pool_graph = Pool(cp)
	pool_graph.map(create_graph_after, lst_bact)
	pool_graph.close()
	pool_graph.join()
	print '...Done'
