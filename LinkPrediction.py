##########################################################################################
# LinkPrediction.py  - http://www.research.rutgers.edu/~ss2078/papers/LinkPrediction.pdf
# Purpose: script contains methods for 10 link prediction algorithms
# version 1.1.0
# date: 01.28.2017
##########################################################################################


# import module/script dependencies
import networkx as nx
import numpy as np
import random
import six



def DegreeProduct(graph, edges):
    ''' Function takes a networkx graph object and list of edges calculates the Degree Product for these edges given the
    structure of the graph.
    :param graph: networkx graph object
    :param edges: list of tuples
    :return: a dictionary of scores for the edges
    '''
    scores = {}

    for edge in edges:
        i = edge[0]
        j = edge[1]

        scores[edge] = (nx.degree(graph, i) * nx.degree(graph, j))

    return scores


def CommonNeighbors(graph, edges):
    ''' Function takes a networkx graph object and list of edges calculates the Common Neighbors for these edges given the
    structure of the graph.
    :param graph: networkx graph object
    :param edges: list of tuples
    :return: a dictionary of scores for the edges
    '''
    scores = {}

    for edge in edges:
        i = edge[0]
        j = edge[1]
        i_neighbors = set(graph[i].keys())
        j_neighbors = set(graph[j].keys())

        if len(i_neighbors) == 0 or len(j_neighbors) == 0:
            scores[edge] = 0.0

        elif len(i_neighbors.intersection(j_neighbors)) == 0:
            scores[edge] = 0.0

        else:
            n_intersection = set(graph[i].keys()).intersection(set(graph[j].keys()))
            scores[edge] = float(len(n_intersection))

    return scores


def Jaccard(graph, edges):
    ''' Function takes a networkx graph object and list of edges calculates the Jaccard for these edges given the
    structure of the graph.
    :param graph: networkx graph object
    :param edges: list of tuples
    :return: a dictionary of scores for the edges
    '''
    scores = {}

    for edge in edges:
        i = edge[0]
        j = edge[1]
        i_neighbors = set(graph[i].keys())
        j_neighbors = set(graph[j].keys())

        if len(i_neighbors) == 0 or len(j_neighbors) == 0:
            scores[edge] = 0.0

        elif len(i_neighbors.intersection(j_neighbors)) == 0:
            scores[edge] = 0.0

        else:
            n_intersection = set(graph[i].keys()).intersection(set(graph[j].keys()))
            n_union = set(graph[i].keys()).union(set(graph[j].keys()))
            scores[edge] = float(len(n_intersection))/len(n_union)

    return scores


def Sorensen(graph, edges):
    ''' Function takes a networkx graph object and list of edges calculates the Sorenson Similarity for these edges
    given the structure of the graph.
    :param graph: networkx graph object
    :param edges: list of tuples
    :return: a dictionary of scores for the edges
    '''
    scores = {}

    for edge in edges:
        i = edge[0]
        j = edge[1]
        i_neighbors = set(graph[i].keys())
        j_neighbors = set(graph[j].keys())

        if len(i_neighbors) == 0 or len(j_neighbors) == 0:
            scores[edge] = 0.0

        elif len(i_neighbors.intersection(j_neighbors)) == 0:
            scores[edge] = 0.0

        else:
            n_intersection = set(graph[i].keys()).intersection(set(graph[j].keys()))
            n_degree = graph.degree(i) + graph.degree(j)
            scores[edge] = float(len(n_intersection))/n_degree

    return scores


def LHN(graph, edges):
    ''' Function takes a networkx graph object and list of edges calculates the Leicht-Holme-Newman for these edges given the
    structure of the graph.
    :param graph: networkx graph object
    :param edges: list of tuples
    :return: a dictionary of scores for the edges
    '''

    scores = {}

    for edge in edges:
        i = edge[0]
        j = edge[1]
        i_neighbors = set(graph[i].keys())
        j_neighbors = set(graph[j].keys())

        if len(i_neighbors) == 0 or len(j_neighbors) == 0:
            scores[edge] = 0.0

        elif len(i_neighbors.intersection(j_neighbors)) == 0:
            scores[edge] = 0.0

        else:
            n_intersection = set(graph[i].keys()).intersection(set(graph[j].keys()))
            n_degree = graph.degree(i) * graph.degree(j)
            scores[edge] = float(len(n_intersection))/n_degree

    return scores


def ShortestPath(graph, edges):
    ''' Function takes a networkx graph object and list of edges calculates the shortest path for these edges given the
    structure of the graph.
    :param graph: networkx graph object
    :param edges: list of tuples
    :return: a dictionary of scores for the edges
    '''

    scores = {}

    for edge in edges:
        i = edge[0]
        j = edge[1]

        if nx.has_path(graph, i, j):
            scores[edge] = 1.0/len(nx.shortest_path(graph, i, j))

        else:
            scores[edge] = 0.0

    return scores


