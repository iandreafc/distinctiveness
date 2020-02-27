# Distinctiveness Centrality

The are five formulas that can be used to calculate Distinctiveness Centrality. The following function calculates them all and provides results as a list of dictionaries.

**`dc_all(G, normalize = False, alpha = 1)`**
:   calculates distinctiveness centrality for directed and undirected graphs.

- **`G`** is a [Networkx](https://networkx.github.io) graph object.
- **`normalize`** can be set to True, to obtain normalized scores for each metric.
- **`alpha`** must be a number greater or equal to 1. It represents the value of the alpha parameter used in the generalized formulas of distinctiveness centrality. If one value is provided it will be used for all the five metrics. Alternatively, alpha can be a `list` of five numbers, to specify different coefficients, for the different metrics (e.g. `alpha = [1,2,1,1,5]`)

Please note that each arc is expected to have a `weight` attribute, otherwise each missing weight will be considered equal to 1. Weights have to be >= 1. 