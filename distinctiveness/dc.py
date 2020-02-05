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
    
    #Calculate degree and weighted degree, taking alpha into account
    if type(G) == nx.Graph:
        deg = dict(nx.degree(G))
        indeg = outdeg = wei_insum_alpha = wei_outsum_alpha = np.nan
        
        #Calculate weighted degree, taking alpha into account
        if alpha != 1:
            wei_sum_alpha = {}
            for node in G.nodes():
                wei_sum_alpha[node] = sum([e[2]["weight"]**alpha for e in list(G.edges(node, data = True))])
        else:
           wei_sum_alpha = dict(nx.degree(G, weight ="weight")) 
            
    elif type(G) == nx.DiGraph:
        deg = wei_sum_alpha = np.nan
        indeg = dict(G.in_degree())
        outdeg = dict(G.out_degree())
        
        if alpha != 1:
            wei_outsum_alpha = {}
            wei_insum_alpha = {}
            for node in G.nodes():
                wei_outsum_alpha[node] = sum([e[2]["weight"]**alpha for e in list(G.out_edges(node, data = True))])
                wei_insum_alpha[node] =  sum([e[2]["weight"]**alpha for e in list(G.in_edges(node, data = True))])
        else:
            wei_insum_alpha = dict(G.in_degree(weight ="weight"))
            wei_outsum_alpha = dict(G.out_degree(weight ="weight"))
            
        
    #Calculate max arc weight
    maxwij = max(dict(G.edges).items(), key=lambda x: x[1]['weight'])[1]["weight"]
    minwij = min(dict(G.edges).items(), key=lambda x: x[1]['weight'])[1]["weight"]
    
    return G, n1, deg, indeg, outdeg, wei_insum_alpha, wei_outsum_alpha, wei_sum_alpha, totalWEI, maxwij, minwij




