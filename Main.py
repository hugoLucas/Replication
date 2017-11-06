import GreedyAlgorithm
import GraphSimulator
import GraphTopology

NUM_VM_PAIRS = 1000

topo = GraphTopology.GraphTopology(k_val=4, n_p=NUM_VM_PAIRS, n_mb=0, max_vm_size=1, phys_host_cap=140)
topo.create_topology()

sim = GraphSimulator.GraphSimulator(topo, NUM_VM_PAIRS)
sim.set_up_data_center()
sim.pass_algorithm(GreedyAlgorithm.GreedyAlgorithm)
