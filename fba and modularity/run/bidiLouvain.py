from bidiLouvain_structs import * 
from bidiLouvain_utils import *

def bidilouvain(lst_metabolites, lst_reactions, edges):
    '''
    Given network information, calculate the maximized modularity
    of a directed bipartite network

    Parameters
    ----------
    lst_metabolites : list of strings
        List of names of metabolites involved in the network.
    lst_reactions : list of strings
        List of reactions involved in the network
    edges : dictionary { (str, str): float }. 
        Key: (src, dest) - tuple of strings. 
        Value: edge weight - float
        Dictionary of directed metabolite - reaction pairs with edge weight.

    Returns
    -------
    maxM : float
        Maximized modularity given by directed bipartite Louvain algorithm.
    graphs : list of Graphs
        the list of graphs on different hierarchical level.

    References
    ----------
    Pesantez-Cabrera Paola, and Ananth Kalyanaraman. Efficient Detection of 
    Communities in Biological Bipartite Networks, IEEE/ACM Transactions on 
    Computational Biology and Bioinformatics (TCBB), 2017.
    '''
    
    # print('Number of metabolites: ', len(lst_metabolites))
    # print('Number of reactions: ', len(lst_reactions))
    # print('number of edges: ', len(edges))
    cutoffIterations = 0.01
    cutoffPhases = 0.0

    # Total weight
    M = sum([x for x in edges.values()])

    ''' INITIALIZAION '''

    # Turn lists of strings into one list of Nodes
    lst_nodes = nodeInitialization(lst_metabolites, lst_reactions)

    # Dictionary of nodes. Just for the purpose of initializing node neighbors (see below)
    dict_nodes = {}
    for node in lst_nodes:
        dict_nodes[node.id]=node

    # Obtain neighbors of each node
    for edge, weight in edges.items():
        srcNode = dict_nodes[edge[0]]
        destNode = dict_nodes[edge[1]]
        # update neighbors
        srcNode.outNeighbors[destNode] = weight
        destNode.inNeighbors[srcNode] = weight

    # Remove unnecessary references
    dict_nodes = None
    srcNode = None
    destNode = None

    # Initialzie lst of metanodes, update nodes' metanode allegiance
    lst_metanodes = []
    for node in lst_nodes:
        meta = MetaNode(member_nodes=[node])
        lst_metanodes.append(meta)
        node.setMetanode(meta)

    # Update the metanode neighbors of nodes
    updateMetanodeNeighborsForNodes(lst_nodes)

    # Update the metanode neighbors of metanodes
    updateMetanodeNeighborsForMetaNodes(lst_metanodes)

    # Update the metanode in and out degrees
    updateDegreeMetaNode(lst_metanodes)

    # Create graph
    g = Graph(lst_metanodes)

    # store graphs at each level
    graphs = []

    [phaseGain, g, g_finish] = PhaseOptimization(g, M, cutoffIterations)
    updateMetanodeNeighborsForNodes(lst_nodes)
    graphs.append(g_finish)

    while(phaseGain > cutoffPhases):
        [phaseGain, g, g_finish] = PhaseOptimization(g, M, cutoffIterations)
        updateMetanodeNeighborsForNodes(lst_nodes)
        graphs.append(g_finish)

    # Calculate maximized modularity
    finalGraph = graphs[-1]
    lstComm=list(finalGraph.communities.values())
    numComm=len(lstComm)
    maxM = 0
    for comm in lstComm:
        maxM += comm.modContribution
    #print("Modularity optimization has ended with maxM = ", maxM)
    #print("Number of communities: ", numComm)
    
    return maxM, graphs
