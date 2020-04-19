#!/usr/bin/env python
# coding: utf-8

# In[2]:


import networkx as nx
import numpy as np

def getCentralization(G, measure="degree", mode="undirected", by_component=False, connection="strong", dist_unreachable="N"):
    
    r"""
    
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
    
    """
    
    print(f"Calculating {measure} centralization (by_component set to {by_component}).")
    
    # -------------------------------------------------
    # calculate centralization per connected component
    # -------------------------------------------------
    
    if by_component==True:
        print("Number of nodes:", nx.number_of_nodes(G))

        if mode=="undirected":
            if nx.is_directed(G)==True:
                G = G.to_undirected()
                print(f"\33[95m(Note: Disregarding directions in directed graph.)\33[0m")
            
            print("Number of connected components:", nx.number_connected_components(G))
            
            centralizations = []
            for cc in sorted(nx.connected_components(G), key=len, reverse=True):
                centralizations.append({'subgraph': G.subgraph(cc), 'nodes': cc, 'n': len(cc)})
                
        elif mode=="all" or mode=="in" or mode=="out":
            
            # check if graph is directed
            if nx.is_directed(G)==False:
                print(f"\33[91mError: mode=\"all\"! Graph is undirected. Set mode=\"undirected\".\33[0m")
                return()
            
            if mode=="out":
                G = G.reverse()

            centralizations = []
            
            if connection=="strong":
                print("Number of strongly connected components:", nx.number_strongly_connected_components(G))
                for cc in sorted(nx.strongly_connected_components(G), key=len, reverse=True):
                    centralizations.append({'subgraph': G.subgraph(cc), 'nodes': cc, 'n': len(cc)})
                    
            if connection=="weak":
                if measure=="closeness":
                    print(f"\33[91mError: connection=\"weak\"! Closeness centralization can only be computed per strongly connected component.\33[0m")
                    return()
                print("Number of weakly connected components:", nx.number_weakly_connected_components(G))
                for cc in sorted(nx.weakly_connected_components(G), key=len, reverse=True):
                    centralizations.append({'subgraph': G.subgraph(cc), 'nodes': cc, 'n': len(cc)})
                    
        if measure=="degree":
            for c in centralizations:
                if mode=="undirected":
                    c['centralities'] = {x:y for x,y in c['subgraph'].degree()}
                    c['centralities_scaled'] = {x:y/(c['n']-1) if not c['n']==1 else 0 for x,y in c['centralities'].items()}
                    c['theoretical_max'] = (c['n']-1)*(c['n']-2)
                elif mode=="all":
                    c['centralities'] = {x:y for x,y in c['subgraph'].degree()}
                    c['centralities_scaled'] = {x:y/(2*(c['n']-1)) if not c['n']==1 else 0 for x,y in c['centralities'].items()}
                    c['theoretical_max'] = 2*(c['n']-1)*(c['n']-2)
                elif mode=="in" or mode=="out":
                    c['centralities'] = {x:y for x,y in c['subgraph'].in_degree()}
                    c['centralities_scaled'] = {x:y/(c['n']-1) if not c['n']==1 else 0 for x,y in c['centralities'].items()}
                    c['theoretical_max'] = (c['n']-1)**2
                    
        elif measure=="betweenness":
            for c in centralizations:
                c['centralities'] = nx.betweenness_centrality(c['subgraph'], normalized=False)
                c['centralities_scaled'] = nx.betweenness_centrality(c['subgraph'], normalized=True)
                if mode=="undirected":
                    c['theoretical_max'] = ((c['n']-1)**2)*(c['n']-2)/2
                elif mode=="all" or mode=="in" or mode=="out":
                    c['theoretical_max'] = ((c['n']-1)**2)*(c['n']-2)
                    
        elif measure=="closeness":
            if mode=="all":
                G = G.to_undirected()
                print(f"\33[95m(Note: mode=\"all\". Disregarding directions.)\33[0m")
            for c in centralizations:
                c['centralities'] = nx.closeness_centrality(c['subgraph'], wf_improved=False)
                c['centralities_scaled'] = c['centralities']
                c['centralities'] = {x:np.float64(y)/(c['n']-1) if not c['n']==1 else 0 for x,y in c['centralities'].items()} # remove normalization from degree centralities
                if mode=="undirected" or mode=="all":
                    c['theoretical_max'] = (c['n']-2)/(2*c['n']-3)
                elif mode=="in" or mode=="out":
                    if dist_unreachable=="N":
                        c['theoretical_max'] = (c['n']-1)/c['n']
                    elif dist_unreachable=="zero":
                        c['theoretical_max'] = 1
                    
        # calculate centralizations
        for c in centralizations:         
            centrality_max = max(c['centralities'].values())

            x = 0

            for v in c['centralities'].values():
                x += (centrality_max - v)
            
            if c['theoretical_max']==0:
                c['centralization'] = np.nan
            else:
                c['centralization'] = x/c['theoretical_max']

        return(centralizations)

    # -------------------------------------------------
    # calculate centralization for whole graph
    # -------------------------------------------------
    
    if by_component==False:
        n = nx.number_of_nodes(G)
        print("Number of nodes:", n)

        if mode=="undirected":
            if nx.is_directed(G)==True:
                G = G.to_undirected()
                print(f"\33[95m(Note: Disregarding directions in directed graph.)\33[0m")
            
            if nx.is_connected(G)==False:
                print(f"\33[95m(Note: Graph is not connected.)\33[0m")
                
        elif mode=="all" or mode=="in" or mode=="out":
            
            # check if graph is directed
            if nx.is_directed(G)==False:
                print(f"\33[91mError: mode=\"all\"! Graph is undirected. Set mode=\"undirected\".\33[0m")
                return()

            # check if graph is connected
            if nx.is_strongly_connected(G)==False:
                print(f"\33[95m(Note: Graph is not strongly connected.)\33[0m")
                if measure=="closeness" and dist_unreachable=="zero":
                    print(f"\33[91mWarning: dist_unreachable=\"zero\". Closeness centralization is not well-defined for disconnected graphs. Set dist_unreachable=\"N\".\33[0m")
            
            if mode=="out":
                G = G.reverse()
                      
        if measure=="degree": 
            if mode=="undirected":
                centralities = {x:y for x,y in G.degree()}
                centralities_scaled = {x:y/(n-1) if not n==1 else 0 for x,y in centralities.items()}
                theoretical_max = (n-1)*(n-2)
            elif mode=="all":
                centralities = {x:y for x,y in G.degree()}
                centralities_scaled = {x:y/(2*(n-1)) if not n==1 else 0 for x,y in centralities.items()}
                theoretical_max = 2*(n-1)*(n-2)
            elif mode=="in" or mode=="out":
                centralities = {x:y for x,y in G.in_degree()}
                centralities_scaled = {x:y/(n-1) if not n==1 else 0 for x,y in centralities.items()}
                theoretical_max = (n-1)**2
                
        elif measure=="betweenness":
            centralities = nx.betweenness_centrality(G, normalized=False)
            centralities_scaled = nx.betweenness_centrality(G, normalized=True)
            if mode=="undirected":
                theoretical_max = ((n-1)**2)*(n-2)/2
            elif mode=="all" or mode=="in" or mode=="out":
                theoretical_max = ((n-1)**2)*(n-2)
                
        elif measure=="closeness":
            if mode=="all":
                G = G.to_undirected()
                print(f"\33[95m(Note: mode=\"all\". Disregarding directions.)\33[0m")
                
            if dist_unreachable=="N": # set geodesic length between disconnected nodes to N
                centralities = nx.closeness_centrality(G, wf_improved=False)
                if mode=="undirected" or mode=="all":
                    distances = {x:len(nx.descendants(G, x))/y if not y==0 else 0 for x,y in centralities.items()} # remove normalization from degree centralities
                    distances = {x:y + n*(n-len(nx.descendants(G, x))-1) for x,y in distances.items()}
                    theoretical_max = (n-2)/(2*n-3)
                elif mode=="in" or mode=="out":
                    distances = {x:len(nx.descendants(G.reverse(), x))/y if not y==0 else 0 for x,y in centralities.items()} # remove normalization from degree centralities
                    distances = {x:y + n*(n-len(nx.descendants(G.reverse(), x))-1) for x,y in distances.items()}
                    theoretical_max = (n-1)/n
                centralities = {x:1/y for x,y in distances.items()}
                centralities_scaled = {x:y*(n-1) for x,y in centralities.items()}
                
            if dist_unreachable=="zero": # set geodesic length between disconnected nodes to 0
                centralities = nx.closeness_centrality(G, wf_improved=False)
                if mode=="undirected" or mode=="all":
                    centralities = {x:np.float64(y)/len(nx.descendants(G, x)) if not len(nx.descendants(G, x))==0 else 0 for x,y in centralities.items()} # remove normalization from degree centralities
                    theoretical_max = (n-2)/(2*n-3)
                    centralities_scaled = {x:y*len(nx.descendants(G, x)) for x,y in centralities.items()}
                elif mode=="in" or mode=="out":
                    centralities = {x:np.float64(y)/len(nx.descendants(G.reverse(), x)) if not len(nx.descendants(G.reverse(), x))==0 else 0 for x,y in centralities.items()} # remove normalization from degree centralities
                    theoretical_max = 1
                    centralities_scaled = {x:y*len(nx.descendants(G.reverse(), x)) for x,y in centralities.items()}
                    
        # calculate centralizations 
        centrality_max = max(centralities.values())

        x = 0

        for v in centralities.values():
            x += (centrality_max - v)
        
        if theoretical_max==0:
            centralization = np.nan
        else:
            centralization = x/theoretical_max

        return(centralities, centralities_scaled, theoretical_max, centralization)

