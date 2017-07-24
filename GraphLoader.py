#######################################################################################
## QueryParser.py
## Purpose: script extracts a graph with corresponding edge metadata from a json file
## version 1.0.0
## date: 07.17.2017
#######################################################################################


## import module/script dependencies
import json
from networkx import nx


def LoadGraph(location):
    '''
    Function reads in a Json file containing a graph and associated edge metadata and returns a Networkx directed
    graph and a dictionary containing the associated edge metadata.
    :param location: path and file name where json file is stored
    :return: the function outputs a list of lists where list[0] "metadata" contains a dictionary where the keys are
    the NETS edges and te values are the associated metadata needed to recreate the original OWL representation and
    list[1] contains an directed OWL-NET graph
    '''

    graph = nx.DiGraph()
    data = json.load(open(location))
    edge_metadata = data['metadata']
    graph.add_nodes_from(data['network']['nodes'])
    graph.add_edges_from(data['network']['edges'])

    return edge_metadata, graph