from distinctiveness.dc import distinctiveness
import networkx as nx
import random

#G = nx.fast_gnp_random_graph(5000, 0.3, directed=False)
G = nx.fast_gnp_random_graph(5000, 0.3, directed=True)

for (u,v,w) in G.edges(data=True):
    w['weight'] = random.randint(0,10)


distinctiveness(G, normalize = True, alpha = [2,3,4,5,6], measures=["D1","D2","D3","D4","D5"])

# measures=["D1","D2","D3","D4","D5"]
# for m in measures:
#     print(distinctiveness(G, normalize = True, alpha = [2,3,4,5,6], measures=[m]))
    
# measures=["D1","D2","D3","D4","D5"]
# for m in measures:
#     print(distinctiveness(G, normalize = False, alpha = 1, measures=[m]))
#     print(distinctiveness(G, normalize = False, alpha = 2, measures=[m]))