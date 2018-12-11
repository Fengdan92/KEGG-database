from bidiLouvain_structs import *
import random

def nodeInitialization(lst_metabolites, lst_reactions):
    '''
    Turn two lists of node names into one list of Nodes.

    Parameters
    ----------
    lst_metabolites : list of strings
        List of names of metabolites involved in the network.
    lst_reactions : list of strings
        List of reactions involved in the network.

    Returns
    -------
    node_metabolites + node_reactions: list of Nodes.
    '''
    node_metabolites = [ Node(x, 0) for x in lst_metabolites ]
    node_reactions = [ Node(x, 1) for x in lst_reactions ]
    return node_metabolites + node_reactions


def updateMetanodeNeighborsForNodes(lst_nodes):
    '''
    Update the metanode neighbors of nodes.
    Loop through neighbor nodes and find their allegiance, 
    then add up the corresponding weight.

    Parameters
    ----------
    lst_nodes : list of Nodes
        List of Nodes with known metanode allegiance, 
        type, inNeighbors, outNeighbors and node_id.

    Updates
    -------
    Each nodes inMetanodes and outMetanodes (dictionary { MetaNode: float }).
    '''
    for node in lst_nodes:
        node.inMetanodes = {}
        node.outMetanodes = {}
        for neighborNode in node.outNeighbors:
            try:
                node.outMetanodes[neighborNode.metanode] += node.outNeighbors[neighborNode]
            except KeyError:
                node.outMetanodes[neighborNode.metanode] = node.outNeighbors[neighborNode]
                
        for neighborNode in node.inNeighbors:
            try:
                node.inMetanodes[neighborNode.metanode] += node.inNeighbors[neighborNode]
            except KeyError:    
                node.inMetanodes[neighborNode.metanode] = node.inNeighbors[neighborNode]
           


def updateMetanodeNeighborsForMetaNodes(lst_metanodes):
    '''
    Update the metanode neighbors of metanodes.

    Parameters
    ----------
    lst_metanodes : list of MetaNodes
        List of MetaNodes with known members and type. 
        The member nodes have inMetanodes and outMetanodes info.

    Updates
    -------
    Each metanode's inNeighbors and outNeighbors (dictionary { MetaNode: float }).
    '''
    for metanode in lst_metanodes:
        for node in metanode.members:
            for m, w in node.inMetanodes.items():
                try:
                    metanode.inNeighbors[m] += w
                except KeyError:
                    metanode.inNeighbors[m] = w
                
            for m, w in node.outMetanodes.items():
                try:
                    metanode.outNeighbors[m] += w
                except KeyError:
                    metanode.outNeighbors[m] = w


def updateDegreeMetaNode(lst_metanodes):
    '''
    Update the inDegree and outDegree of metanodes.

    Parameters
    ----------
    lst_metanodes : list of MetaNodes
        List of MetaNodes with known inNeighbors and outNeighbors.

    Updates
    -------
    Each metanode's inDegree and outDegree (float).
    '''
    for metanode in lst_metanodes:
        metanode.inDegree = sum([w for w in metanode.inNeighbors.values()])
        metanode.outDegree = sum([w for w in metanode.outNeighbors.values()])


def updateCommNeighborsForMetaNodes(lst_metanodes):
    '''
    Update community neighbors of metanodes.

    Parameters
    ----------
    lst_metanodes : list of MetaNodes
        List of MetaNodes with known inNeighbors, outNeighbors 
        and community allegiance.

    Updates
    -------
    Each metanode's inComm and outComm (dictionary { Community: float }).
    '''
    for metanode in lst_metanodes:
        for neighborMetaNode in metanode.outNeighbors:
            try:
                metanode.outComm[neighborMetaNode.community] += metanode.outNeighbors[neighborMetaNode]
            except KeyError:
                metanode.outComm[neighborMetaNode.community] = metanode.outNeighbors[neighborMetaNode]

        for neighborMetaNode in metanode.inNeighbors:
            try:
                metanode.inComm[neighborMetaNode.community] += metanode.inNeighbors[neighborMetaNode]
            except KeyError:
                metanode.inComm[neighborMetaNode.community] = metanode.inNeighbors[neighborMetaNode]


def updateCommNeighborsForCommunity(dict_communities):
    '''
    Update community neighbors of communities.
    
    Parameters
    ----------
    dict_communities : dicitonary { int: Community }
        Key: community ID
        Value: Community
        The communities should have known members. And
        each member's inComm and outComm should be known.
    
    Updates
    -------
    Community's inNeighbors and outNeighbors (dictionary { Community: float }).
    '''
    for comm in dict_communities.values():
        for metanode in comm.members:
            for c, w in metanode.inComm.items():
                try:
                    comm.inNeighbors[c] += w
                except KeyError:
                    comm.inNeighbors[c] = w

            for c, w in metanode.outComm.items():
                try:
                    comm.outNeighbors[c] += w
                except KeyError:
                    comm.outNeighbors[c] = w


