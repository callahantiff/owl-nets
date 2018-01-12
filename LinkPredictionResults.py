#######################################################################################################
# LinkPredictionResults.py
# Purpose: script runs 10 link prediction algorithms on training and testing network data in parallel
# version 1.2.0
# date: 01.28.2017
#######################################################################################################


# import module/script dependencies
import networkx as nx
import numpy as np
from collections import Counter
import operator
import LinkPrediction
import csv


def LabelDict(results, id, var):
    '''
    Function takes a json file of results (containing ice ids and labels) and two variables storing the id and labels
    and returns a dictionary where the keys are the id and the values are the corresponding labels.
    :param results: json file of ice ids and labels
    :param id: variable storing ids
    :param var: variable storing labels
    :return:
    '''

    label_dict = {}

    for res in results['results']['bindings']:
        label_dict[str(res[str(id)]['value'].split('/')[-1]).encode('utf8')] = str(
            res[str(var)]['value'].encode('utf8'))

    return label_dict


def EdgeChecker(scores, edges):
    '''
    Function takes a dictionary of edges (keys) and scores (values) and a list of edges. Using the intersection of the
    edges and keys edges a new dictionary is created.
    :param scores: dictionary of edges (keys) and scores (values)
    :param edges: list of tuples
    :return: dictionary of tuples (keys) and scores (values)
    '''
    final_dict = {}

    for edge in set(edges).intersection(set(scores.keys())):
        final_dict[edge] = scores[edge]

    return final_dict



def main():

    #read in graphs
    owl_graph = nx.read_gml('Network_Data/Trametinib_query_OWL_network.gml').to_undirected()
    nets_graph = nx.read_gml('Network_Data/Trametinib_query_NETS_network.gml').to_undirected()
    mid_graph = nx.read_gml('Network_Data/Trametinib_query_PART_network').to_undirected()

    #run link predictions for each graph
    nets_scores = LinkPrediction.katz(nets_graph, beta=0.001, max_power=5, weight=None, dtype=None)
    nets_nonexist = list(nx.non_edges(nets_graph))
    nets_preds = EdgeChecker(nets_scores, nets_nonexist)

    owl_nonexist = list(nx.non_edges(owl_graph))
    owl_scores = LinkPrediction.RPR(owl_graph, alpha = 0.15, beta = 0)
    owl_preds = EdgeChecker(owl_scores, owl_nonexist)

    #explore predictions
    len(nets_preds) #1652
    np.min(nets_preds.values())
    np.mean(nets_preds.values())
    np.max(nets_preds.values())

    #print top 20 edges
    sorted(Counter(sorted(nets_preds.values())).items(), key=lambda i: i[0]) #get distribution of counts
    sorted_scores = sorted(owl_preds.items(), key=operator.itemgetter(1), reverse=True) #biggest first
    sorted_scores = sorted(nets_preds.items(), key=operator.itemgetter(1), reverse=False) #smallest first

    #investigate the top n items
    edges = sorted_scores[0:20]


    ## Write results for use with with ranking methods

    # graphs
    graph = nx.read_gml('Network_Data/Trametinib_query_OWL_network.gml').to_undirected()

    # graph = nx.read_gml('Network_Data/Trametinib_query_NETS_network.gml').to_undirected()

    graph = nx.read_gml('Network_Data/DDI_reactome_query_NETS_network.gml').to_undirected()


    methods = [LinkPrediction.DegreeProduct(graph, list(nx.non_edges(graph))),
               LinkPrediction.ShortestPath(graph, list(nx.non_edges(graph))),
               LinkPrediction.CommonNeighbors(graph, list(nx.non_edges(graph))),
               LinkPrediction.AdamicAdvar(graph, list(nx.non_edges(graph))),
               LinkPrediction.Jaccard(graph, list(nx.non_edges(graph))),
               LinkPrediction.LHN(graph, list(nx.non_edges(graph))),
               LinkPrediction.ResourceAllocation(graph, list(nx.non_edges(graph))),
               LinkPrediction.Sorensen(graph, list(nx.non_edges(graph))),
               LinkPrediction.katz(graph, beta=0.001, max_power=5, weight=None, dtype=None),
               LinkPrediction.RPR(graph, alpha = 0.15, beta = 0)]


    # method counter for labeling csv files
    count = 0

    for method in methods:
        updated_res = EdgeChecker(method, list(nx.non_edges(graph)))

        with open('Results/DDI_reactome/NETS_DDI ' + str(count) + '.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for key, values in updated_res.items():
                writer.writerow([key, values])

        count += 1




if __name__ == '__main__':
    main()