import numpy as np
from node import Node


def bound_T(N_):
    T_ = N_
    for s in np.arange(1, N_+1, 1):
        temp = int(N_/s) - 2 + (s-1)
        if temp < T_:
            T_ = temp
    return T_


def create_ring_biswapped_network(n):
    g_nodes = []
    h_nodes = []

    for i in range(n):
        sub_graph_g = []
        sub_graph_h = []
        for j in range(n):
            sub_graph_g.append(Node(i, j, 0, True))
            sub_graph_h.append(Node(i, j, 1, True))
        g_nodes.append(sub_graph_g)
        h_nodes.append(sub_graph_h)

    nodes = [g_nodes, h_nodes]
    
    for hg in range(2):
        for i in range(n):
            for j in range(n):
                nodes[hg][i][j].neighbour = [
                    nodes[hg][i][(j-1)%n], 
                    nodes[hg][i][(j+1)%n], 
                    nodes[1-hg][j][i]
                ]


    return nodes