##########################################################
# NETSRepresentation.py
# Purpose: script creates an OWL-NETS graph and metadata
# version 1.1.3
# date: 07.21.2017
##########################################################


## import module/script dependencies
from datetime import datetime
import json
import networkx as nx
import os
from progressbar import ProgressBar, FormatLabel, Percentage, Bar
import simplejson as json
import re
import QueryParser
import QueryRunner



def GraphMaker(triples):
    '''
    Function takes a list of lists, where each list is a triple from a SPARQL query and creates an directed graphical
    representation where nodes are subjects/objects of the triple and edges are the labeled predicates that connect the
    subjects and objects. The function returns the graph.
    :param triples - list of lists, where each list is a triple from a SPARQL query
    :return: a directed graphical representation where nodes are subjects/objects of the triple and edges are the
    labeled predicates
    '''

    graph = nx.DiGraph()

    for triple in triples:

        # to account for instances of an object that is also a string (e.g., "Breast Cancer)
        if len(triple.split(' ')) != 3:
            graph.add_edge(str(triple.split(' ')[0]),
                           ' '.join(triple.split(' ')[2:]),
                           predicate=str(triple.split(' ')[1]))

        else:
            graph.add_edge(str(triple.split(' ')[0]),
                           str(triple.split(' ')[2]),
                           predicate=str(triple.split(' ')[1]))

    # CHECK: ensure the graph contains only 1 connected component
    if nx.number_connected_components(graph.to_undirected()) != 1:
        print 'ERROR: graph contains more than a single component'
    else:
        # CHECK: verify the number of edges in graph is correct
        if len(triples) != len(graph.edges()):
            raise ValueError('Number of Triples and Number of Graph Edges is Different')
        else:
            return graph


def NETSNodeFinder(graph):
    '''
    Function takes a graph and performs certain checks to identify the NETS BIO and Label nodes. Function returns a
    list of NETS nodes (node representing biological entity).
    :param graph: a directed graphical representation where nodes are subjects/objects of the triple and edges are the
        labeled predicates
    :return: a list of NETS nodes
    '''

    node_info = []

    for (i, j) in graph.edges():
        if "IAO_0000219" in graph[i][j]['predicate']:
            in_nodes = [x for x in graph.in_edges(j) if "IAO_0000219" in graph[x[0]][x[1]]['predicate']]
            out_nodes = [x for x in graph.out_edges(j) if "IAO_0000219" in graph[x[0]][x[1]]['predicate']]

            if not out_nodes:
                if len(in_nodes) != 1:
                    raise ValueError('Node has more than 1 incoming edge')

                else:
                    node_info.append(in_nodes[0][1])

        # For endpoints using only RDF - ways to extend/modify the original code
        if graph[i][j]['predicate'] == 'rdfs:label':
            node_info.append(i)

        if graph[i][j]['predicate'] == 'dcterms:title':
            node_info.append(i)

    return list(node_info)


def NETSEdgeFinder(NETS_nodes, graph):
    '''
    Function takes a list of NETS nodes and a directed graph as input and calculates shortest path length for all
    pairwise node comparisons. The Function returns a list of NETS edge lists where edges represent the pairs of NETS
    nodes separated by the shortest path length. Order of of edges in list does not imply a biological relationship.
    :param NETS_nodes: a list of NETS nodes
    :param graph: a directed graphical representation where nodes are subjects/objects of the triple and edges are the
        labeled predicates
    :return: list of lists where edges represent the pairs of NETS nodes separated by the shortest path length
    '''
    order = []

    # while this approach is guaranteed to work it is redundant and could be improved
    for i in range(len(NETS_nodes)):
        shortest_paths = []
        objects = []
        subject = []

        for j in range(len(NETS_nodes)):
            objects.append(NETS_nodes[j])
            subject = NETS_nodes[i]

            # shortest path length on undirected version of graph
            path_length = nx.shortest_path_length(graph.to_undirected(),
                                                  source=NETS_nodes[i],
                                                  target=NETS_nodes[j])
            shortest_paths.append(path_length)

        # determine minimum length - not including 0 (0 represents the distance between a node and itself)
        edge = [[subject, objects[x]] for x, v in enumerate(shortest_paths) if
                v == min([i for i in shortest_paths if i != 0])]
        order += [y for y in edge if y not in order and y[::-1] not in order]

    return order


