##########################################################
## QueryParser.py
## Purpose: script parses and converts SPARQL query text
## version 1.2.0
## date: 07.09.2017
##########################################################


## import module/script dependencies
import re
import os



def TripleType(triple_list):
    '''
    Function takes a list of lists, where the inner lists represent a triple. Each potential triple is checked to ensure
    consistent formatting so that each triple contains three variables, separated by a comma. The function returns a
    lists of lists, where the inner lists represent triples with correct formatting.
    :param triple_list: ist of lists, where the inner lists represent a triple
    :return: lists of lists, where the inner lists represent triples with correct formatting
    '''
    triples = []

    for triple in triple_list:

        # singleton - indicates it is the object for the first triple's subject and predicate
        if len(triple) == 1:
            triples.append(triple_list[0][:-1] + triple)

        # pair - indicates that these are the predicate and object of the first triple
        if len(triple) == 2:
            triples.append(triple_list[0][:-2] + triple)

        # complete triple - one containing exactly 3 variables
        if len(triple) == 3:
            if len([x for x in triple if ':' in x or '?' in x]) == 3:
                triples.append(triple)

            # gets at string objects not split (ex. '2')
            elif (':' in triple[0] or '?' in triple[0]) and (':' in triple[1] or '?' in triple[1]):
                triples.append(triple)

            # split string objects (ex. "'breast', 'cancer'")
            else:
                triples.append(triple_list[0][:-2] + [triple[0]] + [' '.join(triple[1:]).replace('"', "")])

    return triples


def QueryTriples(query_body):
    '''
    Function takes a string representing the body of a SPARQL query and depending on the style that the triples are
    written (1 triple per line or shortcuts with ';') the function parses the triples and returns a list of list
    where each inner list represents a triple.
    :param query_body: string representing the body of a SPARQL query
    :return: a list of list where each inner list represents a triple
    '''
    # identify query triples - accounts for two different types of triple formatting
    # format 1 - 1 triple per line
    if ';' not in query_body:
        query_triple = []

        body = filter(None, query_body[re.compile("{").search(query_body).start() + 1:re.compile("}").search(
            query_body).end() - 1]).split('\n')

        triple_list = filter(None, [x.lstrip(' ').split('.')[0] for x in body if not x.lstrip(' ').startswith('#')])

        for triple in triple_list:
            if '(' not in triple:
                query_triple.append(filter(None, triple.rstrip(' ').split(' ')))

        return TripleType(query_triple)

    # format 2 - alternative triple format:
    ## ?gda sio:SIO_000628 ?gene,?disease;
    ## sio:SIO_000216 ?scoreIRI.
    else:
        body = [x for x in filter(None,
                                  query_body[re.compile("{").search(query_body).start() + 1:re.compile("}").search(
                                      query_body).end() - 1].split('.\n'))]
        query_triple = []

        for triples in body:
            items = []

            for triple in filter(None, triples.split('\n')):

                for var in triple.strip(';').split(','):
                    items.append(filter(None, var.split(' ')))

            query_triple += [list(item) for item in set(tuple(row) for row in TripleType(items))]

        return query_triple


def QueryParser(input_file):
    '''
    Function reads a string containing a file path/name, reads contents, and splits the string into different parts
    of a SPARQL query. The query is parsed with each triple appended to a list. The function returns a list of lists
    where the first list is a list of triples and the second list is a list of lists representing the query text.
    :param input_file: string containing the file path/name of SPARQL query
    :return: a list of lists where list[0] is a list of triples, and list[1] is a list of query components
    (i.e., prefixes and query body)
    '''
    # CHECK - file has data
    if os.stat(input_file).st_size == 0:
        return 'ERROR: input file: {} is empty'.format(input_file)

    else:
        # first remove all commented lines (lines starting with '#')
        data = ''.join(filter(None, [row for row in open(input_file).readlines() if not row.lstrip(' ').startswith('#')]))
        query = data.split(re.search(r'\bselect\b', data, re.IGNORECASE).group(0))

        # identify query triples - accounts for two different types of triple formatting
        query_triples = QueryTriples(query[1])

        # construct pieces of query
        query_triples = [' '.join([item for item in row]) for row in query_triples]

        return [query_triples, query]


def QueryFeature(query_body):
    '''
    Function takes the body of a SPARQL query and searches for rows of the query that contain SPARQL features like
    FILTER or OPTION, and returns a string of features, where each feature is separated by a newline.
    :param query_body - query_body: string representing the body of a SPARQL query
    :return: a string of features, where each feature is separated by a newline
    '''
    features = []

    for row in query_body.split('\n'):
        row = row.lstrip(' ')
        if '(' in row and ('ORDER' or 'GROUP') not in row and not row.startswith('?'):

            # replaces newlines and empty white space with an empty string
            line = [re.sub('["\n"]', '', row)]

            for item in line:
                if '#' in item:
                    features.append(item.split('#')[0])
                else:
                    features.append(item)

    return '\n'.join(features)


def QuerySelect(triples):
    '''
    Function takes a list of lists representing triples and formats each item in each triple according the type of
    variable including: resources ("rdf: type"); literals (2, "name"); and variables ('?subject', '?object'). The
    function returns a list of formatted triples.
    :param triples: a list of lists representing triples
    :return: a list of formatted triples
    '''
    select_list = set()

    # create a list of subjects and objects from query
    triples = [x for y in triples for x in set([y.split(' ')[0], y.split(' ')[2]])]

    for item in triples:

        # if a resource (ex - rdf:type)
        if ':' in item:
            select_list.add('(' + str(item) + ' as ?' + str(item.split(':')[1]) + ')')

        # if a literal (ex - 2; "name")
        elif (':' and '?') not in item:
            select_list.add('(' + str(item) + ' as ?' + str(item) + ')')

        # if a variable (ex - ?subject)
        else:
            select_list.add(item)

    return list(select_list)