def ResourceAllocation(graph, edges):
    ''' Function takes a networkx graph object and list of edges calculates the resource allocation for these edges
    given the structure of the graph.
    :param graph: networkx graph object
    :param edges: list of tuples
    :return: a dictionary of scores for the edges
    '''
    scores = {}

    for edge in edges:
        i = edge[0]
        j = edge[1]
        i_neighbors = set(graph[i].keys())
        j_neighbors = set(graph[j].keys())

        if len(i_neighbors) == 0 or len(j_neighbors) == 0:
            scores[edge] = 0.0

        elif len(i_neighbors.intersection(j_neighbors)) == 0:
            scores[edge] = 0.0

        else:
            w = []
            n_intersection = i_neighbors.intersection(j_neighbors)

            for c in n_intersection:
                w.append(graph.degree(c))
            scores[edge] = 1.0/np.sum(w)

    return scores


def AdamicAdvar(graph, edges):
    ''' Function takes a networkx graph object and list of edges calculates the Adamic Advar for these edges given the
    structure of the graph.
    :param graph: networkx graph object
    :param edges: list of tuples
    :return: a dictionary of scores for the edges
    '''

    scores = {}

    for edge in edges:
        i = edge[0]
        j = edge[1]
        i_neighbors = set(graph[i].keys())
        j_neighbors = set(graph[j].keys())

        if len(i_neighbors) == 0 or len(j_neighbors) == 0:
            scores[edge] = 0.0

        elif len(i_neighbors.intersection(j_neighbors)) == 0:
            scores[edge] = 0.0

        else:
            w = []
            n_intersection = set(graph[i].keys()).intersection(set(graph[j].keys()))

            for c in n_intersection:
                w.append(1.0/np.log(g.degree(c)))
            scores[edge] = np.sum(w)

    return scores


##for the following algorithms parameter values were chosen to be consistent with:
#Liben-Nowell D, Kleinberg J. The link-prediction problem for social networks. Journal of the American society for information science and technology.

def katz(G, beta=0.001, max_power=5, weight=None, dtype=None): #https://github.com/rafguns/linkpred/blob/master/linkpred/predictors/path.py
    """Predict by Katz (1953) measure
    Let 'A' be an adjacency matrix for the directed network `G`.
    Then, each element 'a_{ij}' of 'A^k' (the `k`-th power of `A`) has a
    value equal to the number of walks with length `k` from `i` to `j`.
    The probability of a link rapidly decreases as the walks grow longer.
    Katz therefore introduces an extra parameter (here beta) to weigh
    longer walks less.
    Parameters
    ----------
    beta : a float
        the value of beta in the formula of the Katz equation
    max_power : an int
        the maximum number of powers to take into account
    weight : string or None
        The edge attribute that holds the numerical value used for
        the edge weight.  If None then treat as unweighted.
    dtype : a data type
        data type of edge weights (default numpy.int32)
    """
    ineligible = G.edges()
    nodelist = G.nodes()
    adj = nx.to_scipy_sparse_matrix(G, dtype=np.int32, weight=weight)
    res = {}

    for k in range(1, max_power + 1):
        matrix = (adj ** k).tocoo()
        for i, j, d in zip(matrix.row, matrix.col, matrix.data):
            if i == j:
                continue
            u, v = nodelist[i], nodelist[j]
            # if nx.has_path(G, u, v):
            if (u,v) not in ineligible:
                w = d * (beta ** k)
                res[(u,v)] = 0.0
                res[(u,v)] += w
    # if not G.is_directed():
        # We count double in case of undirected networks ((i, j) and (j, i))
    for pair in res:
        res[pair]/= 2

    return res


def raw_google_matrix(G, nodelist=None, weight=None):
    """Calculate the raw Google matrix (stochastic without teleportation); taken from: https://github.com/rafguns/linkpred/blob/master/linkpred/network/algorithms.py"""
    M = nx.to_numpy_matrix(G, nodelist=nodelist, dtype=np.float32, weight=weight)
    n, m = M.shape  # should be square
    assert n == m and n > 0
    # Find 'dangling' nodes, i.e. nodes whose row's sum = 0
    dangling = np.where(M.sum(axis=1) == 0)
    # add constant to dangling nodes' row
    for d in dangling[0]:
        M[d] = 1.0 / n
    # Normalize. We now have the 'raw' Google matrix (cf. example on p. 11 of
    # Langville & Meyer (2006)).
    M = M / M.sum(axis=1)
    return M