def Direction(sub_graph, restrictions, edges):
    '''
    Function takes a directed graph, a list of restrictions, and an edge. With this information the function identifies
    which node in restriction list is closest to the restriction. This information is needed for determining edge
    directionality.
    :param sub_graph: sub-graph of nodes with out degree > 0 (except for NETS nodes)
    :param restrictions: list of nodes
    :param edges: list of edges
    :return: set of tuples where order of items in tuples specifies edge directionality
    '''

    edge_direction = set()

    # return node that is pointed to
    for rest in set(restrictions):
        path_end = [node for node in edges if nx.has_path(sub_graph, rest, node)]

        if len(path_end) < 2:
            edge_direction.add(tuple(list(set(edges) - set(path_end)) + path_end))
        else:
            edge_direction.add(tuple(path_end))

    return edge_direction


def EdgeDirection(graph, sub_graph, NETS_edges):
    '''
    Function takes the directed full and sub-graphs as well as a list of NETS edges and returns a list of lists where
    each list is an and edge and the order of the nodes in each edge indicates the direction of the relationship between
    the nodes. The direction is determined by first finding the shortest path between the two NETS edges using the
    undirected sub-graph. Each node laying on the shortest path is evaluated and those nodes with an out edge of type
    'rdf_type' that points to an object of 'owl:Restriction' are selected. The NETS node in the path (pointed to by) the
    selected node is the object making the other node (the node that cannot be connected to the selected node by a
    directed path) is the subject.
    :param graph: a directed graphical representation where nodes are subjects/objects of the triple and edges are the
    labeled predicates
    :param sub_graph: sub-graph of nodes with out degree > 0 (except for NETS nodes)
    :param NETS_edges: NETS_edges: list of lists where edges represent the pairs of NETS nodes separated by the shortest
    path length
    :return:
    '''

    edge_direction = set()

    for edges in NETS_edges:
        out_edges = []
        restrictions = []

        for node in nx.shortest_path(sub_graph.to_undirected(), edges[0], edges[1]):

            # check if the node has out_edges
            out_edges += [node for node in graph.out_edges(node) if graph.out_edges(node)]

            # identify restriction nodes among node switch out edges
            restrictions += [edge[0] for edge in out_edges if
                             graph[edge[0]][edge[1]]['predicate'] == 'rdf:type' and edge[1] == 'owl:Restriction']

            edge_direction |= Direction(sub_graph, restrictions, edges)

    return list(edge_direction)


def MetadataDetails(sub_graph, graph, edges):
    '''
    Function takes a graph, a sub-graph of nodes with out degree > 0 (except for NETS nodes) and a list of NETS nodes
    for a single NETS edge and returns a list of lists where list[0] is a list of NETS metadata nodes, list[1] is a set
    of nodes needed for labeling the NETS edge.
    :param sub_graph: sub-graph of nodes with out degree > 0 (except for NETS nodes)
    :param graph: a directed graphical representation where nodes are subjects/objects of the triple and edges are the
        labeled predicates
    :param edges: list of NETS nodes for a single NETS edge
    :return: list of lists where list[0] is a list of NETS metadata nodes, list[1] is a set of nodes needed for labeling
    the NETS edge
    '''
    metadata = []
    restrictions = []

    # get node laying on shortest path between NETS nodes
    for node in nx.shortest_path(sub_graph.to_undirected(), edges[0], edges[1])[1:-1]:

        # get non-NETS nodes with no out degree - restrictions or ontology terms
        for edge in graph.edges(node):
            metadata.append(tuple([edge[0], graph[edge[0]][edge[1]]['predicate'], edge[1]]))

            # labeling primary restriction between NETS nodes
            if edge[1] not in edges:
                restrictions.append(edge)

    return metadata, restrictions


