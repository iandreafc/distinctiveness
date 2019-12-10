import networkx as nx
import numpy as np


def d_preprocess(G, alpha = 1):
    
    #Make an independent copy of the graph
    G = G.copy()
    
    #Check Graph Type and Convert MultiGraph to Graph and directed to undirected
    if type(G) == nx.MultiGraph:
        G1 = nx.Graph()
        for u,v,data in G.edges(data=True):
            w = data['weight'] if 'weight' in data else 1.0
            if G1.has_edge(u,v):
                G1[u][v]['weight'] += w
            else:
                G1.add_edge(u, v, weight=w)
        G = G1.copy()
    elif type(G) == nx.MultiDiGraph:
        #Convert to DiGraph
        G1 = nx.DiGraph()
        for u,v,data in G.edges(data=True):
            w = data['weight'] if 'weight' in data else 1.0
            if G1.has_edge(u,v):
                G1[u][v]['weight'] += w
            else:
                G1.add_edge(u, v, weight=w)
        
        #Make undirected
        UG = G1.to_undirected()
        for node in G1:
            for ngbr in nx.neighbors(G1, node):
                if node in nx.neighbors(G1, ngbr):
                    UG.edges[node, ngbr]['weight'] = (G1.edges[node, ngbr]['weight'] + G1.edges[ngbr, node]['weight'])
        G = UG.copy()
    elif type(G) == nx.DiGraph:
        UG = G.to_undirected()
        for node in G:
            for ngbr in nx.neighbors(G, node):
                if node in nx.neighbors(G, ngbr):
                    UG.edges[node, ngbr]['weight'] = (G.edges[node, ngbr]['weight'] + G.edges[ngbr, node]['weight'])
        G = UG.copy()
    
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
    if alpha > 1:
        wei_deg = dict(nx.degree(G, weight ="weight"))
        wei_deg_alpha = {k:v**alpha for k,v in wei_deg.items()}
    else:
        wei_deg_alpha = dict(nx.degree(G, weight ="weight"))
    
    #Calculates max arc weight
    maxwij = max(dict(G.edges).items(), key=lambda x: x[1]['weight'])[1]["weight"]
    
    return G, n1, deg, wei_deg_alpha, totalWEI, maxwij


#G is a 
def d_all (G, alpha = 1, normalize = False):
    
    if alpha < 1:
        print("WARNING. Alpha cannot be lower than 1. The value is set to 1.")
        alpha = 1
    
    G, n1, deg, wei_deg_alpha, totalWEI, maxwij = d_preprocess(G, alpha = alpha)
    
    #Computes Distinctiveness Centrality, all 5 metrics
    distinctiveness = {}
    for u,v,data in G.edges(data=True):    
        d1u = data['weight'] * np.log10(n1/(deg[v])**alpha)
        d1v = data['weight'] * np.log10(n1/(deg[u])**alpha)
        d2u = 1 * np.log10(n1/(deg[v])**alpha)
        d2v = 1 * np.log10(n1/(deg[u])**alpha)
        d3u = data['weight'] * np.log10(totalWEI/(wei_deg_alpha[v] - data['weight'] + 1))
        d3v = data['weight'] * np.log10(totalWEI/(wei_deg_alpha[u] - data['weight'] + 1))
        d4u = data['weight'] * (data['weight'] / wei_deg_alpha[v])
        d4v = data['weight'] * (data['weight'] / wei_deg_alpha[u])
        d5u = 1* (1 / (deg[v])**alpha)
        d5v = 1* (1 / (deg[u])**alpha)
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
    
    if normalize == True:
        D1max = np.log10(n1) * n1 * maxwij
        D2max = np.log10(n1) * n1
        D3max = np.log10(maxwij * n1) * maxwij * n1
        D4max = n1 * maxwij
        D5max = n1
    
    
    
    return d1,d2,d3,d4,d5