def OWLGraph(query_body):
    '''
    Function takes a string containing a SPARQL query and reformats the string, removing NETS-specific triples into a
    list of triples needed to create the OWL representation.
    :param query_body: a string containing a SPARQL query
    :return: a list of triples needed to create the OWL representation
    '''

    triples = []
    body = query_body[query_body.index('{'):].split('\n')


    # extract query text from triples
    for x in body:
        if not x.lstrip().startswith('FILTER'):
            if x.lstrip().startswith('OPTIONAL'):
                triples.append(x.lstrip().split('OPTIONAL {')[-1])
            else:
                triples.append(x.lstrip())

    return [x.lstrip().strip('?').split(' ') for x in triples if ('?' in x or ':' in x) and '(' not in x]



def NETSQueryParser(query_text, NETS_nodes, NETS_edge_metadata):
    '''
    Function takes the original SPARQL query text, the list of NETS nodes and edge metadata and updates the original
    SPARQL query text. The function returns a list where list[0] contains a string representing the updated query,
    list[1] contains the NETS node label variables, list[2] contains the NETS node identifier variables, list[3]
    contains the OWL graph select statement information, and list[4] contains the OWL query triples.
    :param query_text: a list of lists where list[0] is the query text to run against KaBOB, list[1] is a list of
    triples, and list[2] is a list of query components (i.e., prefixes, select, and query_features)
    :param NETS_nodes: a list of lists, where each list contains the triple for labeling a single NETS node
    :param NETS_edge_metadata: dictionary keyed by NETS edges, values are triples to label NETS edges
    :return: a list where the first item is a string representing the updated query, the
    second list contains the NETS node label variables, the NETS node identifier variables, OWL graph select statement,
    and the final item is the OWL graph triples.
    '''
    ## PREFIX
    # identify query prefixes
    prefix = [str(x) + '\n' for x in query_text[1][0].split('\n') if re.search(r'\bprefix\b', x, re.IGNORECASE)]

    # features - filter, optional, bind
    features = [str(x) + '\n' for x in QueryFeature(query_text[1][1]).split('\n') if 'bind' not in x.lower()]
    bind = [str(x) + '\n' for x in QueryFeature(query_text[1][1]).split('\n') if 'bind' in x.lower()]

    # identify query limits
    try:
        query_text[1][1].index('LIMIT')
        limit = [query_text[1][1][query_text[1][1].index('LIMIT'):len(query_text[1][1])]]
    except ValueError:
        limit = ['']

    ## QUERY BODY
    # query triples
    triples = [str(x) + ' .\n' for x in query_text[0] if 'rdfs:label' not in x]

    # ids
    id_triple = [x.split('.')[0].rstrip() for x in triples if
                 x.split(' ')[2] in NETS_nodes and 'IAO_0000219' in x.split(' ')[1]]

    # edge label triples - with optional clause
    edge_labels = list(set(['OPTIONAL {' + ' '.join(val) + '} \n' for val in NETS_edge_metadata[0].values()]))

    # get node label triples - with optional clause
    node_labels = list(set([' '.join([str(x), 'rdfs:label', str(x) + '_name ', '.\n']) for
                            y in set(NETS_edge_metadata[0].keys()) for x in y]))

    ## SELECT - start ('SELECT'); end ('WHERE {'); and text (query variables)
    try:
        re.search(r'\bdistinct\b', query_text[1][1], re.IGNORECASE).group(0)
        select_start = ['SELECT DISTINCT']
    except AttributeError:
        select_start = ['SELECT']

    # select text
    # OWL
    select_text_OWL = set(['(' + str(x) + ' as ?'+ str(x.split(':')[1]) + ')' if
                           ':' in x else '(' + str(x) + ' as ?' + str(x) + ')' if
                           ':' not in x and '?' not in x else x
                           for y in [x[::2] for x in [x.split(' ')[0:3] for x in triples]] for x in y])

    # NETS
    select_text = set(['(' + str(x) + ' as ?'+ str(x.split(':')[1]) + ')' if
                           ':' in x else '(' + str(x) + ' as ?' + str(x) + ')' if
                           ':' not in x and '?' not in x else x
                           for y in [x[::2] for x in [x.split(' ')[0:3] for x in triples]] for x in y] +
                       [x[-1] for x in NETS_edge_metadata[0].values()] +
                       [str(x[0]) + '_name' for x in NETS_edge_metadata[0].keys()] +
                       [str(x[1]) + '_name' for x in NETS_edge_metadata[0].keys()])

    select_end = ['WHERE { \n']

    ## COMPLETE QUERY
    # NETS
    full_query = prefix + \
                 select_start + \
                 list(select_text) + \
                 select_end +\
                 bind +\
                 triples + \
                 edge_labels +\
                 node_labels +\
                 features +\
                 [' }\n'] +\
                 limit

    # OWL - this code can be improved in future iterations
    OWL_query = prefix + \
                 select_start + \
                 list(select_text) + \
                 select_end + \
                 bind + \
                 triples + \
                 features + \
                 [' }\n'] + \
                 limit

    return [' '.join(full_query), node_labels, id_triple, select_text_OWL, OWLGraph(' '.join(OWL_query))]