def EdgeLabelFinder(restrictions):
    '''
    Function takes a list of restrictions that connect two NETS nodes and a directed graph and identifies the primary
    restriction triple that connects two NETS nodes. The function returns a list representing the subject-predicate-
    object assertion needed to return a label for the restriction triple that acts as an edge connecting the NETS nodes.
    :param restrictions: list of restriction triples laying on the shortest path between two NETS nodes
    :return: a list representing the subject-predicate-object needed to return a label for the restriction triple
    laying on the shortest path between two NETS nodes
    '''

    # separate triple into subject and object lists
    subj, obj = map(list, zip(*restrictions))

    # concepts from ccp ontology - 'ccp_obo_ext:GO_MI_EXT_binding_or_direct_interaction'
    if [i for i, s in enumerate(obj) if s.startswith('ccp')]:
        nodes = [[subj[i], obj[i]] for i, s in enumerate(obj) if s.startswith('ccp')][0]
        return [str(nodes[1]), 'rdfs:label',
                '?' + str(nodes[1].replace(':', '_').strip('?')) + '_Name']
                # str(nodes[0]) + '_' + str(nodes[1].replace(':', '_').strip('?')) + '_Name']

    # concepts from obo ontology - 'obo:RO_0000057'
    if [i for i, s in enumerate(obj) if s.startswith('obo')]:
        nodes = [[subj[i], obj[i]] for i, s in enumerate(obj) if s.startswith('obo')][0]
        return [str(nodes[1]), 'rdfs:label',
                '?' + str(nodes[1].replace(':', '_').strip('?')) + '_Name']
                # str(nodes[0]) + '_' + str(nodes[1].replace(':', '_').strip('?')) + '_Name']

    # special database identifiers - 'iaodrugbank:DrugInteraction_drugbankIdDataField1' (will be removed)
    if 'schema' in '|'.join(obj).lower():
        nodes = [[subj[i], obj[i]] for i, s in enumerate(obj) if 'schema' in s.lower()][0]
        return [str(nodes[1]), 'rdfs:label',
                '?' + str(nodes[1].replace(':', '_').strip('?')) + '_Name']
                # str(nodes[0]) + '_' + str(nodes[1].replace(':', '_').strip('?')) + '_Name']


def ListInsert(graph, metadata):
    '''
    Function takes a list of tuples (all triples comprising shortest path between two NETS nodes) and a list of out
    edges for each NETS node in an edge. The function returns a list of tuples containing all triples except those
    used to retrieve NETS nodes identifiers or labels.
    :param graph: a directed graphical representation where nodes are subjects/objects of the triple and edges are the
    labeled predicates
    :param metadata:list of tuples (all triples comprising shortest path between two NETS nodes)
    :return: a list of tuples sorted in ascending order
    '''
    # finds nodes on path between NETS nodes subclasses
    triple_path = []

    for edge in metadata:
        for part in graph.out_edges(edge[2]):
            preds = [x for x in nx.single_source_shortest_path(graph, (part[1])).values() if len(x) != 1]

            if preds:
                triple_path += [tuple([x[0], graph[x[0]][x[1]]['predicate'], x[1]]) for x in preds]

            else:
                triple_path.append(tuple([part[0], graph[part[0]][part[1]]['predicate'], part[1]]))

    return sorted(list(set(metadata + triple_path)))


def EdgeMetadata(graph, sub_graph, NETS_edges):
    '''
    Function takes a directed graph and sub-graph and list of NETS nodes as arguments. Using the full graph edge list
    and the sub-graph of nodes with out degree > 0 (except for NETS nodes) and returns two dictionaries keyed by NETS
    nodes edges. The first dictionary contains the labels for the primary restriction connecting the NETS nodes. The
    second dictionary contains the shortest path connecting the NETS_nodes (all nodes except the NETS nodes). If edge
    relation between NETS nodes is an identifier then a IAO:denotes relation can be inserted to reconnect the NETS node
    to the path. If the edge relation is anything else a subclassOf relation can reconnect the NETS node to the path.
    :param graph: a directed graphical representation where nodes are subjects/objects of the triple and edges are the
        labeled predicates
    :param sub_graph: sub-graph of nodes with out degree > 0 (except for NETS nodes)
    :param NETS_edges: list of lists where edges represent the pairs of NETS nodes separated by the shortest path length
    :return: two dictionaries: The first dictionary contains the labels for the primary restriction connecting the NETS
    nodes. The second dictionary contains the shortest path connecting the NETS_nodes (all nodes except the NETS nodes).
    '''
    edge_label = {}
    edge_metadata = {}

    # identify abstraction edges and create new triples for accessing label
    for edges in NETS_edges:

        edge_info = MetadataDetails(sub_graph, graph, edges)

        # gets nodes connecting nodes in an edges
        metadata = edge_info[0]

        # gets information to label edge
        restrictions = edge_info[1]

        edge_label[tuple(edges)] = EdgeLabelFinder(restrictions)
        edge_metadata[tuple(edges)] = [ListInsert(graph, metadata)]

    return edge_label, edge_metadata


