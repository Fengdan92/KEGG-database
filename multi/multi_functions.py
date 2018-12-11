import os
import subprocess

import networkx as nx
import sys
from community_functions import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import colorsys

work_direct = '/scratch9/fengdan/KEGG/files/'

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

    return None

def obtain_pairs(bact, dict_bact_ec, dict_ec_pairs):
	'''
	bact : string
		name of the bacteirum
	dict_bact_ec : dict
		key - bacteria names (string)
		value - list of enzymes (list of strings)
	dict_ec_pairs : dict
		key - enzymes (string)
		value - list of reactant pairs (list of tuples)
	'''
	info('function obtain_pairs')
	lst_ec = dict_bact_ec[bact]
	pairs_full = []
	for ec in lst_ec:
		if ec in dict_ec_pairs:
			lst_pairs = dict_ec_pairs[ec]
			for pair in lst_pairs:
				if pair not in pairs_full:
					pairs_full.append(pair)

	file_name = work_direct + bact + '_pairs_full_directed.txt'
	with open(file_name,'w') as fp:
		fp.write('\n'.join('{}\t{}'.format(x[0],x[1]) for x in pairs_full))

	return None


def DiLouvain(bact):
	'''
	bact : string
		name of the bacterium.
	'''
	info('directed louvain')
	fn = bact + '_pairs_full_directed.txt'
	file = open(work_direct + fn, 'r')
	data_edges = file.read()
	data_lst=data_edges.split('\n')
	if data_lst[len(data_lst)-1] == '':
		data_lst = data_lst[:len(data_lst)-1]
		# remove the empty line at the end if needed

	if not data_lst: 
		# if data_lst is empty
		print 'This bacterium has empty pairs: ' + bact
		return None

	output = subprocess.check_output(['./kegg_louvain.sh', fn, bact])

	return None

def DiLouvain_after(bact):
	'''
	bact : string
		name of the bacterium.
	'''
	info('directed louvain (after)')
	fn = bact + '_pairs_full_directed_after.txt'
	file = open(work_direct + fn, 'r')
	data_edges = file.read()
	data_lst=data_edges.split('\n')
	if data_lst[len(data_lst)-1] == '':
		data_lst = data_lst[:len(data_lst)-1]
		# remove the empty line at the end if needed

	if not data_lst: 
		# if data_lst is empty
		return None

	bn = bact + '_after'
	output = subprocess.check_output(['./kegg_louvain.sh', fn, bn])

	return None


def _match_labels(fp_pair_orig, fp_pair_new):
	'''
	Obtain the one-to-one relation between original node labels and
	the renumerated labels done by kegg_louvain.sh.

	Parameters
	----------
	fp_pair_orig : file 
		File that contains the orginal reactant pair information.
	fp_pair_new : file
		File that contains the new, renumerated reactant pair information.

	Returns
	-------
	label_dict : dictionary
		Contains the one-to-one relation between original node labels and the renumerated labels.
		Keys: new labels (string)
		Values: original labels (string)
	'''
	data_orig = fp_pair_orig.read()
	lines_orig=data_orig.split('\n')
	if lines_orig[len(lines_orig)-1] == '':
		lines_orig = lines_orig[:len(lines_orig)-1]
	
	data_new = fp_pair_new.read()
	lines_new=data_new.split('\n')
	if lines_new[len(lines_new)-1] == '':
		lines_new = lines_new[:len(lines_new)-1]


	if len(lines_orig) != len(lines_new):
		print('FILES DOES NOT MATCH!')
		sys.exit()

	edges_orig = []
	for row in lines_orig:
		lst = row.split('\t')
		edges_orig.append((lst[0],lst[1]))

	edges_new = []
	for row in lines_new:
		lst = row.split(' ')
		edges_new.append((lst[0],lst[1]))


	label_dict = {}
	for idx in range(0, len(edges_new)):
		if edges_new[idx][0] not in label_dict:
			label_dict[edges_new[idx][0]] = edges_orig[idx][0]
		if edges_new[idx][1] not in label_dict:
			label_dict[edges_new[idx][1]] = edges_orig[idx][1]

	return label_dict


