########################
# QueryRunner.py
# Purpose: script runs SPARQL queries against a user-specified endpoint
# version 1.1.0
# date: 07.23.2017
########################


## import module/script dependencies
# modules
import os
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import urllib2
from datetime import datetime


def Authenticate(input_file):
    '''
    Function takes a string containing a file path to a file containing authentication information and returns a list
    where list[0] is endpoint url, list[1] is username, and list[2] is password. The function checks the input file
    and if it only contains a URL (situations where a username and password are not required) it returns empty strings
    for those fields.
    :param input_file: a string containing a file path to a file containing authentication information
    :return: a list where list[0] is endpoint url, list[1] is usernames, and list[2] is password
    '''
    # CHECK - file has data
    if os.stat(input_file).st_size == 0:
        return 'ERROR: input file: {} is empty'.format(input_file)

    else:
        data = open(input_file).read().split('\n')

        # if no user/pass is needed return them with URL as empty strings
        if len(data) == 1:
            return [data[0], ' ', ' ']

        if len(data) == 3:
            return data


def RunQuery(query_body, input_file):
    '''
    Function takes a string representing the body of a query, and a list of strings needed to authenticate connection
    to knowledge source. Once authenticated, the function runs the query in query_body and returns a JSON
    files containing the query results.
    :param query_body: updated SPARQL query represented as a single string
    :param input_file: a string containing a file path to a file containing authentication information
    :return: a JSON file containing the output of running the query against the endpoint
    '''
    # get authentication information
    authentication = Authenticate(input_file)

    # CHECK: verify provided enpoint credentials
    request = requests.get(authentication[0], auth=(authentication[1], authentication[2]))

    if request.status_code != 200:
        request.raise_for_status()

    else:
        # set-up endpoint proxy
        proxy = urllib2.ProxyHandler()
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

        # connect to knowledge source
        # url to endpoint - 'http://amc-tantor.ucdenver.pvt:10035/repositories/kabob-dev'
        endpoint = SPARQLWrapper(authentication[0])
        endpoint.setCredentials(user = authentication[1], passwd = authentication[2])
        endpoint.setReturnFormat(JSON)  # query output format

        print str('Started running query at: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # run query against KaBOB
        endpoint.setQuery(query_body)
        query_results = endpoint.query().convert()

        print str('Finished running query at: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print '\n'

        # verify that query worked
        if len(query_results['results'].items()) < 1:
            print 'ERROR: query returned no results'
        else:
            return query_results