def NodeDic(results, edge_info, node_info):
    '''
    Function takes the results of running a query, NETS edge label information, and a list of node information (list[0]
    contains the NETS nodes label triples, list[1] contains the contains the NETS nodes identifier triples). The
    function returns a list of dictionaries where list[0] contains a nested dictionary where keys are bio entity
    identifiers and the values are the the human readable labels and database identifiers; list[1] contains a dictionary
    where the bio node is the key and the value is a set of possible NETS node types for that node.
    :param results: json file containing the query results from endpoint
    :param edge_info: dictionary where the keys are the NETS edges and the values are the edge labels
    :param node_info: a list of node information (list[0] contains the NETS nodes label triples, list[1] contains the
    contains the NETS nodes identifier triples)
    :return: a list of dictionaries: list[0] contains a nested dictionary where keys are bio entity identifiers and the
    values are the the human readable labels and database identifiers; list[1] contains a dictionary where the bio node is
    the key and the value is a set of possible NETS node types for that node
    '''

    print 'Start building OWL-NETs metadata dictionary'

    # creates a map to store NETS node type information
    node_type = {}

    # creates a map to identify which query variables represent the BIO world ID, label, and ICE ID
    node_labeler = {}

    # assign variables needed for node dictionary
    NETS = set([x.strip('?') for y in edge_info[0].keys() for x in y])
    labels = [[re.sub('[?|"\n"]', '', x.split(' ')[0]), re.sub('[?|"\n"]', '', x.split(' ')[2])] for x in node_info[0]]
    ids = [[x.split(' ')[0].strip('?'), x.split(' ')[2].strip('?')] for x in node_info[1]]

    # initialize progress bar progress bar
    widgets = [Percentage(), Bar(), FormatLabel('(elapsed: %(elapsed)s)')]
    pbar = ProgressBar(widgets=widgets, maxval=len(NETS))

    for node in pbar(NETS):
        node_labeler[node] = {}

        for res in results['results']['bindings']:
            node_key = str(res[node]['value'])
            label_value = str([x[1] for x in labels if x[0] == node][0].encode('utf8'))
            id_value = str([x[0] for x in ids if x[1] == node][0].encode('utf8'))

            # NODE TYPE: setting node type information
            if node_key in node_type.keys():
                node_type[node_key].add(node)

            else:
                node_type[node_key] = set()
                node_type[node_key].add(node)

            # NODE METADATA: setting node attributes by NETS node type
            if node_key in node_labeler[node].keys():
                # order matters - not using a set so that each ICE can be mapped to the label with the same index
                node_labeler[node][node_key]['label'].append(res[label_value]['value'].encode('utf8'))
                node_labeler[node][node_key]['id'].append(res[id_value]['value'].encode('utf8'))

            else:
                node_labeler[node][node_key] = {}
                node_labeler[node][node_key]['label'] = [res[label_value]['value'].encode('utf8')]
                node_labeler[node][node_key]['id'] = [res[id_value]['value'].encode('utf8')]

    # close progress bar
    pbar.finish()
    print 'Finished building OWL-NETs metadata dictionary'
    print '\n'

    # CHECK: verify that the counts are correct
    for node in NETS:
        res_count = set()
        for res in results['results']['bindings']:
            res_count.add(res[node]['value'])

        if len(node_labeler[node].keys()) != len(res_count):  # verify the number of nodes in graph is correct
            raise ValueError('The count of results for the ' + str(node) + ' NETS node in the node dictionary differ '
                                                                           'from the query output')

    return node_labeler, node_type