def dc_all (G, alpha = 1, normalize = False):
    
    if alpha < 1:
        print("WARNING. Alpha should be >= 1, except you exactly know what you are doing.")
        if normalize == True:
            print("For alpha < 1 normalization is not carried out.")
            normalize = False
    
    G, n1, deg, indeg, outdeg, wei_insum_alpha, wei_outsum_alpha, wei_sum_alpha, totalWEI, maxwij, minwij = g_preprocess(G, alpha = alpha)
    Glist = list(G.nodes)

    #Define max of all metrics
    if normalize == True:
        D1max = np.log10(n1) * n1 * maxwij
        D1min = (1-alpha) * maxwij * np.log10(n1) * n1
        
        D2max = np.log10(n1) * n1
        D2min = (1-alpha) * np.log10(n1) * n1
        
        D3max = np.log10(maxwij * (n1+1) * n1 * 0.5) * maxwij * n1  #np.log10(totalWEI) * maxwij * n1     
        D3alpha1 = np.log10(maxwij + ((minwij-1)/(n1-1))) / np.log10(maxwij)
        D3alpha2 = np.log10((n1*(maxwij-1))/(n1-1)) / np.log10(maxwij)
        if alpha > 1 and alpha < D3alpha1:
            D3min = minwij * np.log10((minwij + (n1-1)*maxwij) / ((n1-1) * (maxwij**alpha) +1))
        elif alpha > 1 and alpha > D3alpha2:
            D3min = maxwij * np.log10((maxwij * n1) / ((n1-1) * (maxwij**alpha) +1))
        elif alpha == 1:
            D3min = 0 #isolates
        else: #do no normalize (if not in range)
            print("Normalization of D3 is not carried out, for this value of alpha.")
            D3max = 1
            D3min = 0 
        
        D4max = n1 * maxwij
        D4min = 0
        
        D5max = n1
        D5min = 0 #considers isolates
    else:
        D1max = D2max = D3max = D4max = D5max = 1
        D1min = D2min = D3min = D4min = D5min = 0
    
    #Computes Distinctiveness Centrality, all 5 metrics
    if type(G) == nx.Graph:
        #Set keys to zero for all nodes (to take isolates into account)
        d1, d2, d3, d4, d5 = dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0)
        d1_in = d2_in = d3_in = d4_in = d5_in = d1_out = d2_out = d3_out = d4_out = d5_out = np.nan
        
        for u,v,data in G.edges(data=True):    
            d1[u] += data['weight'] * np.log10(n1 / deg[v]**alpha)
            d1[v] += data['weight'] * np.log10(n1 / deg[u]**alpha)
            
            d2[u] += 1 * np.log10(n1 / deg[v]**alpha)
            d2[v] += 1 * np.log10(n1 / deg[u]**alpha)
            
            d3[u] += data['weight'] * np.log10(totalWEI/(wei_sum_alpha[v] - data['weight']**alpha + 1))
            d3[v] += data['weight'] * np.log10(totalWEI/(wei_sum_alpha[u] - data['weight']**alpha + 1))
            
            d4[u] += data['weight'] * (data['weight']**alpha / wei_sum_alpha[v])
            d4[v] += data['weight'] * (data['weight']**alpha / wei_sum_alpha[u])
            
            d5[u] += 1* (1 / deg[v]**alpha)
            d5[v] += 1* (1 / deg[u]**alpha)
            
        if normalize == True:
            d1 = {k:(v-D1min)/(D1max-D1min) for k,v in d1.items()}
            d2 = {k:(v-D2min)/(D2max-D2min) for k,v in d2.items()}
            d3 = {k:(v-D3min)/(D3max-D3min) for k,v in d3.items()}
            d4 = {k:(v-D4min)/(D4max-D4min) for k,v in d4.items()}
            d5 = {k:(v-D5min)/(D5max-D5min) for k,v in d5.items()}
        
    elif type(G) == nx.DiGraph:
        #Set keys to zero for all nodes (to take isolates into account and nodes with zero in- or out-degree)
        d1_in, d2_in, d3_in, d4_in, d5_in, d1_out, d2_out, d3_out, d4_out, d5_out = dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0), dict.fromkeys(Glist, 0)
        d1 = d2 = d3 = d4 = d5 = np.nan
        
        for u,v,data in G.edges(data=True):    
            d1_in[v] += data['weight'] * np.log10(n1 / outdeg[u]**alpha)
            d1_out[u] += data['weight'] * np.log10(n1 / indeg[v]**alpha)
            
            d2_in[v] += 1 * np.log10(n1 / outdeg[u]**alpha)
            d2_out[u] += 1 * np.log10(n1 / indeg[v]**alpha)
            
            d3_in[v] += data['weight'] * np.log10(totalWEI/(wei_outsum_alpha[u] - data['weight']**alpha + 1))
            d3_out[u] += data['weight'] * np.log10(totalWEI/(wei_insum_alpha[v] - data['weight']**alpha + 1))
            
            d4_in[v] += data['weight'] * (data['weight']**alpha / wei_outsum_alpha[u])
            d4_out[u] += data['weight'] * (data['weight']**alpha / wei_insum_alpha[v])
            
            d5_in[v] += 1* (1 / outdeg[u]**alpha)
            d5_out[u] += 1* (1 / indeg[v]**alpha)
           
        if normalize == True:
            d1_in = {k:(v-D1min)/(D1max-D1min) for k,v in d1_in.items()}
            d2_in = {k:(v-D2min)/(D2max-D2min) for k,v in d2_in.items()}
            d3_in = {k:(v-D3min)/(D3max-D3min) for k,v in d3_in.items()}
            d4_in = {k:(v-D4min)/(D4max-D4min) for k,v in d4_in.items()}
            d5_in = {k:(v-D5min)/(D5max-D5min) for k,v in d5_in.items()}
            
            d1_out = {k:(v-D1min)/(D1max-D1min) for k,v in d1_out.items()}
            d2_out = {k:(v-D2min)/(D2max-D2min) for k,v in d2_out.items()}
            d3_out = {k:(v-D3min)/(D3max-D3min) for k,v in d3_out.items()}
            d4_out = {k:(v-D4min)/(D4max-D4min) for k,v in d4_out.items()}
            d5_out = {k:(v-D5min)/(D5max-D5min) for k,v in d5_out.items()}
            
    DC = {"D1":d1, "D2":d2, "D3":d3, "D4":d4, "D5":d5,
          "D1_in":d1_in, "D2_in":d2_in, "D3_in":d3_in, "D4_in":d4_in, "D5_in":d5_in,
          "D1_out":d1_out, "D2_out":d2_out, "D3_out":d3_out, "D4_out":d4_out, "D5_out":d5_out}
    
    return DC