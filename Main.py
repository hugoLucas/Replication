import GreedyAlgorithm
import GraphSimulator
import GraphTopology
import MemoryReduction
import ClusterAlgorithm

NUM_VM_PAIRS = 50

topo = GraphTopology.GraphTopology(k_val=4, n_p=NUM_VM_PAIRS, n_mb=0, max_vm_size=1, phys_host_cap=8)
topo.create_topology()

sim = GraphSimulator.GraphSimulator(topo, NUM_VM_PAIRS)
sim.set_up_data_center()

sim.pass_algorithm(GreedyAlgorithm.GreedyAlgorithm)
sim.revert_state()

sim.pass_algorithm(ClusterAlgorithm.ClusterAlgorithm)
sim.revert_state()

sim.pass_algorithm(MemoryReduction.MemoryReduction)
sim.revert_state()
