import networkx as nx
import numpy as np
import pandas as pd


def weisumalpha(G, a):
    if a != 1:
        wei_sum_alpha = {}
        for node in G.nodes():
            wei_sum_alpha[node] = sum(
                [
                    e[2]["weight"] ** a
                    for e in list(G.edges(node, data=True))
                ]
            )
    else:
        wei_sum_alpha = dict(nx.degree(G, weight="weight"))

    return wei_sum_alpha


def weiinoutsumalpha(G, a):
    if a != 1:
        wei_outsum_alpha = {}
        wei_insum_alpha = {}
        for node in G.nodes():
            wei_outsum_alpha[node] = sum(
                [
                    e[2]["weight"] ** a
                    for e in list(G.out_edges(node, data=True))
                ]
            )
            wei_insum_alpha[node] = sum(
                [
                    e[2]["weight"] ** a
                    for e in list(G.in_edges(node, data=True))
                ]
            )
    else:
        wei_insum_alpha = dict(G.in_degree(weight="weight"))
        wei_outsum_alpha = dict(G.out_degree(weight="weight"))
        
    return wei_insum_alpha, wei_outsum_alpha
    

def g_preprocess(G, alpha=1,
                 measures=["D1", "D2", "D3", "D4", "D5"]):

    if isinstance(alpha, list) and len(alpha) == 5:
        alphalist = alpha
    elif isinstance(alpha, (int, float)):
        alphalist = [alpha] * 5
    else:
        print(
            "Error in the choice of alpha. "
            "Please specify a single number or a list of 5 values."
        )
        return (
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        )

    # Make an independent copy of the graph
    G = G.copy()

    if G.number_of_nodes() < 3:
        print("Graph must have at least 3 nodes.")
        return (
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        )

    # From multigraph to graph
    if type(G) == nx.MultiGraph:
        print("MultiGraph converted to Graph")
        G1 = nx.Graph()
        G1.add_nodes_from(G.nodes(data=True))
        for u, v, data in G.edges(data=True):
            w = data["weight"] if "weight" in data else 1.0
            if G1.has_edge(u, v):
                G1[u][v]["weight"] += w
            else:
                G1.add_edge(u, v, weight=w)
        G = G1.copy()
    elif type(G) == nx.MultiDiGraph:
        print("MultiDiGraph converted to DiGraph")
        G1 = nx.DiGraph()
        G1.add_nodes_from(G.nodes(data=True))
        for u, v, data in G.edges(data=True):
            w = data["weight"] if "weight" in data else 1.0
            if G1.has_edge(u, v):
                G1[u][v]["weight"] += w
            else:
                G1.add_edge(u, v, weight=w)
        G = G1.copy()

    # Remove Loops
    loops = nx.selfloop_edges(G)
    if list(loops):
        print("WARNING: Loops will be ignored.")
        G.remove_edges_from(loops)

    # Check if all existing arcs have weights, otherwise assign value of 1
    # Check for negative weights, zero weights and weight lower than 1
    arcweights = [e[2]["weight"] for e in G.edges.data() if "weight" in e[2]]
    numweights = len(arcweights)
    arcweights = set(arcweights)
    if any(w < 1 for w in arcweights):
        print(
            "Graph contains arcs with negative or zero weights,"
            " or weights lower than 1. Weights must be >= 1."
        )
    if numweights != len(G.edges):
        print(
            "WARNING: weights are not specified for all arcs."
            " Each arc must have a weight >= 1.\n"
            "Missing weights are automatically set equal to 1."
        )
        for u, v, data in G.edges(data=True):
            if "weight" not in data:
                data["weight"] = 1

    # Sums the weight of all arcs
    totalWEI = 0
    if "D3" in measures:
        for u, v, data in G.edges(data=True):
            totalWEI += data["weight"]

    n1 = nx.number_of_nodes(G) - 1

    # Calculates degree and weighted degree, taking alpha into account
    if type(G) == nx.Graph:
        if any(m in measures for m in ["D1", "D2", "D5"]):
            deg = dict(nx.degree(G))
        else:
            deg = np.nan
        indeg = outdeg = wei_insum_alpha_list = wei_outsum_alpha_list = np.nan

        # Calculate weighted degree, taking alpha into account
        # case of different alphas for each metric
        if len(set(alphalist)) != 1:
            wei_sum_alpha_list = [0, 0]
            
            # Only needed for D3 and D4
            if "D3" in measures:
                wei_sum_alpha_list.append(weisumalpha (G, alphalist[2]))
            else:
                wei_sum_alpha_list += [0]
                
            if "D4" in measures:
                wei_sum_alpha_list.append(weisumalpha (G, alphalist[3]))
            else:
                wei_sum_alpha_list += [0]

            wei_sum_alpha_list += [0]
        else:
            if any(m in measures for m in ["D3", "D4"]):
                if alphalist[0] != 1:
                    wei_sum_alpha = {}
                    for node in G.nodes():
                        wei_sum_alpha[node] = sum(
                            [
                                e[2]["weight"] ** alphalist[0]
                                for e in list(G.edges(node, data=True))
                            ]
                        )
                else:
                    wei_sum_alpha = dict(nx.degree(G, weight="weight"))
            else:
                wei_sum_alpha = 0

            wei_sum_alpha_list = (
                [0, 0] + [wei_sum_alpha] * 2 + [0]
            )  # Only needed for D3 and D4

    elif type(G) == nx.DiGraph:
        deg = wei_sum_alpha_list = np.nan
        if any(m in measures for m in ["D1", "D2", "D5"]):
            indeg = dict(G.in_degree())
            outdeg = dict(G.out_degree())
        else:
            indeg = outdeg = np.nan

        if len(set(alphalist)) != 1:
            wei_insum_alpha_list = [0, 0]
            wei_outsum_alpha_list = [0, 0]
            
            # Only needed for D3 and D4
            if "D3" in measures:
                insum, outsum = weiinoutsumalpha(G, alphalist[2])
                wei_insum_alpha_list.append(insum)
                wei_outsum_alpha_list.append(outsum)
            else:
                wei_insum_alpha_list.append(0)
                wei_outsum_alpha_list.append(0)
                
            if "D4" in measures:
                insum, outsum = weiinoutsumalpha(G, alphalist[3])
                wei_insum_alpha_list.append(insum)
                wei_outsum_alpha_list.append(outsum)
            else:
                wei_insum_alpha_list.append(0)
                wei_outsum_alpha_list.append(0)

            wei_insum_alpha_list += [0]
            wei_outsum_alpha_list += [0]
        else:
            if any(m in measures for m in ["D3", "D4"]):
                if alphalist[0] != 1:
                    wei_outsum_alpha = {}
                    wei_insum_alpha = {}
                    for node in G.nodes():
                        wei_outsum_alpha[node] = sum(
                            [
                                e[2]["weight"] ** alphalist[0]
                                for e in list(G.out_edges(node, data=True))
                            ]
                        )
                        wei_insum_alpha[node] = sum(
                            [
                                e[2]["weight"] ** alphalist[0]
                                for e in list(G.in_edges(node, data=True))
                            ]
                        )
                else:
                    wei_insum_alpha = dict(G.in_degree(weight="weight"))
                    wei_outsum_alpha = dict(G.out_degree(weight="weight"))
            else:
                wei_insum_alpha = wei_outsum_alpha = 0

            wei_insum_alpha_list = [0, 0] + [wei_insum_alpha] * 2 + [0]
            wei_outsum_alpha_list = [0, 0] + [wei_outsum_alpha] * 2 + [0]

    # Calculate max and min arc weight
    if G.number_of_edges() > 0:
        hasedges = True
        if any(m in measures for m in ["D1", "D3", "D4"]):
            maxwij = max(dict(G.edges).items(),
                         key=lambda x: x[1]["weight"])[1]["weight"]
        else:
            maxwij = np.nan
        if "D3" in measures:
            minwij = min(dict(G.edges).items(),
                         key=lambda x: x[1]["weight"])[1]["weight"]
        else:
            minwij = np.nan
    else:
        print(
            "Graph has no edges (remember that loops have been removed)."
            "The function will return all zeros, regardless of normalizaiton."
        )
        hasedges = False
        maxwij = np.nan
        minwij = np.nan

    return (
        G,
        n1,
        deg,
        indeg,
        outdeg,
        wei_insum_alpha_list,
        wei_outsum_alpha_list,
        wei_sum_alpha_list,
        totalWEI,
        maxwij,
        minwij,
        hasedges,
    )