def SimRank(G, c=0.8, num_iterations=10, weight=None):
        """Predict using SimRank; taken from: https://github.com/rafguns/linkpred/blob/master/linkpred/network/algorithms.py
        .. math ::
            sim(u, v) = \frac{c}{|N(u)| \cdot |N(v)|} \sum_{p \in N(u)}
                        \sum_{q \in N(v)} sim(p, q)
        where 'N(v)' is the set of neighbours of node 'v'.
        Parameters
        ----------
        c : float, optional
            decay factor, determines how quickly similarity decreases
        num_iterations : int, optional
            number of iterations to calculate
        weight: string or None, optional
            If None, all edge weights are considered equal.
            Otherwise holds the name of the edge attribute used as weight.
        """
        #set-up inital variables
        res = {}
        nodelist = G.nodes()
        ineligible = G.edges()
        n = len(G)
        M = raw_google_matrix(G, nodelist=nodelist, weight=weight)
        sim = np.identity(n, dtype=np.float32)

        for i in range(num_iterations):
            temp = c * M.T * sim * M
            sim = temp + np.identity(n) - np.diag(np.diag(temp))

        (m, n) = sim.shape
        assert m == n

        for i in range(m):
            # sim(a, b) = sim(b, a), leading to a 'mirrored' matrix.
            # We start the column range at i + 1, such that we only look at the
            # upper triangle in the matrix, excluding the diagonal:
            # sim(a, a) = 1.
            u = nodelist[i]
            for j in range(i + 1, n):
                if sim[i, j] > 0:
                    v = nodelist[j]
                    if (u, v) not in ineligible:
                        res[(u, v)] = 0.0
                        res[(u, v)] = sim[i, j]
        return res


def RPR(G, alpha=0.15, beta=0):
    """Return the rooted PageRank of all nodes with respect to node 'root'
    taken from: https://github.com/rafguns/linkpred/blob/master/linkpred/network/algorithms.py
    Parameters
    ----------
    G : a networkx.(Di)Graph
        network to compute PR on
    root : a node from the network
        the node that will be the starting point of all random walks
    alpha : float
        PageRank probability that we will advance to a neighbour of the
        current node in a random walk
    beta : float or int
        Normally, we return to the root node with probability 1 - alpha.
        With this parameter, we can also advance to a random other node in the
        network with probability beta. Thus, we get back to the root node with
        probability 1 - alpha - beta. This is off (0) by default.
    weight : string or None
        The edge attribute that holds the numerical value used for
        the edge weight.  If None then treat as unweighted.
    """
    #set default variables
    weight = None
    res = {} #stores results
    eligible_node = G.nodes()
    personalization = dict.fromkeys(G, beta)

    for u in G.nodes():
        personalization[u] = 1 - beta
        pagerank_scores = nx.pagerank_scipy(G, alpha, personalization, weight=weight)

        for v, w in six.iteritems(pagerank_scores):
            if w > 0 and u != v and v in eligible_node:
                res[(u, v)] = 0.0
                res[(u, v)] += w

    return res


# def simrank(G, c=0.8, num_iterations= 10):
#     r"""Calculate SimRank matrix for nodes in nodelist; taken from: https://github.com/rafguns/linkpred/blob/master/linkpred/network/algorithms.py
#     SimRank is defined as:
#     .. math ::
#         sim(u, v) = \frac{c}{|N(u)| |N(v)|} \sum_{p \in N(u)}
#                     \sum_{q \in N(v)} sim(p, q)
#     Parameters
#     ----------
#     G : a networkx.Graph
#         network
#     nodelist : collection of nodes, optional
#         nodes to calculate SimRank for (default: all)
#     c : float, optional
#         decay factor, determines how quickly similarity decreases
#     num_iterations : int, optional
#         number of iterations to calculate
#     weight: string or None, optional
#         If None, all edge weights are considered equal.
#         Otherwise holds the name of the edge attribute used as weight.
#     """
#     labels = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute='names')  # stores the node label
#
#     nodelist = None
#     weight = None
#     n = len(labels)
#     M = raw_google_matrix(labels, nodelist=nodelist, weight=weight)
#     sim = np.identity(n, dtype=np.float32)
#     for i in range(num_iterations):
#         temp = c * M.T * sim * M
#         sim = temp + np.identity(n) - np.diag(np.diag(temp))
#
#     sim_res = nx.from_numpy_matrix(sim)
#     sim_res = nx.Graph(sim_res)
#     sim_res.remove_edges_from(sim_res.selfloop_edges())
#
#     #save edges to dictionary
#     sim_edges = {}
#     for edge in sim_res.edges(data=True):
#         node0 = labels.node[edge[0]]['names']
#         node1 = labels.node[edge[1]]['names']
#         sim_edges[(node0, node1)] = edge[2]['weight']
#
#     return sim_edges
