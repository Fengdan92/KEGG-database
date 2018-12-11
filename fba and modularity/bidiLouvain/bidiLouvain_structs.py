class Node(object):
    '''
    Node object.
    This object corresponds to an orginal node: a single metabolite or reaction.

    Initialization
    --------------
    node_id: string.
        Node name. e.g. 'glu__D_e', 'ATPM'
    node_type: int, 0 or 1.
        Node type. 
        type = 0, metabolites.
        type = 1, reactions.

    Other Attributes
    ----------------
    inNeighbors: dictionary { Node: float }. 
        Key: neighbor Node
        Value: inweight (neighbor -> self): float
    outNeighbors: dictionary { Node: float }.
        Key: neighbor Node
        Value: outweight (self -> neighbor): float
    inMetanodes: dictionary { MetaNode: float }
        Key: neighbor MetaNode
        Value: inweight (metanode -> self): float
    outMetanodes: dictionary { MetaNode: float }
        Key: neighbor MetaNode
        Value: outweight (self -> metanode): float
    metanode: MetaNode
        The metanode this node belongs to.
    '''
    def __init__(self, node_id, node_type):
        self.id = node_id
        self.type = node_type
        self.inNeighbors = {}
        self.outNeighbors = {}
        self.inMetanodes = {}
        self.outMetanodes = {} 

    def setMetanode(self, metanode):
        '''Set allegiance to metanode'''
        self.metanode = metanode



class MetaNode(object):
    '''
    MetaNode object.
    This object represents one vertex in each graph.
    Usually contains multiple Nodes.

    Initialization
    --------------
    member_nodes: list of Nodes
        Node members of this metanode.

    Other Attributes
    ----------------
    type: int, 0 or 1.
        Metanode type, based on its members' type.
        type = 0, metabolites.
        type = 1, reactions.
    inNeighbors: dictionary { MetaNode: float }. 
        Key: neighbor MetaNode
        Value: inweight (neighbor -> self): float
    outNeighbors: dictionary { MetaNode: float }.
        Key: neighbor MetaNode
        Value: outweight (self -> neighbor): float
    inComm: dictionary { Community: float }
        Key: neighbor Community
        Value: inweight (community -> self): float
    outComm: dictionary { Community: float }
        Key: neighbor Community
        Value: outweight (self -> community): float
    inDegree: float
        The total weight that are coming into this metanode.
    outDegree: float
        The total weight that are going out of this metanode.
    community: Community
        The community this metanode belongs to.
    '''
    def __init__(self, member_nodes):
        self.members = member_nodes
        self.type = member_nodes[0].type
        self.inNeighbors = {} 
        self.outNeighbors = {} 
        self.inComm = {}
        self.outComm = {}
        self.inDegree = None
        self.outDegree = None

    def setCommunity(self, community):
        '''Set allegiance to community'''
        self.community = community
    
    def updateInComm(self, metanode, fromComm, toComm):
        '''Update the inComm attribute of self, when its 
        inNeighbor metanode is moved from fromComm to toComm.'''
        if metanode in self.inNeighbors:
            self.inComm[fromComm] -= self.inNeighbors[metanode]
            if self.inComm[fromComm] < 1e-5:
                del self.inComm[fromComm]
            if toComm not in self.inComm:
                self.inComm[toComm] = self.inNeighbors[metanode]
            else:
                self.inComm[toComm] += self.inNeighbors[metanode]
    
    def updateOutComm(self, metanode, fromComm, toComm):
        '''Update the outComm attribute of self, when its 
        outNeighbor metanode is moved from fromComm to toComm.'''
        if metanode in self.outNeighbors:
            self.outComm[fromComm] -= self.outNeighbors[metanode]
            if self.outComm[fromComm] < 1e-5:
                del self.outComm[fromComm]
            if toComm not in self.outComm:
                self.outComm[toComm] = self.outNeighbors[metanode]
            else:
                self.outComm[toComm] += self.outNeighbors[metanode]
                


