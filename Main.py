import ClusterAlgorithm
import MemoryReduction
import GreedyAlgorithm
import GraphSimulator
import GraphTopology

import matplotlib

NUM_VM_PAIRS = 50
MAX_VM_SIZE = 1
NUM_SIMS = 20
HOST_CAP = 8
K_VAL = 4

base_data, greedy_data, cluster_data, mem_reduc_data = [], [], [], []
for i in range(0, NUM_SIMS):
    topo = GraphTopology.GraphTopology(k_val=K_VAL, n_p=NUM_VM_PAIRS, n_mb=0, max_vm_size=MAX_VM_SIZE,
                                       phys_host_cap=HOST_CAP)
    topo.create_topology()

    sim = GraphSimulator.GraphSimulator(topo, NUM_VM_PAIRS)
    sim.set_up_data_center()

    base_data.append(sim.get_base_cost())

    greedy_data.append(sim.pass_algorithm(GreedyAlgorithm.GreedyAlgorithm))
    sim.revert_state()

    cluster_data.append(sim.pass_algorithm(ClusterAlgorithm.ClusterAlgorithm))
    sim.revert_state()

    mem_reduc_data.append(sim.pass_algorithm(MemoryReduction.MemoryReduction))
    sim.revert_state()

    print "SIM {} done...".format(str(i + 1))

