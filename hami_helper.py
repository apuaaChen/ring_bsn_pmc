def create_hami_cycle(nodes, n, N):
    hami_cycle = [nodes[0][0][0],]
    nodes[0][0][0].in_hami = True
    i = 0
    j = 1
    hg = 0
    counter = 1
    while ((i!=0 or j!=0 or hg != 0) and (len(hami_cycle) <= N)):
        assert nodes[hg][i][j].in_hami == False
        hami_cycle.append(nodes[hg][i][j])
        nodes[hg][i][j].in_hami = True
        if (nodes[hg][i][(j+1)%n].in_hami):
            hg = 1 - hg
            temp = i
            i = j
            j = temp
        else:
            j = (j + 1) % n
    
    assert len(hami_cycle) == N
    for i in range(len(hami_cycle)):
        assert hami_cycle[i] in hami_cycle[(i+1) % N].neighbour
        assert hami_cycle[i] in hami_cycle[(i-1) % N].neighbour
    
    return hami_cycle