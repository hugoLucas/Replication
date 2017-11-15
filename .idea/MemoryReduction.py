
class MemoryReduction:
    """
    Memory Recution Algorithm:
        1. Iterate through every physical machine, from left to right (1 -> n):
            2. Iterate through all pairs of VMs and find:
                2a. The reduction in communication cost of putting one VM in the pair inside that physical machine (try
                both and then find which is the best)
                2b. The reduction in communication cost of putting both VMs of the pair inside that physical machine
                2c. Save those numbers in a dictionary
            3. Find the largest reduction in the sets generated in 2a and 2b.
            4. Place the VMs according to the largest reduction found in the previous step.
            5. Loop

    Reduction should be calculated by dividing the change in communication cost by the memory requirement of the
    placement.

    Args:
        self.topology (GraphTopology): the topology this algorithm will use to replicate virtual machines
        self.vm_pairs (VMPair): a list of VMPair objects inside the input topology
    """

    def __init__(self, base_topo, virtual_machine_pairs):
        self.vm_pairs = virtual_machine_pairs
        self.topology = base_topo

    def allocate(self):
        for host in self.topology.get_hosts():
            while host.has_space():
                if host.can_fit(1):
                    single_placement = self.one_vm_cost_map(host)
                if host.can_fit(2):
                    double_placement = self.two_vm_cost_map()

                single_placement = sorted(single_placement, key=lambda x: x[0], reverse=True)
                double_placement = sorted(double_placement, key=lambda x: x[0], reverse=True)


    def get_cost(self):
        pass

    def one_vm_cost_map(self, physical_host):
        costs = []
        for pair in self.vm_pairs:
            vm_1, vm_2 = pair.get_vms()
            vm_1_original_parent, vm_2_original_parent = vm_1.get_parent(), vm_2.get_parent()

            original_cost = self.cost_function(vm_1_original_parent, vm_2_original_parent)
            new_cost_1 = self.cost_function(host, vm_2_original_parent) * pair.get_communication_frequency()
            new_cost_2 = self.cost_function(vm_1_original_parent, host) * pair.get_communication_frequency()

            if new_cost_1 < new_cost_2:
                costs.append([original_cost - new_cost_1, vm_1])
            else:
                costs.append([original_cost - new_cost_2, vm_2])
        return costs

    def two_vm_cost_map(self, physical_host):
        """
        This method iterates through all vm pairs in order to determine if the placement of an entire pair of virutal
        machines is the most efficient placement in the host.

        :param physical_host:   the current physical host being investigated
        :return: a list of tuples of the form [int, vm_pair], means no vm in the pair was in the physical host
        """
        costs = []
        for pair in self.vm_pairs:
            vm_1, vm_2 = pair.get_vms()
            vm_1_original_parent, vm_2_original_parent = vm_1.get_parent(), vm_2.get_parent()
            original_cost = self.cost_function(vm_1_original_parent, vm_2_original_parent)

            if physical_host != vm_1_original_parent and physical_host != vm_2_original_parent:
                costs.append([original_cost/2, pair])

    def cost_function(self, parent_1, parent_2):
        if parent_1 == parent_2:
            return 0
        else:
            edge_1, edge_2 = parent_1.get_edge_switch(), parent_2.get_edge_switch()
            return self.topology.get_distance(edge_1, edge_2) + 2
