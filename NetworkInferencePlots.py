##############################################################################################
# NetworkInferencePlots.py
# Purpose: script generates AUC plots to compare performance of network inference algorithms
# version 1.0.8
# date: 01.28.2017
##############################################################################################


# import module/script dependencies
import json
import numpy as np
import matplotlib.pyplot as plt



def ResultParser(file):
    '''
    Function takes as input a file that stores a list of lists (length of steps) and outputs a list of the average AUC
    and precision values across n steps.
    :param file: string storing the json file containing link prediction results
    :return: list storing the average AUC values across n steps
    '''

    auc_results = []; prec_results = []; auc = []; prec = []; auc_mod = []

    # open the json file
    with open(file) as json_data:
        results = json.load(json_data)

    for i in results:
        if len(i) == 2:
            auc_results.append(i[0])
            auc = [np.mean(x) for x in auc_results]
            prec_results.append(i[1])
            prec = [np.mean(x) for x in prec_results]
        else:
            auc_results.append(i)
            auc = [np.mean(x) for x in auc_results]

    for j in auc:
        if j < 0.5:
            auc_mod.append(1 - j)
        else:
            auc_mod.append(j)

    return auc_mod, prec



def ResultPlotter(steps, data, xlabel, ylabel, title, output):
    '''
    Function takes a list of data, plotting parameters and plots the data. The plot is saved according to the file
    directory specified by the user.
    :param steps: list storing the x-axis values
    :param data: list of lists of AUC scores for plotting
    :param xlabel: string storing x-axis label
    :param ylabel: string storing y-axis label
    :param title: string storing plot title
    :param output: string storing information for saving plot
    :return: plot is created and written to user-specified location
    '''

    plt1, = plt.plot(steps, data[0], color = 'purple', marker = '>', linestyle = ':', linewidth=2)
    plt2, = plt.plot(steps, data[1], color = 'magenta', marker = 's', linestyle = ':',linewidth=2)
    plt3, = plt.plot(steps, data[2], color = 'forestgreen', marker = 'o', linestyle = ':',linewidth=2)
    plt4, = plt.plot(steps, data[3], color = 'orange', marker = 'd', linestyle = ':',linewidth=2)
    plt5, = plt.plot(steps, data[4], color = 'gold', marker = '*', linestyle = ':',linewidth=2)
    plt6, = plt.plot(steps, data[5], color = 'slategray', marker = '>', linestyle = ':',linewidth=2)
    plt7, = plt.plot(steps, data[6], color = 'limegreen', marker = 's', linestyle = ':',linewidth=2)
    plt8, = plt.plot(steps, data[7], color = 'cyan', marker = 'd', linestyle = ':',linewidth=2)
    plt9, = plt.plot(steps, data[8], color = 'red', marker = '*', linestyle = ':',linewidth=2)
    plt10, = plt.plot(steps, data[9], color = 'royalblue', marker = '>', linestyle = ':',linewidth=2)
    # plt11, = plt.plot(steps, data[10], color='orange', marker='o', linestyle=':', linewidth=2)

    hline = plt.axhline(y=0.5, xmax=1, linestyle ='--', color='black')
    # plt.legend([plt1, plt2, plt3, plt4, plt5, plt6, plt7, plt8, plt9, plt10, hline],
    #            ['Degree Product', 'Common Neighbors', 'Shortest Path', 'Jaccard Index', 'Sorenson Similarity',
    #             'Leicht-Holme-Newman', 'Adamic Advar', 'Resource Allocation', 'Katz', 'Rooted Page Rank',
    #             'Pure Chance'], loc='upper center', prop={'size': 10}, ncol=3)


    plt.legend([plt1, plt2, plt3, plt4, plt5, plt6, plt7, plt8, plt9, plt10, hline], ['Degree Product', 'Common Neighbors', 'Shortest Path', 'Jaccard Index', 'Sorenson Similarity', 'Leicht-Holme-Newman', 'Adamic Advar', 'Resource Allocation', 'Katz', 'Rooted Page Rank', 'Pure Chance'],loc=9,prop={'size': 9}, bbox_to_anchor=(0.5, -0.15), ncol=3)

    plt.subplots_adjust(bottom=0.25)
    #plt.tight_layout(pad=6.5)
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.grid(True, color ='black')
    plt.title(title, fontsize=18)
    plt.ylim(0.45, 1.0)
    plt.yticks(fontsize=12)
    plt.yticks(fontsize=12)

    return plt.savefig(output, dpi=600) #save plot



def main():
    #load results and format for plotting
    file = 'Results/Trametinib/OWL_Tram'
    dp_res = ResultParser(str(file) + '_DP.json')
    sp_res = ResultParser(str(file) + '_SP.json')
    cn_res = ResultParser(str(file) + '_CN.json')
    j_res = ResultParser(str(file) + '_J.json')
    ss_res = ResultParser(str(file) + '_SS.json')
    lhn_res = ResultParser(str(file) + '_LHN.json')
    aa_res = ResultParser(str(file) + '_AA.json')
    ra_res = ResultParser(str(file) + '_RA.json')
    k_res = ResultParser(str(file) + '_K.json')
    # s_res = ResultParser(str(file) + '_SR.json')
    rpr_res = ResultParser(str(file) + '_RPR.json')
    # hrg_resa = ResultParser('Results/Trematinib/nice_trem_HRG_AUC.json')
    # hrg_resp = ResultParser2('Results/Trematinib/nice_trem_HRG_PREC.json')

    #plot results
    data = [dp_res[0], cn_res[0], sp_res[0], j_res[0], ss_res[0], lhn_res[0], aa_res[0], ra_res[0], k_res[0], rpr_res[0]]
    steps = [0.05, 0.1, 0.3, 0.5, 0.7, 0.9, 0.95]
    ResultPlotter(steps, data, 'Fraction of Observed Edges', 'Average  AUC', '', 'Results/Trametinib/AUCplot_OWL.png')


if __name__ == '__main__':
    main()