def DictCleaner(dic, label, identifier):
    '''
    Function removes redundancy from a dictionary's values represented as lists. The function checks the contents
    of two lists and removes redundancy while maintaining the corresponding order of items in each list. For example,
    a = [1,2,2,3,4,2]; b = [a,b,b,c,d,b] would be altered to a = [1,2,3,4]; b = [a,b,c,d].
    :param dic: a nested dictionary where keys are bio entity identifiers and the values are the the human readable
    labels
    and database identifiers
    :param label: list of bio entity label identifiers from dictionary
    :param identifier: list of database identifiers from dictionary
    :return: the input dictionary without redundancy
    '''
    # remove duplicates for label or ICE that are all the same
    for key, value in dic.iteritems():
        for i in value:
            updated = sorted(set(zip(dic[key][i][label], dic[key][i][identifier])))

            # CHECK - verify that the process worked correctly
            if len(updated) != (len([list(t) for t in zip(*updated)][0]) and len([list(t) for t in zip(*updated)][1])):
                raise ValueError('Duplicate removal failed')

            dic[key][i][label] = [list(t) for t in zip(*updated)][0]
            dic[key][i][identifier] = [list(t) for t in zip(*updated)][1]

    return dic


def EdgeDic(edge_info):
    '''
    Function takes the NETS edge labeling information as inputs and creates a dictionary of results. The key of the
    dictionary is a NETS edge and the values are the  bio entity identifiers and the values are the the human readable
    labels.
    :param edge_info: dictionary where the keys are the NETS edges and the values are the edge labels
    :return: a dictionary is a NETS edge and the values are the  bio entity identifiers and the values are the the
    human readable labels
    '''
    # create a dictionary storing the
    edge_labeler = {}

    for key, value in edge_info.items():
        edge_labeler[key] = {}
        edge_labeler[key]['id'] = value[0]
        edge_labeler[key]['label'] = value[2]

    return edge_labeler


def NETSGraph(results, NETS_edges, node_labeler, node_type, edge_labeler):
    '''
    Function takes a json file of query results, a list of NETS edges, node and edge metadata dictionaries, and a
    dictionary containing NETS edge information by BIO node. Using these items the function creates the directed
    OWL-NETS abstraction network. Node metadata includes: labels (a list of human readable labels); id (the endpoint
    database identifiers); and bio (the NETS node type). Edge metadata includes: labels (human readable label for the
    edge between two NETS nodes) and id (the ontology concept term used to link the NETS nodes).
    :param results: json file containing the query results from endpoint
    :param NETS_edges: list of lists, where each list is a NETS edge and the order specifies a directional relationship
    :param node_labeler: node metadata nested lists (list[0] contains the NETS nodes label triples, list[1] contains the
    contains the NETS nodes identifier triples)
    :param node_type: dictionary with BIO node as key and set of NETS node types as value
    :param edge_labeler: dictionary where the keys are the NETS edges and the values are the edge labels
    :return: OWL-NETS directed graph
    '''
    print 'Started building OWL-NETS graph'

    # initialize progress bar progress bar
    widgets = [Percentage(), Bar(), FormatLabel('(elapsed: %(elapsed)s)')]
    pbar = ProgressBar(widgets=widgets, maxval=len(results['results']['bindings']))

    NETS_graph = nx.DiGraph()

    for res in pbar(results['results']['bindings']):
        for edge in NETS_edges:

            i = res[str(edge[0].strip('?').encode('utf8'))]['value'].encode('utf8')
            j = res[str(edge[1].strip('?').encode('utf8'))]['value'].encode('utf8')

            # set nodes
            NETS_graph.add_node(min(node_labeler[edge[0].strip('?')][i]['label'], key=len),
                                labels=node_labeler[edge[0].strip('?')][i]['label'],
                                id=node_labeler[edge[0].strip('?')][i]['id'],
                                bio=i,
                                type='-'.join(list(node_type[i])))

            # gets second node in edge
            NETS_graph.add_node(min(node_labeler[edge[1].strip('?')][j]['label'], key=len),
                                labels=node_labeler[edge[1].strip('?')][j]['label'],
                                id=node_labeler[edge[1].strip('?')][j]['id'],
                                bio=j,
                                type='-'.join(list(node_type[j])))
            # add edge
            NETS_graph.add_edge(min(node_labeler[edge[0].strip('?')][i]['label'], key=len),
                                min(node_labeler[edge[1].strip('?')][j]['label'], key=len),
                                labels=res[(edge_labeler[tuple(edge)]['label']).strip('?')]['value'].encode('utf8'),
                                id=(edge_labeler[tuple(edge)]['id']).strip('?'),
                                edge='-'.join([edge[0].strip('?'), edge[1].strip('?')]))


    # closes first progress bar
    pbar.finish()
    print 'Finished building OWL-NETS graph'
    print '\n'

    # print information about graph
    print 'Directed OWL-NETS Graph has ' + str(len(NETS_graph.nodes())) + ' nodes, ' + str(
        len(NETS_graph.edges())) + ' edges, and ' + str(
        nx.number_connected_components(NETS_graph.to_undirected())) + ' connected component(s)'

    return NETS_graph