def create_graph(bact):
	info('create_graph')
	G = nx.DiGraph()
	fn = bact + '_pairs_full_directed.txt'
	file = open(work_direct + fn, 'r')
	data_edges = file.read()
	data_lst=data_edges.split('\n')
	if data_lst[len(data_lst)-1] == '':
		data_lst = data_lst[:len(data_lst)-1]
		# remove the empty line at the end if needed

	if not data_lst: 
		# if data_lst is empty
		filename_edges_after = bact + '_pairs_full_directed_after.txt' 
		with open(work_direct + filename_edges_after,'w') as fp:
			fp.write('\n'.join('{}\t{}'.format(x[0],x[1]) for x in G.edges()))
		return None

	edges_lst = []
	for row in data_lst:
		lst = row.split('\t')
		edges_lst.append((lst[0],lst[1]))
		# (src, dest)

	G.add_edges_from(edges_lst)
	#print(nx.info(G))

	fp_pair_orig = open(work_direct + fn, 'r')
	fp_pair_new = open(work_direct + fn + '_renum', 'r')

	label_dict = _match_labels(fp_pair_orig = fp_pair_orig, fp_pair_new = fp_pair_new)

	filename_partition = 'partition_' + bact + '.txt'

	file = open(work_direct + filename_partition, 'r')
	data_partition = file.read()
	lst_partition = data_partition.split('\n')
	if lst_partition[len(lst_partition)-1] == '':
		lst_partition = lst_partition[:len(lst_partition)-1]

	partition_new = {}
	for row in lst_partition:
		lst = row.split(' ')
		partition_new[lst[0]]=int(lst[1])
		# lst[0] is a string
	partition_orig = {}
	for key, value in partition_new.items():
		partition_orig[label_dict[key]]=value

	size = float(len(set(partition_orig.values()))) # number of communities
	[pos, pos_hyper, hypergraph] = community_layout(G, partition_orig)
	nx.draw(hypergraph, pos_hyper, node_size = 50)
	plt.savefig(work_direct + 'hypergraph_' + bact + '.png', format='png', bbox_inches="tight", dpi=300)
	plt.clf()


	count = 0.
	for com in set(partition_orig.values()) :
		count += 1. # counting communities
		list_nodes = [nodes for nodes in partition_orig.keys() if partition_orig[nodes] == com]
		nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20, node_color = cm.gnuplot(count / size))
	nx.draw_networkx_edges(G, pos, alpha=0.5)
	#plt.show()
	plt.savefig(work_direct + 'final_graph_' + bact + '.png', format='png', bbox_inches="tight", dpi=300)
	plt.clf()

	# remove border isoaltes
	com_removed=list(nx.isolates(hypergraph))
	nodes_removed=[]
	for key,value in partition_orig.items():
		if value in com_removed:
			nodes_removed.append(key)

	G.remove_nodes_from(nodes_removed)
	filename_edges_after = bact + '_pairs_full_directed_after.txt' 
	with open(work_direct + filename_edges_after,'w') as fp:
		fp.write('\n'.join('{}\t{}'.format(x[0],x[1]) for x in G.edges()))


	return None

def create_graph_after(bact):
	info('create_graph (after)')
	rgb_tuple = [(0,0,0),(1,0,103),(213,255,0),(255,0,86),(158,0,142),(14,76,161),(255,229,2),(0,95,57),
(0,255,0),(149,0,58),(255,147,126),(164,36,0),(0,21,68),(145,208,203),(98,14,0),(107,104,130),
(0,0,255),(0,125,181),(106,130,108),(0,174,126),(194,140,159),(190,153,112),(0,143,156),
(95,173,78),(255,0,0),(255,0,246),(255,2,157),(104,61,59),(255,116,163),(150,138,232),(152,255,82),
(167,87,64),(1,255,254),(255,238,232),(254,137,0),(189,198,255),(1,208,255),(187,136,0),(117,68,177),
(165,255,210),(255,166,254),(119,77,0),(122,71,130),(38,52,0),(0,71,84),(67,0,44),(181,0,255),
(255,177,103),(255,219,102),(144,251,146),(126,45,210),(189,211,147),(229,111,254),(222,255,116),
(0,255,120),(0,155,255),(0,100,1),(0,118,255),(133,169,0),(0,185,23),(120,130,49),(0,255,198),
(255,110,65),(232,94,190)]
	strcolor=['#%02x%02x%02x' % x for x in rgb_tuple]

	G = nx.DiGraph()
	fn = bact + '_pairs_full_directed_after.txt'
	file = open(work_direct + fn, 'r')
	data_edges = file.read()
	data_lst=data_edges.split('\n')
	if data_lst[len(data_lst)-1] == '':
		data_lst = data_lst[:len(data_lst)-1]
		# remove the empty line at the end if needed

	if not data_lst: 
		# if data_lst is empty
		return None

	edges_lst = []
	for row in data_lst:
		lst = row.split('\t')
		edges_lst.append((lst[0],lst[1]))
		# (src, dest)

	G.add_edges_from(edges_lst)
	#print(nx.info(G))

	fp_pair_orig = open(work_direct + fn, 'r')
	fp_pair_new = open(work_direct + fn + '_renum', 'r')

	label_dict = _match_labels(fp_pair_orig = fp_pair_orig, fp_pair_new = fp_pair_new)

	filename_partition = 'partition_' + bact + '_after.txt'

	file = open(work_direct + filename_partition, 'r')
	data_partition = file.read()
	lst_partition = data_partition.split('\n')
	if lst_partition[len(lst_partition)-1] == '':
		lst_partition = lst_partition[:len(lst_partition)-1]

	partition_new = {}
	for row in lst_partition:
		lst = row.split(' ')
		partition_new[lst[0]]=int(lst[1])
		# lst[0] is a string
	partition_orig = {}
	for key, value in partition_new.items():
		partition_orig[label_dict[key]]=value


	size = float(len(set(partition_orig.values()))) # number of communities
	[pos, pos_hyper, hypergraph] = community_layout(G, partition_orig)
	nx.draw(hypergraph, pos_hyper, node_size = 50); 
	plt.savefig(work_direct + 'hypergraph_' + bact + '_after.png', format='png', bbox_inches="tight", dpi=300)
	plt.clf()

	count = 0.
	for com in set(partition_orig.values()) :
		count += 1. # counting communities
		list_nodes = [nodes for nodes in partition_orig.keys() if partition_orig[nodes] == com]
		nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20, node_color = strcolor[int(count)])
	nx.draw_networkx_edges(G, pos, alpha=0.5)
	#plt.show()
	plt.savefig(work_direct + 'final_graph_' + bact + '_after.png', format='png', bbox_inches="tight", dpi=300)
	plt.clf()

	return None