def distinctiveness(G, alpha=1, normalize=False,
                    measures=["D1", "D2", "D3", "D4", "D5"]):

    if isinstance(alpha, list) and len(alpha) == 5:
        alphalist = alpha
    elif isinstance(alpha, (int, float)):
        alphalist = [alpha] * 5
    else:
        print(
            "Error in the choice of alpha."
            " Please specify a single number or a list of 5 values."
        )
        return np.nan

    if any(a < 1 for a in alphalist):
        print(
            "WARNING. Alpha should be >= 1,"
            " except you exactly know what you are doing."
        )
        if normalize is True:
            print(
                "For alpha < 1 normalization is not carried out."
                " This will be deactivated for all metrics."
            )
            normalize = False

    (
        G,
        n1,
        deg,
        indeg,
        outdeg,
        wei_insum_alpha_list,
        wei_outsum_alpha_list,
        wei_sum_alpha_list,
        totalWEI,
        maxwij,
        minwij,
        hasedges,
    ) = g_preprocess(G, alpha=alpha, measures=measures)

    if not hasedges:
        normalize = False

    Glist = list(G.nodes)

    # Define max of all metrics
    if normalize is True:
        print(
            "WARNING. Normalization of D3 is"
            " carried out using loose upper and lower bounds."
        )
        
        if "D1" in measures:
            D1max = np.log10(n1) * n1 * maxwij
            D1min = (1 - alphalist[0]) * maxwij * np.log10(n1) * n1

        if "D2" in measures:
            D2max = np.log10(n1) * n1
            D2min = (1 - alphalist[1]) * np.log10(n1) * n1

        if "D3" in measures:
            if type(G) == nx.Graph:
                D3max = np.log10(maxwij * (n1 + 1) * n1 * 0.5) * maxwij * n1
            elif type(G) == nx.DiGraph:
                D3max = np.log10(maxwij * (n1 + 1) * n1) * maxwij * n1
    
            threshold = (n1 - 1) * (maxwij ** alphalist[2] - maxwij)
            if (minwij - 1) > threshold:
                D3min = 0  # considers isolates
            else:
                D3min = (
                    n1
                    * maxwij
                    * np.log10(
                        ((n1 - 1) * maxwij + minwij)
                        / ((n1 - 1) * (maxwij) ** alphalist[2] + 1)
                    )
                )

        if "D4" in measures:
            D4max = n1 * maxwij
            D4min = 0  # considers isolates

        if "D5" in measures:
            D5max = n1
            D5min = 0  # considers isolates # 1/(n1**alphalist[4])
    else:
        D1max = D2max = D3max = D4max = D5max = 1
        D1min = D2min = D3min = D4min = D5min = 0

    # Computes Distinctiveness Centrality, all 5 metrics
    if type(G) == nx.Graph:
        # Set keys to zero for all nodes (to take isolates into account)
        if "D1" in measures:
            d1 = dict.fromkeys(Glist, 0)
        else:
            d1 = np.nan
        if "D2" in measures:
            d2 = dict.fromkeys(Glist, 0)
        else:
            d2 = np.nan
        if "D3" in measures:
            d3 = dict.fromkeys(Glist, 0)
        else:
            d3 = np.nan
        if "D4" in measures:
            d4 = dict.fromkeys(Glist, 0)
        else:
            d4 = np.nan
        if "D5" in measures:
            d5 = dict.fromkeys(Glist, 0)
        else:
            d5 = np.nan

        d1_in = np.nan
        d2_in = np.nan
        d3_in = np.nan
        d4_in = np.nan
        d5_in = np.nan
        d1_out = np.nan
        d2_out = np.nan
        d3_out = np.nan
        d4_out = np.nan
        d5_out = np.nan

        for u, v, data in G.edges(data=True):
            if "D1" in measures:
                d1[u] += data["weight"] * np.log10(n1 / deg[v] ** alphalist[0])
                d1[v] += data["weight"] * np.log10(n1 / deg[u] ** alphalist[0])

            if "D2" in measures:
                d2[u] += 1 * np.log10(n1 / deg[v] ** alphalist[1])
                d2[v] += 1 * np.log10(n1 / deg[u] ** alphalist[1])

            if "D3" in measures:
                d3[u] += data["weight"] * np.log10(
                    totalWEI
                    / (wei_sum_alpha_list[2][v]
                       - data["weight"] ** alphalist[2] + 1)
                )
                d3[v] += data["weight"] * np.log10(
                    totalWEI
                    / (wei_sum_alpha_list[2][u]
                       - data["weight"] ** alphalist[2] + 1)
                )

            if "D4" in measures:
                d4[u] += data["weight"] * (
                    data["weight"] ** alphalist[3] / wei_sum_alpha_list[3][v]
                )
                d4[v] += data["weight"] * (
                    data["weight"] ** alphalist[3] / wei_sum_alpha_list[3][u]
                )

            if "D5" in measures:
                d5[u] += 1 * (1 / deg[v] ** alphalist[4])
                d5[v] += 1 * (1 / deg[u] ** alphalist[4])

        if normalize is True:
            if "D1" in measures:
                d1 = {k: (v - D1min) / (D1max - D1min) for k, v in d1.items()}
            if "D2" in measures:
                d2 = {k: (v - D2min) / (D2max - D2min) for k, v in d2.items()}
            if "D3" in measures:
                d3 = {k: (v - D3min) / (D3max - D3min) for k, v in d3.items()}
            if "D4" in measures:
                d4 = {k: (v - D4min) / (D4max - D4min) for k, v in d4.items()}
            if "D5" in measures:
                d5 = {k: (v - D5min) / (D5max - D5min) for k, v in d5.items()}

    elif type(G) == nx.DiGraph:
        # Set keys to zero for all nodes
        # (to take isolates into account and nodes with zero in- or out-degree)
        if "D1" in measures:
            d1_in = dict.fromkeys(Glist, 0)
            d1_out = dict.fromkeys(Glist, 0)
        else:
            d1_in = d1_out = np.nan
        if "D2" in measures:
            d2_in = dict.fromkeys(Glist, 0)
            d2_out = dict.fromkeys(Glist, 0)
        else:
            d2_in = d2_out = np.nan
        if "D3" in measures:
            d3_in = dict.fromkeys(Glist, 0)
            d3_out = dict.fromkeys(Glist, 0)
        else:
            d3_in = d3_out = np.nan
        if "D4" in measures:
            d4_in = dict.fromkeys(Glist, 0)
            d4_out = dict.fromkeys(Glist, 0)
        else:
            d4_in = d4_out = np.nan
        if "D5" in measures:
            d5_in = dict.fromkeys(Glist, 0)
            d5_out = dict.fromkeys(Glist, 0)
        else:
            d5_in = d5_out = np.nan

        d1 = d2 = d3 = d4 = d5 = np.nan

        for u, v, data in G.edges(data=True):

            if "D1" in measures:
                d1_in[v] += data["weight"] * \
                    np.log10(n1
                             / outdeg[u] ** alphalist[0])
                d1_out[u] += data["weight"] * \
                    np.log10(n1
                             / indeg[v] ** alphalist[0])

            if "D2" in measures:
                d2_in[v] += 1 * np.log10(n1 / outdeg[u] ** alphalist[1])
                d2_out[u] += 1 * np.log10(n1 / indeg[v] ** alphalist[1])

            if "D3" in measures:
                d3_in[v] += data["weight"] * np.log10(
                    totalWEI
                    / (wei_outsum_alpha_list[2][u]
                       - data["weight"] ** alphalist[2] + 1)
                )
                d3_out[u] += data["weight"] * np.log10(
                    totalWEI
                    / (wei_insum_alpha_list[2][v]
                       - data["weight"] ** alphalist[2] + 1)
                )

            if "D4" in measures:
                d4_in[v] += data["weight"] * (
                    data["weight"] ** alphalist[3]
                    / wei_outsum_alpha_list[3][u]
                )
                d4_out[u] += data["weight"] * (
                    data["weight"] ** alphalist[3]
                    / wei_insum_alpha_list[3][v]
                )

            if "D5" in measures:
                d5_in[v] += 1 * (1 / outdeg[u] ** alphalist[4])
                d5_out[u] += 1 * (1 / indeg[v] ** alphalist[4])

        if normalize is True:
            # print("Normalization is only carried out"
            #       " for undirected graph metrics.")
            if "D1" in measures:
                d1_in = {k: (v - D1min) / (D1max - D1min)
                          for k, v in d1_in.items()}
                d1_out = {k: (v - D1min) / (D1max - D1min)
                          for k, v in d1_out.items()}
            if "D2" in measures:
                d2_in = {k: (v - D2min) / (D2max - D2min)
                          for k, v in d2_in.items()}
                d2_out = {k: (v - D2min) / (D2max - D2min)
                      for k, v in d2_out.items()}
            if "D3" in measures:
                d3_in = {k: (v - D3min) / (D3max - D3min)
                          for k, v in d3_in.items()}
                d3_out = {k: (v - D3min) / (D3max - D3min)
                      for k, v in d3_out.items()}
            if "D4" in measures:
                d4_in = {k: (v - D4min) / (D4max - D4min)
                          for k, v in d4_in.items()}
                d4_out = {k: (v - D4min) / (D4max - D4min)
                      for k, v in d4_out.items()}
            if "D5" in measures:
                d5_in = {k: (v - D5min) / (D5max - D5min)
                          for k, v in d5_in.items()}
                d5_out = {k: (v - D5min) / (D5max - D5min)
                      for k, v in d5_out.items()}

    DC = {
        "D1": d1,
        "D2": d2,
        "D3": d3,
        "D4": d4,
        "D5": d5,
        "D1_in": d1_in,
        "D2_in": d2_in,
        "D3_in": d3_in,
        "D4_in": d4_in,
        "D5_in": d5_in,
        "D1_out": d1_out,
        "D2_out": d2_out,
        "D3_out": d3_out,
        "D4_out": d4_out,
        "D5_out": d5_out,
    }
    DC = {k: v for k, v in DC.items() if not isinstance(v, float)}

    return DC




