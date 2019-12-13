import networkx as nx
import numpy as np


def g_preprocess(G, alpha = 1):
    
    #Make an independent copy of the graph
    G = G.copy()
    
    #From multigraph to graph
    if type(G) == nx.MultiGraph:
        print("MultiGraph converted to Graph")
        G1 = nx.Graph()
        for u,v,data in G.edges(data=True):
            w = data['weight'] if 'weight' in data else 1.0
            if G1.has_edge(u,v):
                G1[u][v]['weight'] += w
            else:
                G1.add_edge(u, v, weight=w)
        G = G1.copy()
    elif type(G) == nx.MultiDiGraph:
        print("MultiDiGraph converted to DiGraph")
        G1 = nx.DiGraph()
        for u,v,data in G.edges(data=True):
            w = data['weight'] if 'weight' in data else 1.0
            if G1.has_edge(u,v):
                G1[u][v]['weight'] += w
            else:
                G1.add_edge(u, v, weight=w)
        G = G1.copy()
    
    #Remove Loops
    loops = list(nx.selfloop_edges(G))
    if loops:
        print("WARNING: Loops will be ignored.")
        G.remove_edges_from(loops)
    
    #Check if all existing arcs have weights, otherwise assign value of 1
    #Also set negative weights to 1
    negwarn = False
    for u,v,data in G.edges(data=True):
        if not 'weight' in data:
            data['weight'] = 1
        elif data['weight'] < 0:
            negwarn = True
    if negwarn == True:
        print("WARNING: graph contained arcs with negative weights, whose weight was changed to 1")
    
    #Sum weights of all arcs
    totalWEI = 0
    for u,v,data in G.edges(data=True):
        totalWEI += data['weight']
    
    n1 = nx.number_of_nodes(G) - 1
    
    #Calculates degree and weighted degree
    if type(G) == nx.Graph:
        deg = dict(nx.degree(G))
        indeg = outdeg = wei_indeg_alpha = wei_outdeg_alpha = np.nan
        
        #Calculate weighted degree, taking alpha into account
        wei_deg_alpha = dict(nx.degree(G, weight ="weight"))
        if alpha > 1:
            wei_deg_alpha = {k:v**alpha for k,v in wei_deg_alpha.items()}
            
    elif type(G) == nx.DiGraph:
        deg = wei_deg_alpha = np.nan
        indeg = dict(G.in_degree())
        outdeg = dict(G.out_degree())
        
        wei_indeg_alpha = dict(G.in_degree(weight ="weight"))
        wei_outdeg_alpha = dict(G.out_degree(weight ="weight"))
        if alpha > 1:
            wei_indeg_alpha = {k:v**alpha for k,v in wei_indeg_alpha.items()}
            wei_outdeg_alpha = {k:v**alpha for k,v in wei_outdeg_alpha.items()}
            
        
    #Calculates max arc weight
    maxwij = max(dict(G.edges).items(), key=lambda x: x[1]['weight'])[1]["weight"]
    
    return G, n1, deg, indeg, outdeg, wei_indeg_alpha, wei_outdeg_alpha, wei_deg_alpha, totalWEI, maxwij




def dc_all (G, alpha = 1, normalize = False):
    
    if alpha < 1:
        print("WARNING. Alpha cannot be lower than 1. The value is set to 1.")
        alpha = 1
    
    G, n1, deg, indeg, outdeg, wei_indeg_alpha, wei_outdeg_alpha, wei_deg_alpha, totalWEI, maxwij = g_preprocess(G, alpha = alpha)
    Glist = list(G.nodes)

    #Define max of all metrics
    if normalize == True:
        D1max = np.log10(n1) * n1 * maxwij
        D2max = np.log10(n1) * n1
        D3max = np.log10(maxwij * n1) * maxwij * n1
        D4max = n1 * maxwij
        D5max = n1
    else:
        D1max = D2max = D3max = D4max = D5max = 1
    
    #Computes Distinctiveness Centrality, all 5 metrics
    if type(G) == nx.Graph:
        #Set keys to zero for all nodes (to take isolates into account)
        d1, d2, d3, d4, d5 = dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0)
        d1_in = d2_in = d3_in = d4_in = d5_in = d1_out = d2_out = d3_out = d4_out = d5_out = np.nan
        
        for u,v,data in G.edges(data=True):    
            d1[u] = (data['weight'] * np.log10(n1 / deg[v]**alpha)) / D1max
            d1[v] = (data['weight'] * np.log10(n1 / deg[u]**alpha)) / D1max
            
            d2[u] = (1 * np.log10(n1 / deg[v]**alpha)) / D2max
            d2[v] = (1 * np.log10(n1 / deg[u]**alpha)) / D2max
            
            d3[u] = (data['weight'] * np.log10(totalWEI/(wei_deg_alpha[v] - data['weight']**alpha + 1))) / D3max
            d3[v] = (data['weight'] * np.log10(totalWEI/(wei_deg_alpha[u] - data['weight']**alpha + 1))) / D3max
            
            d4[u] = (data['weight'] * (data['weight']**alpha / wei_deg_alpha[v])) / D4max
            d4[v] = (data['weight'] * (data['weight']**alpha / wei_deg_alpha[u])) / D4max
            
            d5[u] = (1* (1 / deg[v]**alpha)) / D5max
            d5[v] = (1* (1 / deg[u]**alpha)) / D5max
        
    elif type(G) == nx.DiGraph:
        #Set keys to zero for all nodes (to take isolates into account and nodes with zero in- or out-degree)
        d1_in, d2_in, d3_in, d4_in, d5_in, d1_out, d2_out, d3_out, d4_out, d5_out = dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0)
        d1 = d2 = d3 = d4 = d5 = np.nan
        
        for u,v,data in G.edges(data=True):    
            d1_in[v] = (data['weight'] * np.log10(n1 / outdeg[u]**alpha)) / D1max
            d1_out[u] = (data['weight'] * np.log10(n1 / indeg[v]**alpha)) / D1max
            
            d2_in[v] = (1 * np.log10(n1 / outdeg[u]**alpha)) / D2max
            d2_out[u] = (1 * np.log10(n1 / indeg[v]**alpha)) / D2max
            
            d3_in[v] = (data['weight'] * np.log10(totalWEI/(wei_outdeg_alpha[u] - data['weight']**alpha + 1))) / D3max
            d3_out[u] = (data['weight'] * np.log10(totalWEI/(wei_indeg_alpha[v] - data['weight']**alpha + 1))) / D3max
            
            d4_in[v] = (data['weight'] * (data['weight']**alpha / wei_outdeg_alpha[u])) / D4max
            d4_out[u] = (data['weight'] * (data['weight']**alpha / wei_indeg_alpha[v])) / D4max
            
            d5_in[v] = (1* (1 / outdeg[u]**alpha)) / D5max
            d5_out[u] = (1* (1 / indeg[v]**alpha)) / D5max
           
            
    DC = {"D1":d1, "D2":d2, "D3":d3, "D4":d4, "D5":d5,
          "D1_in":d1_in, "D2_in":d2_in, "D3_in":d3_in, "D4_in":d4_in, "D5_in":d5_in,
          "D1_out":d1_out, "D2_out":d2_out, "D3_out":d3_out, "D4_out":d4_out, "D5_out":d5_out}
    
    return DC