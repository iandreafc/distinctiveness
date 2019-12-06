import networkx as nx
import numpy as np


def d_preprocess(G):
    
    #Make an independent copy of the graph
    G = G.copy()
    
    #Check Graph Type
    #Currently only undirected graphs are accepted
    
    #Remove Loops
    if list(G.selfloop_edges()):
        print("WARNING: Loops will be ignored.")
        G.remove_edges_from(G.selfloop_edges())
    
    #Check if all existing arcs have weights, otherwise assign value of 1
    #Also removes negative weights
    for u,v,data in G.edges(data=True):
        if not 'weight' in data or data['weight'] <= 0:
            data['weight'] = 1
    
    #Sum weights of all arcs
    totalWEI = 0
    for u,v,data in G.edges(data=True):
        totalWEI += data['weight']
    
    n1 = nx.number_of_nodes(G) - 1
    
    #Calculates degree and weighted degree
    deg = dict(nx.degree(G))
    wei_deg = dict(nx.degree(G, weight ="weight"))
    
    
    return G, n1, deg, wei_deg, totalWEI


#G is a 
def d_all (G, normalize = False):
    
    G, n1, deg, wei_deg, totalWEI = d_preprocess(G)
    
    #Computes Distinctiveness Centrality, all 5 metrics
    distinctiveness = {}
    for u,v,data in G.edges(data=True):    
        d1u = data['weight'] * np.log10(n1/deg[v])
        d1v = data['weight'] * np.log10(n1/deg[u])
        d2u = 1 * np.log10(n1/deg[v])
        d2v = 1 * np.log10(n1/deg[u])
        d3u = data['weight'] * np.log10(totalWEI/(wei_deg[v] - data['weight'] + 1))
        d3v = data['weight'] * np.log10(totalWEI/(wei_deg[u] - data['weight'] + 1))
        d4u = data['weight'] * (data['weight'] / wei_deg[v])
        d4v = data['weight'] * (data['weight'] / wei_deg[u])
        d5u = 1* (1 / deg[v])
        d5v = 1* (1 / deg[u])
        try:
            distinctiveness[u] = [x + y for x, y in zip(distinctiveness[u], [d1u,d2u,d3u,d4u,d5u])]
        except:
            distinctiveness[u] = [d1u,d2u,d3u,d4u,d5u]
        try: 
            distinctiveness[v] = [x + y for x, y in zip(distinctiveness[v], [d1v,d2v,d3v,d4v,d5v])]
        except:
            distinctiveness[v] = [d1v,d2v,d3v,d4v,d5v]

    for isolate in list(nx.isolates(G)):
        distinctiveness[isolate] = [0,0,0,0,0]
    
    d1 = {k:v[0] for k,v in distinctiveness.items()}
    d2 = {k:v[1] for k,v in distinctiveness.items()}
    d3 = {k:v[2] for k,v in distinctiveness.items()}
    d4 = {k:v[3] for k,v in distinctiveness.items()}
    d5 = {k:v[4] for k,v in distinctiveness.items()}
    
    return d1,d2,d3,d4,d5