class Community(object):
    '''
    Community object.
    This object represents clusters in each graph.
    Usually contains multiple MetaNodes.

    Initialization
    --------------
    community_id: int
        Community ID.
    member_metanodes: list of MetaNodes
        MetaNode members of this community.

    Other Attributes
    ----------------
    type: int, 0 or 1.
        Community type, based on its members' type.
        type = 0, metabolites.
        type = 1, reactions.
    inNeighbors: dictionary { Community: float }. 
        Key: neighbor Community
        Value: inweight (neighbor -> self): float
    outNeighbors: dictionary { MetaNode: float }.
        Key: neighbor Community
        Value: outweight (self -> neighbor): float
    inDegree: float
        The total weight that are coming into this community.
    outDegree: float
        The total weight that are going out of this community.
    coCluster: Community
        The co-cluster of this community.
    modContribution: float
        The modularity contribution of this community.
    '''
    def __init__(self, community_id, member_metanodes):
        self.id = community_id
        self.members = member_metanodes
        self.type = member_metanodes[0].type
        self.inNeighbors = {} # dict. Community: weight = neighbor->self
        self.outNeighbors = {} # dict. Community: weight = self->neighbor
        self.inDegree = None
        self.outDegree = None

    def setCoCluster(self, cocluster):
        '''Set co-cluster'''
        self.coCluster = cocluster

    def setModContribution(self, modContribution):
        '''Set modularity contribution'''
        self.modContribution = modContribution

    def addMetaNode(self, metanode):
        '''Add metanode into this community'''
        self.members.append(metanode)
        for c, w in metanode.inComm.items():
            if c not in self.inNeighbors:
                self.inNeighbors[c] = w
            else:
                self.inNeighbors[c] += w
        for c, w in metanode.outComm.items():
            if c not in self.outNeighbors:
                self.outNeighbors[c] = w
            else:
                self.outNeighbors[c] += w
        self.inDegree += metanode.inDegree
        self.outDegree += metanode.outDegree

    def removeMetaNode(self, metanode):
        '''Remove metanode from this community'''
        self.members.remove(metanode)
        for c, w in metanode.inComm.items():
            self.inNeighbors[c] -= w
            if self.inNeighbors[c] < 1e-5:
                del self.inNeighbors[c]
        for c, w in metanode.outComm.items():
            self.outNeighbors[c] -= w
            if self.outNeighbors[c] < 1e-5:
                del self.outNeighbors[c]
        self.inDegree -= metanode.inDegree
        self.outDegree -= metanode.outDegree

    def updateIn(self, metanode, fromComm, toComm):
        ''' A metanode is moved from fromComm and toComm, and
        self is metanode's outComm.'''
        self.inNeighbors[fromComm] -= metanode.outComm[self]
        if self.inNeighbors[fromComm] < 1e-5:
            del self.inNeighbors[fromComm]
        if toComm not in self.inNeighbors:
            self.inNeighbors[toComm] = metanode.outComm[self]
        else:
            self.inNeighbors[toComm] += metanode.outComm[self]
    
    def updateOut(self, metanode, fromComm, toComm):
        ''' A metanode is moved from fromComm and toComm, and
        self is metanode's inComm.'''
        self.outNeighbors[fromComm] -= metanode.inComm[self]
        if self.outNeighbors[fromComm] < 1e-5:
            del self.outNeighbors[fromComm]
        if toComm not in self.outNeighbors:
            self.outNeighbors[toComm] = metanode.inComm[self]
        else:
            self.outNeighbors[toComm] += metanode.inComm[self]
        


class Graph(object):
    '''
    Graph object.
    Reprensents a network with metanodes as vertices.

    Initialization
    --------------
    metanodes: list of MetaNodes.
        This is the list of vertices of the network.

    Other Attributes
    ----------------
    communitiies: dictionary {int: Community}. 
        Key: community id: int
        Value: Community
        This is the communities of the network, constructed
        based on the metanodes' allegiance to communities.
    '''
    def __init__(self, metanodes):
        self.metanodes = metanodes 

    def updateCommunity(self):
        '''Update community active in this network'''
        self.communities = {} 
        for metanode in self.metanodes:
            if metanode.community.id not in self.communities:
                self.communities[metanode.community.id]=metanode.community