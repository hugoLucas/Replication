class GreedyAlgorithm:
    """
    This class will replicate certain virtual machines in a topology following the algorithm:
        1. Order all VMPair objects with respect to their communication frequency in decreasing order
        2. Find all PhysicalHost objects with non-zero remaining capacity
        3. For all VMPair objects in the ordered set:
            For all PhysicalHost objects in the left over set:
                Determine if placing one of the VirtualMachine objects in the VMPair in the current PhysicalHost will
                reduce the communication cost of the pair object
                If so, replicate the one of the VirtualMachine objects and place it in the current host
    This is done until no more hosts with remaining capacity exist

    Args:
        self.topology (GraphTopology): the topology this algorithm will use to replicate virtual machines
    """
    def __init__(self, base_topo):
        self.topology = base_topo
        pass

    def allocate(self):

        pass

    def get_cost(self):
        pass