def updateDegreeComm(dict_communities):
    '''
    Update the inDegree and outDegree of communities.

    Parameters
    ----------
    dict_communities : dicitonary { int: Community }
        Key: community ID
        Value: Community
        The communities should have known inNeighbors
        and outNeightbors.

    Updates
    -------
    Each community's inDegree and outDegree (float).
    '''
    for comm in dict_communities.values():
        comm.inDegree = sum([w for w in comm.inNeighbors.values()])
        comm.outDegree = sum([w for w in comm.outNeighbors.values()])


def updateCoCluster(affected_communities, all_communities, M):
    '''
    Updates the affected_communities' co-cluster and modularity
    contribution, given all communities and total weight of the
    network M.
    
    Parameters
    ----------
    affected_communities: dicitonary { int: Community }
        Only these communities' co-cluster and modContribution 
        has changed, and therefore need to be updated.
    all_communities: dicitonary { int: Community }
        All communities present in the current network.
        Required information: community type, outNeighbors,
        inDegree and outDegree.
    M: float. 
        Total weight of the network (a constant).
    
    Updates
    -------
    Community's co-cluster and modularity contribution.
    '''
    for comm in affected_communities.values():
        _modGain = {}
        candidate = [x for x in all_communities.values() if x.type != comm.type] # all different-type communities
        for c in candidate:
            if c in comm.outNeighbors:
                _modGain[c] = comm.outNeighbors[c]/M - comm.outDegree/M*c.inDegree/M
            else:
                _modGain[c] = 0 - comm.outDegree/M*c.inDegree/M

        # Finds maximum in _modGain[k] and output the corresponding key
        cocluster=max(_modGain.keys(), key=(lambda k: _modGain[k])) # Community
        comm.setCoCluster(cocluster)
        comm.setModContribution(_modGain[cocluster])


def metanodeTestMove(graph, fromComm, toComm, metanodeMoved, M): 
    '''
    Test moving metanodeMoved from fromComm to toComm.
    The graph remain the same after testMove and a modularity 
    gain is returned.
    
    Parameters
    ----------
    graph: Graph
        The current network.
    fromComm: Community
        Metanode moved away from this community.
    toComm: Community
        Metanode moved to this community.
    metanodeMoved: Metanode
        The moved metanode.
    M: float
        Total weight of the network (a constant).
    
    Updates
    -------
    Graph is first updated for the move, and then
    updated again for the reverse move. Therefore,
    everything stays the same.
    
    Returns
    -------
    _modGain: float
        The modularity gain of the test move.
    '''
    # determine list of affected communities:
    # fromComm, toComm and ALL other-type communities
    # affectedCommunities = [fromComm, toComm] + [ x for x in graph.communities.values() if x.type != fromComm.type]
    #print("Test move.")
    affectedCommunities = [fromComm, toComm] + list(fromComm.inNeighbors.keys()) + list(fromComm.outNeighbors.keys()) + list(toComm.inNeighbors.keys()) + list(toComm.outNeighbors.keys())
    affectedCommunities = list(set(affectedCommunities))
    _modGain = 0
    
    dict_affComm = {}
    for comm in affectedCommunities:
        dict_affComm[comm.id]=comm

    # save old modularity contribution
    old_mod_contribution = {}
    for comm in affectedCommunities:
        old_mod_contribution[comm]=comm.modContribution
    
    # Test move: fromComm -> toComm
    metanodeMoved.setCommunity(toComm)
    for neighborMetaNode in metanodeMoved.outNeighbors:# metanodeMoved is neighborMetaNode's inNeighbor
        neighborMetaNode.updateInComm(metanode=metanodeMoved, fromComm=fromComm, toComm=toComm)
    for neighborMetaNode in metanodeMoved.inNeighbors:# metanodeMoved is neighborMetaNode's outNeighbor
        neighborMetaNode.updateOutComm(metanode=metanodeMoved, fromComm=fromComm, toComm=toComm)
    fromComm.removeMetaNode(metanodeMoved)
    toComm.addMetaNode(metanodeMoved)
    for neighborComm in metanodeMoved.outComm: # metanodeMoved -> neighborComm
        neighborComm.updateIn(metanode=metanodeMoved, fromComm=fromComm, toComm=toComm)
    for neighborComm in metanodeMoved.inComm: # neighborComm -> metanodeMoved
        neighborComm.updateOut(metanode=metanodeMoved, fromComm=fromComm, toComm=toComm)
    graph.updateCommunity()
    updateCoCluster(dict_affComm, graph.communities, M)
    
    for comm in affectedCommunities:
        _modGain += comm.modContribution - old_mod_contribution[comm]

    # now move it back: toComm -> fromComm
    metanodeMoved.setCommunity(fromComm)
    for neighborMetaNode in metanodeMoved.outNeighbors:# metanodeMoved is neighborMetaNode's inNeighbor
        neighborMetaNode.updateInComm(metanode=metanodeMoved, fromComm=toComm, toComm=fromComm)
    for neighborMetaNode in metanodeMoved.inNeighbors:# metanodeMoved is neighborMetaNode's outNeighbor
        neighborMetaNode.updateOutComm(metanode=metanodeMoved, fromComm=toComm, toComm=fromComm)
    fromComm.addMetaNode(metanodeMoved)
    toComm.removeMetaNode(metanodeMoved)
    for neighborComm in metanodeMoved.outComm: # metanodeMoved -> neighborComm
        neighborComm.updateIn(metanode=metanodeMoved, fromComm=toComm, toComm=fromComm)
    for neighborComm in metanodeMoved.inComm: # neighborComm -> metanodeMoved
        neighborComm.updateOut(metanode=metanodeMoved, fromComm=toComm, toComm=fromComm)
    graph.updateCommunity()
    updateCoCluster(dict_affComm, graph.communities, M)

    return _modGain

