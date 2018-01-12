####################################################################
# NetworkStatistics.py
# Purpose: script explores different characteristics of a newtork
# version 1.1.0
# date: 07.21.2017
####################################################################


# import module/script dependencies
import networkx as nx
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from pylab import show
from powerlaw import plot_pdf, Fit, pdf
import powerlaw



# produce network statistics
# read in graphs
trem_owl = nx.read_gml('Network_Data/Trametinib_query_OWL_network.gml')
trem_nets = nx.read_gml('Network_Data/Trametinib_query_NETS_network.gml')
ddi_owl = nx.read_gml('Network_Data/DDI_reactome_query_OWL_network.gml')
ddi_nets=nx.read_gml('Network_Data/DDI_reactome_query_NETS_network.gml')

len(list(nx.non_edges(ddi_nets.to_undirected())))


count = set
for node in trem_nets.nodes(data=True):




nx.number_connected_components(ddi_owl.to_undirected())

## Descriptives

for i in [ddi_nets, ddi_owl]:
    print 'Clustering Coefficient'
    print nx.average_clustering(i.to_undirected())

    print 'Number of Connected Components'
    print nx.number_connected_components(i.to_undirected())

    print 'Average Network Closeness (Centrality)'
    print sum(nx.closeness_centrality(i.to_undirected()).values())/len(nx.closeness_centrality(i.to_undirected()).values())

    print 'degree heterogeneity'
    print float(np.mean(map(lambda x: x ** 2, i.to_undirected().degree().values()))) / (
    (i.to_undirected().number_of_edges() * 2 /i.to_undirected().number_of_nodes()) ** 2)

    print 'Average number of neighbors'
    print sum(nx.average_neighbor_degree(i.to_undirected()).values())

    print 'Nodes'
    print nx.number_of_nodes(i.to_undirected())

    print 'edges'
    print nx.number_of_edges(i.to_undirected())

    print 'Density'
    print nx.density(trem_nets.to_undirected())

    print 'Number of cliques'
    print len(nx.number_of_cliques(i.to_undirected()))

    print 'Average Degree'
    print 2.0 * (len(i.to_undirected().edges())) / len(i.to_undirected().nodes())

    print 'Average Degree Assortativity'
    print nx.degree_assortativity_coefficient(i.to_undirected())

# things for only connected graphs
ddi = max(nx.connected_component_subgraphs(ddi_nets.to_undirected()), key=len)
print 'Network Diameter'
nx.diameter(ddi.to_undirected())

print 'Shorest paths (sum)'
sum(nx.all_pairs_shortest_path_length(ddi_owl.to_undirected()).values()[0].values())

print 'Average shortest_path (Characteristic path length)'
nx.average_shortest_path_length(ddi_owl.to_undirected())

ddi_owl_nodes = ddi_owl.nodes()
## CCDF with power-law fit
trem_owl_freq = Counter(nx.degree(trem_owl.to_undirected()).values()).values()
trem_nets_freq = Counter(nx.degree(trem_nets.to_undirected()).values()).values()
ddi_owl_freq = np.sort(Counter(list(nx.degree(ddi_owl.to_undirected()).values())).values())
ddi_nets_freq = np.sort(Counter(list(nx.degree(ddi_nets.to_undirected()).values())).values())


nx.degree(trem_owl.to_undirected()).values()

fit1 = powerlaw.Fit(nx.degree(trem_owl.to_undirected()).values(), discrete = True)
fit2 = powerlaw.Fit(nx.degree(trem_nets.to_undirected()).values(), discrete = True)

fit1 = powerlaw.Fit(nx.degree(ddi_owl.to_undirected()).values(), discrete = True)
fit2 = powerlaw.Fit(nx.degree(ddi_nets.to_undirected()).values(), discrete = True)

fig2 = fit1.plot_ccdf(color='mediumaquamarine', linewidth=2)
fit1.power_law.plot_ccdf(color='mediumaquamarine', linestyle='--', ax=fig2)
fit2.plot_ccdf(color='m', linewidth=2, ax=fig2)
fit2.power_law.plot_ccdf(color='m', linestyle='--', ax=fig2)

fig2.legend(['OWL CCDF',
             'OWL CCDF Power-Law Fit',
             'OWL-NETS CCDF',
             'OWL-NETS CCDF Power-Law Fit'],loc='lower left', fontsize=14, numpoints=1)
