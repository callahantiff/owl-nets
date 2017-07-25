#######################################
# OWLRepresentation.py
# Purpose: script creates an OWL graph
# version 1.2.0
# date: 07.17.2017
########################################


## import module/script dependencies
from datetime import datetime
import json
import networkx as nx
import os
from progressbar import ProgressBar, FormatLabel, Percentage, Bar
import QueryParser
import NETSRepresentation
import QueryRunner



def OWLGraph(results, updated_query_text):
    '''
    Function takes query results (JSON format) and a list of lists, where list[0] contains query select statement and
    list[1] contains query body and creates a graph where each subject and object in the triple are the nodes and the
    edges represents the predicates connecting these nodes. Each edge has an edge attribute that contains the triple
    :param results: json file containing the query results from endpoint
    :param triples: list of lists, where list[0] contains query select statement and list[1] contains query body
    :return: OWL representation as a directed graph object
    '''
    print 'Started building OWL representation graph'

    # initialize progress bar progress bar
    widgets = [Percentage(), Bar(), FormatLabel('(elapsed: %(elapsed)s)')]
    pbar = ProgressBar(widgets=widgets, maxval=len(results['results']['bindings']))

    # re-format variables
    select = [x.split('?')[-1].strip(')') if x.startswith('(') else x.strip('?') for x in updated_query_text[0]]

    # creates an empty directed graph
    graph = nx.DiGraph()

    for res in pbar(results['results']['bindings']):

        for row in updated_query_text[1]:
            row0 = [row[0].split(':')[1].strip('?') if ':' in row[0] else row[0]][0].strip('?')
            row2 = [row[2].split(':')[1].strip('?') if ':' in row[2] else row[2]][0].strip('?')

            # add nodes
            graph.add_node(str(res[row0]['value'].encode('utf8')), type=row0)
            graph.add_node(str(res[row2]['value'].encode('utf8')), type=row2)

            # add edges
            graph.add_edge(str(res[row0]['value'].encode('utf8')),
                           str(res[row2]['value'].encode('utf8')),
                           predicate = str(row[1].encode('utf8')),
                           triple='-'.join([str(x.encode('utf8')) for x in row]))

    # close progress bar
    pbar.finish()
    print 'Finished building OWL representation graph'
    print '\n'

    # CHECK - verify we have included all of the nodes
    graph_res = []
    for res in results['results']['bindings']:
        for node in res.keys():
            if node in select:
                node = str(res[node]['value'].encode('utf8'))
                graph_res.append(node)

    if set(graph_res) != set(graph.nodes()):
        raise ValueError('Number of graph nodes do not match json results')

    else:
        # print information about graph
        print 'Directed OWL graph has ' + str(len(graph.nodes())) + ' nodes, ' + str(len(graph.edges())) + ' edges, and ' + str(
            nx.number_connected_components(graph.to_undirected())) + ' connected components'

        return graph


def OWLNetworkBuilder(input1):
    '''
    Function takes several strings as arguments from the user and with them generates an OWL representation network.
    :param input1: string containing file path/name for SPARQL query
    '''

    print str('Started building OWL Representation Network: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # parse query and return triples
    query_text = QueryParser.QueryParser(input1)

    # create a graph representation of query
    graph = NETSRepresentation.GraphMaker(query_text[0])

    ## NETS NODES
    # will return a list of NETS nodes
    NETS_nodes = NETSRepresentation.NETSNodeFinder(graph)

    ## NETS EDGES
    # create sub-graph from graph with NETS_nodes and nodes with out degree > 0
    keep = [node for node in graph.nodes() if graph.out_degree(node) > 0 or node in NETS_nodes]
    sub_graph = graph.subgraph(keep)

    # get NETS edges and maintains order specified in query
    NETS_edges = NETSRepresentation.NETSEdgeFinder(NETS_nodes, sub_graph)

    # get edge metadata
    NETS_edge_metadata = NETSRepresentation.EdgeMetadata(graph, sub_graph, NETS_edges)

    # update query text
    updated_query_text = QueryParser.NETSQueryParser(query_text, NETS_nodes, NETS_edge_metadata)

    ## QUERY ENDPOINT
    # authentication file (format: url, user, password) - should be placed in same user directory as query
    authentication = 'SPARQL_Queries/authentication'

    # look to see if results already exist (if OWL-NETS was previously run)
    if str(input1.split('/')[-1]) + '_results.json' in os.listdir(''.join(str(input1.split('/')[-2]) + '/')):
        print 'Using existing query results'
        with open(input1.rpartition(".")[-1] + "_results.json") as json_data:
            results = json.load(json_data)
    else:
        print 'Generating new query results'

        # run query
        results = QueryRunner.RunQuery(updated_query_text[0], authentication)

        # export results to json file
        with open(str(input1.rpartition(".")[-1] + "_results.json") + '_results.json', 'w') as outfile:
            json.dump(results, outfile)

    # with open('Query_Data/DDI_reactome_query_results.json') as json_data:
    #     results = json.load(json_data)

    ## NETWORK POPULATION
    OWL_graph = OWLGraph(results, updated_query_text[3:])

    # write graphs to gml and JSON files
    # input2 = 'Network_Data/Angiogenesis_query_OWL'
    # nx.write_gml(OWL_graph, str(input2) + '_network.gml')
    nx.write_gml(OWL_graph, str(input1.rpartition(".")[-1] + "_OWL") + '_network.gml')

    print str('Finished building OWL Representation network: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n'