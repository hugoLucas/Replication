import GraphSimulator
import GraphTopology

NUM_VM_PAIRS = 1000

topo = GraphTopology.GraphTopology(k_val=8, n_p=NUM_VM_PAIRS, n_mb=0, max_vm_size=1, phys_host_cap=None)
topo.create_topology()

sim = GraphSimulator.GraphSimulator(topo, NUM_VM_PAIRS)

