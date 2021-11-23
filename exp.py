from scipy.stats import bernoulli
from node import Node
from bsn_helper import bound_T, create_ring_biswapped_network
from hami_helper import create_hami_cycle
import numpy as np
import random
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser(description="5-step diagnosis of ring-based biswapped network")

parser.add_argument('--n', type=int, default=3, help="ring size")
parser.add_argument('--p1', type=float, default=0.5, help="p1")
parser.add_argument('--p2', type=float, default=0.5, help="p2")
parser.add_argument('--print', action="store_true", help="print the nodes along the Hamiltionian cycle")

args = parser.parse_args()
n = args.n
N = n * n * 2
T = bound_T(N)

def single_exp(n):
    # Create the biswapped network
    nodes = create_ring_biswapped_network(n)

    # Step 2: construct the hamiltonian cycle
    hami_cycle = create_hami_cycle(nodes, n, N)

    # Step 3: assign faulty nodes
    t_star = random.randint(1, T)
    faulty_indices = np.arange(len(hami_cycle))
    np.random.shuffle(faulty_indices)
    faulty_indices = faulty_indices[:t_star]

    for i in faulty_indices:
        hami_cycle[i].state = False

    #############################################################
    # Step 2: Conduct four test rounds along Hamiltonian cycle
    # to get its bidirection cycle syndrome.
    #############################################################

    clockwise_syndrome = []
    counter_clockwise_syndrome = []

    p1 = args.p1
    p2 = args.p2

    # clockwise test rounds
    for i in range(len(hami_cycle)):
        # i is fault-free
        if (hami_cycle[i].state):
            # i+1 is fault-free
            if hami_cycle[(i+1) % N].state:
                clockwise_syndrome.append(0)
            # i+1 is faulty
            else:
                clockwise_syndrome.append(1)
        # if i faulty
        else:
            # i+1 is fault-free
            if hami_cycle[(i+1) % N].state:
                clockwise_syndrome.append(bernoulli.rvs(size=(1,), p=p1)[0])
            else:
                clockwise_syndrome.append(bernoulli.rvs(size=(1,), p=p2)[0])

    # counter clockwise test rounds
    for i in range(len(hami_cycle)):
        # i+1 is fault-free
        if (hami_cycle[(i+1) % N].state):
            # i is fault-free
            if hami_cycle[i].state:
                counter_clockwise_syndrome.append(0)
            else:
                counter_clockwise_syndrome.append(1)
        # if i+1 is faulty
        else:
            # i if fault-free
            if hami_cycle[i].state:
                counter_clockwise_syndrome.append(bernoulli.rvs(size=(1,), p=p1)[0])
            else:
                counter_clockwise_syndrome.append(bernoulli.rvs(size=(1,), p=p2)[0])


    #############################################################
    # Step 3: Use ring diagnosis algorithm PickOut
    #############################################################

    for idx, n in enumerate(hami_cycle):
        n.hami_idx = idx

    # Step 3.1 Partition the cycle into sequences
    markers = np.zeros_like(clockwise_syndrome)
    a0 = 0
    for i in range(len(clockwise_syndrome)):
        if clockwise_syndrome[i] == 0 and clockwise_syndrome[(i+1) % N] == 1:
            a0 = i
            break

    while (True):
        if clockwise_syndrome[(a0+1)%N] == 0:
            a0 = (a0+1)%N
        else:
            if markers[(a0+2)%N] != 1:
                markers[(a0+2)%N] = 1
                a0 = (a0+2)%N
            else:
                break

    Sequences = []
    a0 = 0
    for i in range(len(clockwise_syndrome)):
        if markers[i] == 1:
            a0 = i + 1
            break

    sequence = []

    for i in range(len(clockwise_syndrome)):
        if (markers[(a0 + i) % N] == 1):
            sequence.append(hami_cycle[(a0 + i) % N])
            Sequences.append(sequence)
            sequence = []
        else:
            sequence.append(hami_cycle[(a0 + i) % N])

    # Step 3.2: For each sequence Si, from tail-first to tail-last
    # in counterclockwise direction, try to find the 1-arrow of first 
    # appearance. If such 1-arrow exists, then identify those node from
    # the one pointed by the 1-arrow to tail-last as faulty,
    # and fi records the number of diagnosed faulty nodes in Si.

    fi_seq = []
    f = 0

    for idx, s in enumerate(Sequences):
        # print("seq %d:" % idx)
        fi = 0
        for idx in np.arange(0, len(s)-2, 1)[::-1]:
            if counter_clockwise_syndrome[s[idx].hami_idx] == 1:
                fi += 1
                s[idx].diag_state = False
            else:
                if fi > 0:
                    s[idx].diag_state = False
        fi_seq.append(fi)
        f += fi

    # Step 3.3: For each sequence Si, if |Si| >= T-s-f+fi+3
    # f = sum fi, then pick out this sequence
    # identify the head as faulty, all unknown nodes in tail as fault-free

    for idx, s in enumerate(Sequences):
        if len(s) >= T - len(Sequences) - f + fi_seq[idx] + 3:
            for i in range(len(s) - 1):
                if s[i].diag_state == None:
                    s[i].diag_state = True
            s[-1].diag_state = False
            fi_seq[idx] += 1


    # Step 4: Diagnose the unknown nodes using the test outcomes between sequences

    # Case 1: if the head of unknown sequence is identified as fault-free,
    # then unknown nodes in tail must be faulty

    # Case 2: if the head is identified as faulty and the number of unknonw nodes
    # in tail is more than the number of allowed faults, then those unknown nodes 
    # in tail must be fault-free

    for idx, s in enumerate(Sequences):
        # both cases require the diagnode of the head node
        head = s[-1]
        if head.diag_state == None:
            if (Sequences[(idx + 1) % len(Sequences)][0].diag_state):
                # if the head is identified as fault-free
                if counter_clockwise_syndrome[head.hami_idx] == 0:
                    s[-1].diag_state = True
                    for i in range(len(s) - 1):
                        if s[i].diag_state == None:
                            s[i].diag_state = False
                            fi_seq[idx] += 1
                # if the head is identified as faulty
                # TODO: there could be more rules can be applied
                else:
                    s[-1].diag_state = False
                    fi_seq[idx] += 1

                    fault_num = 0
                    for fi in fi_seq:
                        if fi == 0:
                            fault_num += 1
                        else:
                            fault_num += fi
                    
                    # get number of unknonw
                    unknown_num = 0
                    for n in s:
                        if n.diag_state == None:
                            unknown_num += 1
                    
                    if unknown_num + fault_num > T:
                        for n in s:
                            if n.diag_state == None:
                                n.diag_state = True

    #############################################################
    # Step 4: Arrange one round of tests exploiting the diagnosed
    # fault-free nodes to test unknown nodes and identify the 
    # unknown nodes by corresponding test outcomes
    #############################################################

    modified = True
    while(modified):
        modified = False
        for n in hami_cycle:
            # if n is a diagnosed fault-free node:
            if n.diag_state:
                for ne in n.neighbour:
                    if ne.diag_state == None:
                        ne.diag_state = ne.state
                        modified = True

    eu = 0

    for n in hami_cycle:
        if args.print:
            n.print_node()
        n.correct()
        if n.diag_state == None:
            eu += 1

    # conmpute the number of unknonw nodes
    # print("EU: %d, U: %s" % (eu, float(eu)/float(N)))
    return eu


eus = []
for i in tqdm(range(1000)):
    eus.append(single_exp(n))

eu_mean = np.mean(eus)
eu_max = np.max(eus)

print("N|T: %d|%d" % (N, T))
print("EU: %.3f, UMAX: %d, U%%: %.3f%%" % (eu_mean, eu_max, float(eu_mean)/float(N) * 100))