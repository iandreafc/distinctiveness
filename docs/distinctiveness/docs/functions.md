# Distinctiveness Centrality

The are five formulas that can be used to calculate Distinctiveness Centrality. The following function calculates them all and provides results as a list of dictionaries.
 
**`dc_all(G, normalize = False, alpha = 1)`**
:   calculates distinctiveness centrality for directed and undirected graphs.

- **`G`** is a [Networkx](https://networkx.github.io) graph object.
- **`normalize`** can be set to True, to obtain normalized scores for each metric.
- **`alpha`** can have a value equal to 1 or bigger. Represents the value of the alpha parameter used in the generalized formulas of distinctiveness centrality.