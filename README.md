# getCentralization

    Calculate the centralization of a graph.
    
    Parameters
    -----
    
    G : graph
        A NetworkX graph.
        
    measure : string, optional (default="degree")
        Options are "degree", "betweenness", and "closeness".
    
    mode : string, optional (default="undirected")
        If "undirected", graph is undirected or, if graph is directed, directions are disregarded.
        If "all", both outgoing and incoming paths are considered.
        If "out", only outgoing paths are considered. Ignored if measure is "betweenness".
        If "in", only incoming paths are considered. Ignored if measure is "betweenness".
    
    by_component : boolean, optional (default=False)
        If True, centralization is calculated per component. Returns dictionary of results.
    
    connection : string, optional (default="strong")
        Used only if by_component is True.
        If "strong", compute centralization per strongly connected component.
        If "weak", compute centralization per weakly connected component. Cannot be used if measure is "closeness".
    
    dist_unreachable : string, optional (default="N")
        Used only if measure is "closeness".
        If "N", in case there is no path between node u and v, distance between u and v is set to the number of nodes. 
        If "zero", in case there is no path between node u and v, distance between u and v is set to zero.
            This will avoid infinitely long distances. Note, however, that the resulting closeness centralization will not be an accurate measure if graph is not strongly connected.   
            Returns centralities_scaled that are normalized by number of reachable nodes instead of n-1.
        
    Returns
    -----
    
    centralities : Dictionary of nodes with centrality as the value.
    
    centralities_scaled : Dictionary of nodes with centrality values scaled to range from 0 to 1.
    
    theoretical_max :  Graph level centrality score of the most centralized graph with the same number of nodes (some version of star graph, depending on mode).
    
    centralization : Graph centralization normalized using the theoretical maximum.