########### *************************************** EXPERIMENTAL *********************************************** ##

def distinctiveness_byattribute(G, attname, attval, alpha=1, measures=["D1", "D2", "D3", "D4", "D5"]):

    if isinstance(alpha, list) and len(alpha) == 5:
        alphalist = alpha
    elif isinstance(alpha, (int, float)):
        alphalist = [alpha] * 5
    else:
        print(
            "Error in the choice of alpha."
            " Please specify a single number or a list of 5 values."
        )
        return np.nan

    if any(a < 1 for a in alphalist):
        print(
            "WARNING. Alpha should be >= 1,"
            " except you exactly know what you are doing."
        )

    (
        G,
        n1,
        deg,
        indeg,
        outdeg,
        wei_insum_alpha_list,
        wei_outsum_alpha_list,
        wei_sum_alpha_list,
        totalWEI,
        maxwij,
        minwij,
        hasedges,
    ) = g_preprocess(G, alpha=alpha, measures=measures)

    Glist = list(G.nodes)

    # Computes Distinctiveness Centrality, all 5 metrics
    if type(G) == nx.Graph:
        # Set keys to zero for all nodes (to take isolates into account)
        if "D1" in measures:
            d1 = dict.fromkeys(Glist, 0)
        else:
            d1 = np.nan
        if "D2" in measures:
            d2 = dict.fromkeys(Glist, 0)
        else:
            d2 = np.nan
        if "D3" in measures:
            d3 = dict.fromkeys(Glist, 0)
        else:
            d3 = np.nan
        if "D4" in measures:
            d4 = dict.fromkeys(Glist, 0)
        else:
            d4 = np.nan
        if "D5" in measures:
            d5 = dict.fromkeys(Glist, 0)
        else:
            d5 = np.nan

        d1_in = np.nan
        d2_in = np.nan
        d3_in = np.nan
        d4_in = np.nan
        d5_in = np.nan
        d1_out = np.nan
        d2_out = np.nan
        d3_out = np.nan
        d4_out = np.nan
        d5_out = np.nan
        
        for u, v, data in G.edges(data=True):
            if "D1" in measures:
                if G.nodes[v][attname] == attval:
                    d1[u] += data["weight"] * np.log10(n1 / deg[v] ** alphalist[0])
                if G.nodes[u][attname] == attval:
                    d1[v] += data["weight"] * np.log10(n1 / deg[u] ** alphalist[0])

            if "D2" in measures:
                if G.nodes[v][attname] == attval:
                    d2[u] += 1 * np.log10(n1 / deg[v] ** alphalist[1])
                if G.nodes[u][attname] == attval:
                    d2[v] += 1 * np.log10(n1 / deg[u] ** alphalist[1])

            if "D3" in measures:
                if G.nodes[v][attname] == attval:
                    d3[u] += data["weight"] * np.log10(
                        totalWEI
                        / (wei_sum_alpha_list[2][v]
                           - data["weight"] ** alphalist[2] + 1)
                    )
                if G.nodes[u][attname] == attval:
                    d3[v] += data["weight"] * np.log10(
                        totalWEI
                        / (wei_sum_alpha_list[2][u]
                           - data["weight"] ** alphalist[2] + 1)
                    )

            if "D4" in measures:
                if G.nodes[v][attname] == attval:
                    d4[u] += data["weight"] * (
                        data["weight"] ** alphalist[3] / wei_sum_alpha_list[3][v]
                    )
                if G.nodes[u][attname] == attval:
                    d4[v] += data["weight"] * (
                        data["weight"] ** alphalist[3] / wei_sum_alpha_list[3][u]
                    )

            if "D5" in measures:
                if G.nodes[v][attname] == attval:
                    d5[u] += 1 * (1 / deg[v] ** alphalist[4])
                if G.nodes[u][attname] == attval:
                    d5[v] += 1 * (1 / deg[u] ** alphalist[4])


    elif type(G) == nx.DiGraph:
        # Set keys to zero for all nodes
        # (to take isolates into account and nodes with zero in- or out-degree)
        if "D1" in measures:
            d1_in = dict.fromkeys(Glist, 0)
            d1_out = dict.fromkeys(Glist, 0)
        else:
            d1_in = d1_out = np.nan
        if "D2" in measures:
            d2_in = dict.fromkeys(Glist, 0)
            d2_out = dict.fromkeys(Glist, 0)
        else:
            d2_in = d2_out = np.nan
        if "D3" in measures:
            d3_in = dict.fromkeys(Glist, 0)
            d3_out = dict.fromkeys(Glist, 0)
        else:
            d3_in = d3_out = np.nan
        if "D4" in measures:
            d4_in = dict.fromkeys(Glist, 0)
            d4_out = dict.fromkeys(Glist, 0)
        else:
            d4_in = d4_out = np.nan
        if "D5" in measures:
            d5_in = dict.fromkeys(Glist, 0)
            d5_out = dict.fromkeys(Glist, 0)
        else:
            d5_in = d5_out = np.nan

        d1 = d2 = d3 = d4 = d5 = np.nan

        for u, v, data in G.edges(data=True):

            if "D1" in measures:
                if G.nodes[u][attname] == attval:
                    d1_in[v] += data["weight"] * \
                        np.log10(n1
                                 / outdeg[u] ** alphalist[0])
                if G.nodes[v][attname] == attval:
                    d1_out[u] += data["weight"] * \
                        np.log10(n1
                                 / indeg[v] ** alphalist[0])

            if "D2" in measures:
                if G.nodes[u][attname] == attval:
                    d2_in[v] += 1 * np.log10(n1 / outdeg[u] ** alphalist[1])
                if G.nodes[v][attname] == attval:
                    d2_out[u] += 1 * np.log10(n1 / indeg[v] ** alphalist[1])

            if "D3" in measures:
                if G.nodes[u][attname] == attval:
                    d3_in[v] += data["weight"] * np.log10(
                        totalWEI
                        / (wei_outsum_alpha_list[2][u]
                           - data["weight"] ** alphalist[2] + 1)
                    )
                if G.nodes[v][attname] == attval:
                    d3_out[u] += data["weight"] * np.log10(
                        totalWEI
                        / (wei_insum_alpha_list[2][v]
                           - data["weight"] ** alphalist[2] + 1)
                    )

            if "D4" in measures:
                if G.nodes[u][attname] == attval:
                    d4_in[v] += data["weight"] * (
                        data["weight"] ** alphalist[3]
                        / wei_outsum_alpha_list[3][u]
                    )
                if G.nodes[v][attname] == attval:
                    d4_out[u] += data["weight"] * (
                        data["weight"] ** alphalist[3]
                        / wei_insum_alpha_list[3][v]
                    )

            if "D5" in measures:
                if G.nodes[u][attname] == attval:
                    d5_in[v] += 1 * (1 / outdeg[u] ** alphalist[4])
                if G.nodes[v][attname] == attval:
                    d5_out[u] += 1 * (1 / indeg[v] ** alphalist[4])

    DC = {
        "D1": d1,
        "D2": d2,
        "D3": d3,
        "D4": d4,
        "D5": d5,
        "D1_in": d1_in,
        "D2_in": d2_in,
        "D3_in": d3_in,
        "D4_in": d4_in,
        "D5_in": d5_in,
        "D1_out": d1_out,
        "D2_out": d2_out,
        "D3_out": d3_out,
        "D4_out": d4_out,
        "D5_out": d5_out,
    }
    DC = {k: v for k, v in DC.items() if not isinstance(v, float)}

    return DC


