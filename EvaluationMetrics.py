#########################################################################################
# EvaluationMetrics.py
# Purpose: script contains methods for evaluating link prediction algorithm performance
# version 1.0
# date: 01.28.2017
#########################################################################################


# import module/script dependencies
import random
import heapq



def AUC(nonexist_scores, missing_scores):
    '''
    Function calculates the probability that a randomly chosen missing link is given a higher score than a randomly
    chosen nonexistent link using procedures described by Lu & Zhou (2010)
    (doi:http://dx.doi.org/10.1016/j.physa.2010.11.027T). The function takes a list containing missing, non-existent
    edges, and predictions, and returns an AUC score. Current method is currently set to perform 1,000 comparisons.
    :param nonexist_scores: list of nonexistent edges and scores
    :param missing_scores: list of test edges and scores
    :return: an integer which is the AUC score for that comparison
    '''

    # comparisons = len(nonexist_scores)*len(missing_scores) #HOW MANY??
    comparisons = 1000
    count = 0.0

    for i in xrange(comparisons):
        TN = random.sample(nonexist_scores.values(), 1)
        TP = random.sample(missing_scores.values(), 1)

        if TP > TN:
            count += 1.0
        if TP == TN:
            count += 0.5

    auc = count/comparisons

    return auc



def KPrecision(auc, scores, testing_edges):
    '''
    Function calculates the ratio of relevant items selected from the top n items using procedures described by Lu &
    Zhou (2010) (doi:http://dx.doi.org/10.1016/j.physa.2010.11.027T). The function takes a list containing missing and
    non-existent edges, the list of all predictions, and returns a top k-precision score for 20% of scores.
    :param auc: integer representing AUC score - to indicate whether the top or bottom of list should be assessed
    :param scores: list of test edges and scores
    :param testing_edges: list of nonexistent edges and scores
    :return: an integer which is the precision for the top number of selected links
    '''

    #get 20% of edges
    links = [int(len(scores)*0.20) if int(len(scores)*0.20) >= 1 else 1][0]

    if auc < 0.5:
        # pred_list = heapq.nsmallest(links, set([x[1] for x in scores.items()])) #returns n highest likelihood scores
        pred_list = heapq.nsmallest(links, scores, key=lambda k: scores[k])
    else:
        # pred_list = heapq.nlargest(links, set([x[1] for x in scores.items()])) #returns n highest likelihood scores
        pred_list = heapq.nlargest(links, scores, key=lambda k: scores[k])

    y_pred = [0 if (i[0], i[1]) in testing_edges else 0 if (i[1], i[0]) in testing_edges else 1 for i in pred_list]

    return float(y_pred.count(0))/links