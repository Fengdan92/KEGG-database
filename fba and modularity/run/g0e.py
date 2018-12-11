import pickle
from bidiLouvain import *
from bidiLouvain_utils import *
import random
import sys

runNumber = str(sys.argv[1]) # the first external argument, in string. Worldrank.
#millis = int(round(time.time() * 1000))
#rndseed = millis + int(runNumber)*37
random.seed()
#print "g0e run number " + str(runNumber) + " has random seed: " + str(rndseed)

file1 = open('/scratch/fy9/g0e/lst_reactions_g0e.pkl', 'rb')
lst_reactions = pickle.load(file1)
file1.close()

file2 = open('/scratch/fy9/g0e/lst_metabolites_g0e.pkl', 'rb')
lst_metabolites = pickle.load(file2)
file2.close()

file3 = open('/scratch/fy9/g0e/edges_g0e.pkl', 'rb')
edges_tmp = pickle.load(file3)
file3.close()

lst_reactions = [x.encode('ascii','ignore') for x in lst_reactions]
lst_metabolites = [x.encode('ascii','ignore') for x in lst_metabolites]

edges = {}
for key, value in edges_tmp.items():
    src = key[0].encode('ascii','ignore')
    dest = key[1].encode('ascii','ignore')
    edges[(src,dest)]=value 

[maxM, graphs]=bidilouvain(lst_metabolites, lst_reactions, edges)
print "g0e run number " + str(runNumber) + " has maximum modularity: " + str(maxM)
# this will show up in the .out files in /scratch/fy9/run folder

# Print community strcuture
filename = '/scratch/fy9/g0e/commStruc_g0e_run' + runNumber + '.pkl'
s=getCommStruc(graphs[-1])
file = open(filename, 'wb')
pickle.dump(s, file)
file.close()

# Print partition info
partition = {}
for key, value in s.items():
    for node in value:	
        partition[node]=key
filename = '/scratch/fy9/g0e/partition_g0e_run' + runNumber + '.pkl'
file = open(filename, 'wb')
pickle.dump(partition, file)
file.close()

# Print co-cluster info
dict_cocluster = {}
for comm in graphs[-1].communities.values():
    dict_cocluster[comm.id]= comm.coCluster.id
filename = '/scratch/fy9/g0e/cocluster_g0e_run' + runNumber + '.pkl'
file = open(filename, 'wb')
pickle.dump(dict_cocluster, file)
file.close()