def dc_nodeattribute(G, attname, alpha = 1, measures=["D1", "D2", "D3", "D4", "D5"]):

    DCall = pd.DataFrame()
    for attval in set([v[attname] for k,v in dict(G.nodes(data=True)).items()]):
        DC_att = distinctiveness_byattribute(G, attname, attval, alpha= alpha, measures= measures)    
        DC_att = pd.DataFrame(DC_att).sort_index()
        
        DC_att.columns = [x+"_"+str(attval) for x in DC_att.columns]
        DCall = pd.concat([DCall, DC_att], axis = 1)
           
    return DCall


    
def dc_edgeattribute(G, attname, alpha = 1, measures=["D1", "D2", "D3", "D4", "D5"]):
    
    DCall = pd.DataFrame()
    for attval in set([e[2][attname] for e in G.edges(data=True)]):
        G1 = G.copy()
        for e in G.edges(data=True):
            if not e[2][attname] == attval:
                G1.remove_edge(*e[:2]) 
        
        DC_edge = distinctiveness(G1, alpha= alpha, measures= measures)
        DC_edge = pd.DataFrame(DC_edge).sort_index()
        DC_edge.columns = [x+"_"+str(attval) for x in DC_edge.columns]
        DCall = pd.concat([DCall, DC_edge], axis = 1)
        
    return DCall