def GraphJson(graph, edge_labels, output):
    '''
    Function writes a Networkx graph to a Json file. Within this file there are two keys. The first key "metadata",
    stores the metadata for each edge that is needed to transform back to the original OWL representation. The second
    key "network", stores the nodes and edges of the OWL-NET.
    :param graph: OWL-NETS undirected graph
    :param edge_labels: dictionary containing the shortest path connecting the NETS nodes within each NETS edge (all
    nodes except the NETS nodes)
    :param output: file path and name where to store Json file output
    :return: json file storing the graph and associated edge metadata
    '''

    return json.dump(dict(metadata=dict((', '.join(u), v) for (u, v) in edge_labels.items()),
                          network=dict(nodes=[[n, graph.node[n]] for n in graph.nodes()],
                                       edges=[[u, v, graph.edge[u][v]] for u, v in graph.edges()])),
                     open(output, 'w'))



def NETSNetworkBuilder(input1):
    '''
    Function takes several strings as arguments from the user and with them generates and NETS abstraction network with
    edge metadata.
    :param input1: string containing file path/name for SPARQL query
    '''

    print str('Started building OWL-NETS Abstraction Network: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print '\n'

    # parse query and return triples
    query_text = QueryParser.QueryParser(input1)

    # create a graph representation of query
    graph = GraphMaker(query_text[0])

    ## NETS NODES
    # will return a list of NETS nodes
    NETS_nodes = NETSNodeFinder(graph)

    ## NETS EDGES
    # create sub-graph from graph with NETS_nodes and nodes with out degree > 0
    keep = [node for node in graph.nodes() if graph.out_degree(node) > 0 or node in NETS_nodes]
    sub_graph = graph.subgraph(keep)

    # get NETS edges and maintains order specified in query
    NETS_edges = NETSEdgeFinder(NETS_nodes, sub_graph)

    # get direction of NETS edges
    NETS_edge_order = EdgeDirection(graph, sub_graph, NETS_edges)

    # get edge metadata
    NETS_edge_metadata = EdgeMetadata(graph, sub_graph, NETS_edge_order)

    # update query text
    updated_query_text = QueryParser.NETSQueryParser(query_text, NETS_nodes, NETS_edge_metadata)

    for x in updated_query_text[0].split('\n'):
        print x

    ## QUERY ENDPOINT
    # authentication file (format: url, user, password) - should be placed in same user directory as query
    authentication = 'SPARQL_Queries/authentication'

    # look to see if results already exist (if OWL-NETS was previously run)
    if str(input1.split('/')[-1]) + '_results.json' in os.listdir(''.join(str(input1.split('/')[-2]) + '/')):

        print 'Using existing query results'
        print '\n'

        with open(input1.rpartition(".")[-1] + "_results.json") as json_data:
            results = json.load(json_data)
    else:
        print 'Generating new query results'
        print '\n'

        # run query
        results = QueryRunner.RunQuery(updated_query_text[0], authentication)

        # export results to json file
        with open(str(input1.rpartition(".")[-1] + "_results.json"), 'w') as outfile:
            json.dump(results, outfile)

    ## NETWORK POPULATION
    # get and set node metadata
    node_info = NodeDic(results, NETS_edge_metadata, updated_query_text[1:])

    # organize output for labeling edges
    edge_data = EdgeDic(NETS_edge_metadata[0])

    # build NETS graph
    NETS_graph = NETSGraph(results, NETS_edge_order, DictCleaner(node_info[0], 'id', 'label'), node_info[1], edge_data)

    # write graphs to gml and JSON files
    nx.write_gml(NETS_graph, str(input1.rpartition(".")[-1] + "_NETS") + '_network.gml')
    GraphJson(NETS_graph, NETS_edge_metadata[1], str(input1.rpartition(".")[-1] + "_NETS") + '_network.json')

    print str(
        'Finished building OWL-NETS Representation network: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n'