def metanodeMove(graph, fromComm, toComm, metanodeMoved, M):
    '''
    Move the metanode from fromComm to toComm.
    
    Parameters
    ----------
    graph: Graph
        The current network.
    fromComm: Community
        Metanode moved away from this community.
    toComm: Community
        Metanode moved to this community.
    metanodeMoved: Metanode
        The moved metanode.
    M: float
        Total weight of the network (a constant).
    
    Updates
    -------
    1. metanoteMoved.community.
    2. The inComm and outComm of metanode neighbors
       of the moved metanode.
    3. fromComm.members/inNeighbors/outNeighbors/inDgree/outDegree.
    4. inComm.members/inNeighbors/outNeighbors/inDgree/outDegree.
    5. Communities that are connected to the moved metanode. 
       Their in/outNeighbours changed.
    6. Whole graph's communities.
    7. All affected communities' co-clusters and modularity 
       contribution.
    '''
    #affectedCommunities = [fromComm, toComm] + [ x for x in graph.communities.values() if x.type != fromComm.type]
    affectedCommunities = [fromComm, toComm] + list(fromComm.inNeighbors.keys()) + list(fromComm.outNeighbors.keys()) + list(toComm.inNeighbors.keys()) + list(toComm.outNeighbors.keys())
    affectedCommunities = list(set(affectedCommunities))
    
    dict_affComm = {}
    for comm in affectedCommunities:
        dict_affComm[comm.id]=comm

    metanodeMoved.setCommunity(toComm)
    for neighborMetaNode in metanodeMoved.outNeighbors:# metanodeMoved is neighborMetaNode's inNeighbor
        neighborMetaNode.updateInComm(metanode=metanodeMoved, fromComm=fromComm, toComm=toComm)
    for neighborMetaNode in metanodeMoved.inNeighbors:# metanodeMoved is neighborMetaNode's outNeighbor
        neighborMetaNode.updateOutComm(metanode=metanodeMoved, fromComm=fromComm, toComm=toComm)
    fromComm.removeMetaNode(metanodeMoved)
    toComm.addMetaNode(metanodeMoved)
    for neighborComm in metanodeMoved.outComm: # metanodeMoved -> neighborComm
        neighborComm.updateIn(metanode=metanodeMoved, fromComm=fromComm, toComm=toComm)
    for neighborComm in metanodeMoved.inComm: # neighborComm -> metanodeMoved
        neighborComm.updateOut(metanode=metanodeMoved, fromComm=fromComm, toComm=toComm)
    graph.updateCommunity()
    updateCoCluster(dict_affComm, graph.communities, M)

def getModularity(g):
    '''Obtain modularity of graph g'''
    m = 0
    for comm in g.communities.values():
        m += comm.modContribution
    
    return m

def getCommStruc(g):
    '''Obtain community structure of g.
    return dictionary { comm.id: list of node.id }.'''
    commStruc = {}
    for comm in g.communities.values():
        nodes=[]
        for metanode in comm.members:
            for node in metanode.members:
                nodes.append(node.id)
        commStruc[comm.id]=nodes
    return commStruc
        

