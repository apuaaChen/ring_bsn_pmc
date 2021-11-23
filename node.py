# Define a class of the node
class Node:
    def __init__(self, i, j, hg, state):
        self.i = i
        self.j = j
        self.hg = hg
        
        self.state = state
        self.diag_state = None

        self.neighbour = []

        self.in_hami = False
        self.hami_idx = -1
    
    def print_node(self):
        if self.diag_state == None:
            diag = "Unknown"
        elif self.diag_state:
            diag = "fault-free"
        else:
            diag = "faulty"
        
        if self.state:
            typ = "fault-free"
        else:
            typ = "fault"
        print("<%d, %d, %d | %s> : %s" % (self.hg, self.i, self.j, typ, diag))

    def correct(self):
        if self.diag_state != None:
            assert self.state == self.diag_state