#
# from mpl_toolkits.axes_grid.inset_locator import inset_axes
# fig2in = inset_axes(fig2, width="30%", height="30%", loc=3)
# fig2in.hist(nx.degree(ddi_owl).values(), bins = 5000, normed = True, color='deepskyblue')
# fig2in.set_xlim(0, 100)
#
# fig2in.hist(nx.degree(ddi_nets).values(), bins = 50, normed = True, color='red', alpha = 0.65)
# # fig2in.set_xlim(0, 0.1)
# fig2in.set_xticks([])
# fig2in.set_yticks([])

fig2.patch.set_facecolor('whitesmoke')
fig2.set_xlabel(r'Degree $k$', fontsize=16)
fig2.set_ylabel(r'$P(K \geq k)$', fontsize=16)
fig2.grid(True, color='black')
fig2.tick_params(axis='both', which='major', labelsize=14)
fig2.tick_params(axis='both', which='minor', labelsize=14)
# plt.ylim(0.01, 1.01)
# plt.xlim(0.98, 31622)
plt.tight_layout()
plt.savefig("Results/DDI_reactome/DDI_degreeDistribution.png", dpi=600)  # save plot



# create degree distribution plots
plot_res = []
for r in [trem_owl, trem_nets, ddi_owl, ddi_nets]:
    # #get counts of node occurrence in target list
    degree = Counter(list(nx.degree(r.to_undirected()).values())).values()  # for r = 1

    # update indegree to include a value of zero for nodes not in target list
    pdf = np.sort(degree)
    cdf = np.arange(len(pdf)) / float(len(pdf))
    ccdf = 1 - cdf
    plot_res.append([pdf, ccdf])

# generate plot
plt1, = plt.loglog(plot_res[2][0], plot_res[2][1], '.', color='turquoise', markersize=12, alpha=0.75)
plt2, = plt.loglog(plot_res[0][0], plot_res[0][1], '.', color='turquoise', markersize=12, alpha=0.75)
plt3, = plt.loglog(plot_res[3][0], plot_res[3][1], '.', color='red', markersize=12, alpha=0.75)
plt4, = plt.loglog(plot_res[1][0], plot_res[1][1], '.', color='lime', markersize=12)


plt.legend([plt1, plt3], ['OWL Representation', 'OWL-NETS'],
           loc='upper right', fontsize=12, numpoints=1)

plt.legend([plt2, plt4], ['OWL Representation', 'OWL-NETS'],
           loc='upper right', fontsize=12, numpoints=1)

plt.xlabel(r'Degree $k$', fontsize=12)
plt.ylabel(r'$Pr(k)$', fontsize=12)
plt.grid(True, color='black')
plt.ylim(0.01, 1.01)
plt.xlim(0.98, 31622)
plt.tight_layout()
plt.savefig("Network_visualizations/Tram_degreeDistribution.png", dpi=600)  # save plot
# save plot


## Betweenness

def most_important(G):
    '''
    returns a copy of G with the most important nodes according to the pagerank
    '''
    ranking = nx.betweenness_centrality(G).items()
    print ranking

    r = [x[1] for x in ranking]
    m = sum(r) / len(r)  # mean centrality
    t = m * 3  #threshold
    Gt = G.copy()

    # threshold, we keep only the nodes with 3 times the mean
    for k, v in ranking:
        if v < t:
            Gt.remove_node(k)

    return Gt

G = graph.to_undirected()
G=owl.to_undirected()
Gt = most_important(G) # trimming

Gt.nodes(data = True)

# create the layout
pos = nx.spring_layout(G)
# draw the nodes and the edges (all)
nx.draw_networkx_nodes(G,pos,node_color='b',alpha=0.3,node_size=50)
nx.draw_networkx_edges(G,pos,alpha=0.1)

# draw the most important nodes with a different style
nx.draw_networkx_nodes(Gt,pos,node_color='r',alpha=0.4,node_size=200)


# also the labels this time
labels = nx.get_node_attributes(Gt, 'type')
nx.draw_networkx_labels(Gt,pos,labels,font_size=5,font_color='black')
plt.axis('off')
plt.tight_layout()
plt.savefig("Network_visualizations/Trem_betweeness_importance_NETS.png", dpi=1000)

res = []
count1 = 0
count2 = 0
count3 = 0
count4 = 0
for i in ddi.to_undirected().edges(data =True):
    if i[2]['nice'] == ['drug1_ice', 'target_ice']:
        count1 += 1

    if i[2]['nice'] == ['pathway_target_ice', 'drug2_ice']:
        count2 += 1

    if i[2]['nice'] == ['target_ice', 'pathway_ice']:
        count3 += 1

    if i[2]['nice'] == ['pathway_ice', 'pathway_target_ice']:
        count4 += 1




if __name__ == '__main__':
    main()