# iteration optimization of graph
def iterationOptimization(g, M):
    '''
    Iteration optimization of g. 
    All vertices are scanned linearly in an arbitrary
    order.
    
    Parameters
    ----------
    g: Graph
        Current network with full information of Nodes, 
        Metanodes and Communities.
    M: float
        Total weight of the graph.
    
    Updates
    -------
    Graph is being updated whenever this a metanode moved.
    
    Returns
    -------
    iterGain: float
        Modularity gain from this iteration.
    '''
    m_start = getModularity(g)
    #print("===============================================")
    #print("Starting iteration, m = ", m_start)
    
    lst_metanodes = g.metanodes
    # Randomize the list of metanodes
    random.shuffle(lst_metanodes) 

    iterGain = 0
    for metanode in lst_metanodes:
        C = metanode.community
        # Find candidate community for moving metanode
        lst_comm = [x for x in g.communities.values() if x.type == C.type] 
        lst_comm.remove(C)
        
        gain_flag = 0
        highestGainID = -1 
        for comm in lst_comm:
            _modGain = metanodeTestMove(graph=g, fromComm = C, toComm = comm, metanodeMoved=metanode, M=M)
            if _modGain > gain_flag:
                gain_flag = _modGain
                highestGainID = comm.id
        
        if highestGainID >= 0: # meaning there is a move that increased modularity
            metanodeMove(graph=g, fromComm = C, toComm = g.communities[highestGainID], metanodeMoved=metanode, M=M)
            iterGain += gain_flag
    
    #print("Iteration gain is", iterGain)
    m_end = getModularity(g)
    #print("Ending iteration, m = ", m_end)
    #print("===============================================")
    
    return iterGain



def PhaseOptimization(g, M, cutoffIterations = 0.01):
    '''
    Phase optimization of graph g. 
    A phase stops when iteration modularity gain
    is no bigger than cuttoffIterations.

    Parameters
    ----------
    g : Graph
        The new compact graph from last phase, 
        or the level 1 graph if this is the first
        phase.
    M : float
        Total weight of the graph (constant).
    cutoffIterations : float. Default = 0.01.
        Stop iteration if iterGain is smaller than or equal to 0.01.
    
    Returns
    -------
    phase_gain : float
        The maximized modularity gain of this phase.
    g_new : Graph
        the new compact graph after this phase finished.
    g : Graph
        the updated input graph, before compaction.
    '''
    #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    #print("Phase starts")
    # start of the phase
    phaseGain = 0
    
    # Initialzie communities
    communityID = 0
    dict_communities = {}
    for metanode in g.metanodes:
        comm = Community(community_id = communityID, member_metanodes = [metanode])
        dict_communities[communityID] = comm
        metanode.setCommunity(comm)
        communityID += 1

    # Update communities
    g.updateCommunity()
    
    # Update inComm and outComm of all metanodes
    updateCommNeighborsForMetaNodes(g.metanodes)

    # Update neighbors of communities
    updateCommNeighborsForCommunity(g.communities)

    # Update community degrees
    updateDegreeComm(g.communities)

    # Update co-cluster and M contribution of community. 
    updateCoCluster(affected_communities = g.communities, all_communities = g.communities, M=M)
    
    iterGain = iterationOptimization(g, M)
    phaseGain += iterGain
    while(iterGain > cutoffIterations):
        iterGain = iterationOptimization(g, M)
        phaseGain += iterGain

    # graph compaction
    lst_metanodes = []
    comm_meta = {}
    for comm in g.communities.values():
        new_members = [] # new node members for new metanode
        for metanode in comm.members:
            new_members = new_members + metanode.members
        compMeta = MetaNode(new_members)
        compMeta.inDegree = comm.inDegree
        compMeta.outDegree = comm.outDegree
        comm_meta[comm]=compMeta
        lst_metanodes.append(compMeta)

    for comm, meta in comm_meta.items():
        for inComm in comm.inNeighbors:
            meta.inNeighbors[comm_meta[inComm]]=comm.inNeighbors[inComm]
        for outComm in comm.outNeighbors:
            meta.outNeighbors[comm_meta[outComm]]=comm.outNeighbors[outComm]

    for meta in lst_metanodes:
        for node in meta.members:
            node.setMetanode(meta)

    g_new = Graph(lst_metanodes)
    #print("Phase gain is", phaseGain)
    #print("Phase ends")
    #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    return phaseGain, g_new, g
