#######################################################################################################
# NetworkInference.py
# Purpose: script runs 10 link prediction algorithms on training and testing network data in parallel
# version 1.1.0
# date: 01.28.2017
#######################################################################################################


# import module/script dependencies
import multiprocessing
from datetime import datetime
from functools import partial
import networkx as nx
import random
import json
import EvaluationMetrics
import LinkPrediction



def GraphMaker(graph, percent):
    '''
    Function takes a Networkx graph object and percent of edges to sample. The function creates a training graph by
    randomly sampling a certain percent of edges to remove from the full graph. The percent of randomly sampled edges
    is stored as a list.
    :param graph: networkx graph object
    :param percent: an integer of edges to sample
    :return: training_graph - network graph with randomly sampled edges removed; testing_edges - list of randomly
    sampled edges
    '''

    training = set(random.sample(graph.edges(), int(nx.number_of_edges(graph) * percent)))
    testing_edges = set(set(graph.edges()) - training)

    if len(training) + len(testing_edges) != len(graph.edges()): #verify that training graph/testing edges are correct
        raise ValueError('# of training + testing edges != total # of edges in graph')

    # training graph
    training_graph = nx.Graph()

    # original graph nodes
    training_graph.add_nodes_from(graph.nodes())

    # add training edges between nodes
    training_graph.add_edges_from(training)

    if len(training_graph.nodes()) != len(graph.nodes()): #verify training graph contains original graph
        raise ValueError('Training graph does not contain all of the original graph nodes')

    return training_graph, testing_edges


def DPFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Degree Product scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        missing_scores = LinkPrediction.DegreeProduct(training_graph, testing_edges)
        nonexist_scores = LinkPrediction.DegreeProduct(training_graph, nonexist_edges)

        #get AUC
        auc_round = EvaluationMetrics.AUC(nonexist_scores, missing_scores)
        auc.append(auc_round)

        #precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, dict(missing_scores, **nonexist_scores), testing_edges)
        prec.append(prec_round)

    return auc, prec


def SPFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Shortest Path scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        missing_scores = LinkPrediction.ShortestPath(training_graph, testing_edges)
        nonexist_scores = LinkPrediction.ShortestPath(training_graph, nonexist_edges)

        #get AUC
        auc_round = EvaluationMetrics.AUC(nonexist_scores, missing_scores)
        auc.append(auc_round)

        #precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, dict(missing_scores, **nonexist_scores), testing_edges)
        prec.append(prec_round)

    return auc, prec


def CNFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Common Neighbors scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        missing_scores = LinkPrediction.CommonNeighbors(training_graph, testing_edges)
        nonexist_scores = LinkPrediction.CommonNeighbors(training_graph, nonexist_edges)

        #get AUC
        auc_round = EvaluationMetrics.AUC(nonexist_scores, missing_scores)
        auc.append(auc_round)

        #precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, dict(missing_scores, **nonexist_scores), testing_edges)
        prec.append(prec_round)

    return auc, prec


def JFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Jaccard scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        missing_scores = LinkPrediction.Jaccard(training_graph, testing_edges)
        nonexist_scores = LinkPrediction.Jaccard(training_graph, nonexist_edges)

        #get AUC
        auc_round = EvaluationMetrics.AUC(nonexist_scores, missing_scores)
        auc.append(auc_round)

        #precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, dict(missing_scores, **nonexist_scores), testing_edges)
        prec.append(prec_round)

    return auc, prec


def SSFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Sorenson Similarity scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        missing_scores = LinkPrediction.Sorensen(training_graph, testing_edges)
        nonexist_scores = LinkPrediction.Sorensen(training_graph, nonexist_edges)

        #get AUC
        auc_round = EvaluationMetrics.AUC(nonexist_scores, missing_scores)
        auc.append(auc_round)

        #precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, dict(missing_scores, **nonexist_scores), testing_edges)
        prec.append(prec_round)

    return auc, prec


def LHNFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Leicht-Holme-Newman scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        missing_scores = LinkPrediction.LHN(training_graph, testing_edges)
        nonexist_scores = LinkPrediction.LHN(training_graph, nonexist_edges)

        #get AUC
        auc_round = EvaluationMetrics.AUC(nonexist_scores, missing_scores)
        auc.append(auc_round)

        #precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, dict(missing_scores, **nonexist_scores), testing_edges)
        prec.append(prec_round)

    return auc, prec


def AAFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Adamic Advar scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        missing_scores = LinkPrediction.AdamicAdar(training_graph, testing_edges)
        nonexist_scores = LinkPrediction.AdamicAdar(training_graph, nonexist_edges)
        #get AUC
        auc_round = EvaluationMetrics.AUC(nonexist_scores, missing_scores)
        auc.append(auc_round)

        #precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, dict(missing_scores, **nonexist_scores), testing_edges)
        prec.append(prec_round)

    return auc, prec


def RAFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Resource Allocaiton scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        missing_scores = LinkPrediction.ResourceAllocation(training_graph, testing_edges)
        nonexist_scores = LinkPrediction.ResourceAllocation(training_graph, nonexist_edges)

        #get AUC
        auc_round = EvaluationMetrics.AUC(nonexist_scores, missing_scores)
        auc.append(auc_round)

        #precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, dict(missing_scores, **nonexist_scores), testing_edges)
        prec.append(prec_round)

    return auc, prec


def KFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Katz scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []
    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        scores = LinkPrediction.katz(training_graph, beta=0.001, max_power=5, weight=None, dtype=None)

        #get AUC
        count = 0.0
        for i in xrange(1000):
            TN = random.sample(nonexist_edges, 1)[0]
            TP = random.sample(testing_edges, 1)[0]

            if (TN[0], TN[1]) in scores.keys():
                TN_val = scores[(TN[0], TN[1])]
            else: TN_val = 0.0

            if (TP[0], TP[1]) in scores.keys():
                TP_val = scores[(TP[0], TP[1])]
            else: TP_val = 0.0

            if TP_val > TN_val:
                count += 1.0
            if TP_val == TN_val:
                count += 0.5

        auc_round = count/1000
        auc.append(auc_round)

        #precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, scores, testing_edges)
        prec.append(prec_round)

    return auc, prec


def SFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the SimRank scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''

    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        scores = LinkPrediction.SimRank(training_graph, c=0.8, num_iterations= 10)

        # get AUC
        count = 0.0
        for i in xrange(1000):
            TN = random.sample(nonexist_edges, 1)[0]
            TP = random.sample(testing_edges, 1)[0]

            if (TN[0], TN[1]) in scores.keys():
                TN_val = scores[(TN[0], TN[1])]
            else:
                TN_val = 0.0

            if (TP[0], TP[1]) in scores.keys():
                TP_val = scores[(TP[0], TP[1])]
            else:
                TP_val = 0.0

            if TP_val > TN_val:
                count += 1.0
            if TP_val == TN_val:
                count += 0.5

        auc_round = count/1000
        auc.append(auc_round)

        # precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, scores, testing_edges)
        prec.append(prec_round)

    return auc, prec


def PRFracAUC(network, nonexist_edges, iterations, steps):
    '''
    Function takes a network, list of non-existent edges, the number of iterations, and the percent of edges to sample
    (steps) and runs the Rooted Page Rank scoring function over each sampled network for the specified number of
    iterations.
    :param network: undirected graph
    :param nonexist_edges: list of non-existent edges from the graph
    :param iterations: integer representing the number of iterations to run
    :param steps: list of percent of edges to sample
    :return:
    '''
    auc = []; prec = []

    for j in xrange(iterations):
        iteration_data = GraphMaker(network, steps)
        training_graph = iteration_data[0]
        testing_edges = iteration_data[1]
        scores = LinkPrediction.RPR(training_graph, alpha=0.15, beta=0)

        # get AUC
        count = 0.0
        for i in xrange(1000):
            TN = random.sample(nonexist_edges, 1)[0]
            TP = random.sample(testing_edges, 1)[0]

            if (TN[0], TN[1]) in scores.keys():
                TN_val = scores[(TN[0], TN[1])]
            else:
                TN_val = 0.0

            if (TP[0], TP[1]) in scores.keys():
                TP_val = scores[(TP[0], TP[1])]
            else:
                TP_val = 0.0

            if TP_val > TN_val:
                count += 1.0
            if TP_val == TN_val:
                count += 0.5

        auc_round = count/1000
        auc.append(auc_round)

        # precision - getting top or bottom K links depends on whether or not AUC is >/< 0.5
        prec_round = EvaluationMetrics.KPrecision(auc_round, scores, testing_edges)
        prec.append(prec_round)

    return auc, prec


def main():
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    #specify initial arguments for all functions
    manager = multiprocessing.Manager()
    network = nx.read_gml('Network_Data/Trametinib_query_NETS_network.gml').to_undirected()
    nonexist_edges = manager.list(list(nx.non_edges(network)))
    nonexist_edges = list(nx.non_edges(network))  # non-existent edges in graph
    iterations = 100
    steps = [0.05, 0.1, 0.3, 0.5, 0.7, 0.9, 0.95]
    file = 'Results/Trametinib/NETS_Tram_'

    pool = multiprocessing.Pool(processes=4)  # set up pool

    #Degree Product
    func = partial(DPFracAUC, network, nonexist_edges, iterations)
    DPres = pool.map(func, steps)
    print 'Finished running Degree Product'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #write dictionary to json file
    with open(str(file) + 'DP.json', 'w') as fout:
        json.dump(DPres, fout)

    #Shortest Path
    func2 = partial(SPFracAUC, network, nonexist_edges, iterations)
    SPres = pool.map(func2, steps)
    print 'Finished running Shortest Path'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #write dictionary to json file
    with open(str(file) + 'SP.json', 'w') as fout:
        json.dump(SPres, fout)

    #Common Neighbors
    func3 = partial(CNFracAUC, network, nonexist_edges, iterations)
    CNres = pool.map(func3, steps)
    print 'Finished running Common Neighbors'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #write dictionary to json file
    with open(str(file) + 'CN.json', 'w') as fout:
        json.dump(CNres, fout)

    #Jaccard
    func4 = partial(JFracAUC, network, nonexist_edges, iterations)
    Jres = pool.map(func4, steps)
    print 'Finished running Jaccard Index'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #write dictionary to json file
    with open(str(file) + 'J.json', 'w') as fout:
        json.dump(Jres, fout)

    #Sorensen Similarity
    func5 = partial(SSFracAUC, network, nonexist_edges, iterations)
    SSres = pool.map(func5, steps)
    print 'Finished running Sorensen Similarity'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #write dictionary to json file
    with open(str(file) + 'SS.json', 'w') as fout:
        json.dump(SSres, fout)

    #Leicht-Holme-Newman
    func6 = partial(LHNFracAUC, network, nonexist_edges, iterations)
    LHNres = pool.map(func6, steps)
    print 'Finished running Leicht-Holme-Newman'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #write dictionary to json file
    with open(str(file) + 'LHN.json', 'w') as fout:
        json.dump(LHNres, fout)

    #Adamic Advar
    func7 = partial(AAFracAUC, network, nonexist_edges, iterations)
    AAres = pool.map(func7, steps)
    print 'Finished running Adamic Advar'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #write dictionary to json file
    with open(str(file) + 'AA.json', 'w') as fout:
        json.dump(AAres, fout)

    #Resource Allocation
    func8 = partial(RAFracAUC, network, nonexist_edges, iterations)
    RAres = pool.map(func8, steps)
    print 'Finished running Resource Allocation'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #write dictionary to json file
    with open(str(file) + 'RA.json', 'w') as fout:
        json.dump(RAres, fout)

    #Katz
    func9 = partial(KFracAUC, network, nonexist_edges, iterations)
    Kres = pool.map(func9, steps)
    print 'Finished running Katz'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #write dictionary to json file
    with open(str(file) + 'K.json', 'w') as fout:
        json.dump(Kres, fout)

    # #Simrank
    # func10 = partial(SFracAUC, network, nonexist_edges, iterations)
    # Sres = pool.map(func10, steps)
    # print 'Finished running SimRank'
    # # write dictionary to json file
    # with open(str(file) + 'SR.json', 'w') as fout:
    #     json.dump(Sres, fout)

    # Rooted Page Rank
    func11 = partial(PRFracAUC, network, nonexist_edges, iterations)
    RPRres = pool.map(func11, steps)
    print 'Finished running Rooted Page Rank'
    print str('Started running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # write dictionary to json file
    with open(str(file) + 'RPR.json', 'w') as fout:
        json.dump(RPRres, fout)


    pool.close()
    pool.join()

    print str('Finished running predictions ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    main()
