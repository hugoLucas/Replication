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
    This is done until no more hosts with remaining capacity exist. The code in this class assumes the VMs have a
    uniform size.

    Args:
        self.topology (GraphTopology): the topology this algorithm will use to replicate virtual machines
        self.vm_pairs (VMPair): a list of VMPair objects inside the input topology
    """
    def __init__(self, base_topo, virtual_machine_pairs):
        self.vm_pairs = virtual_machine_pairs
        self.topology = base_topo

    def allocate(self):
        """
        Replicates VMs according to the algorithm outlined above
        :return: None
        """
        vm_pairs = sorted(self.vm_pairs, key=lambda v: v.get_communication_frequency())
        phy_hosts = filter(lambda v: v.has_space(), self.topology.get_hosts())

        while len(phy_hosts) > 0:
            pair = vm_pairs.pop(0)
            vm_1, vm_2 = pair.get_vms()
            if vm_1.get_parent() != vm_2.get_parent():
                host_1, host_2 = vm_1.get_parent(), vm_2.get_parent()
                comm_cost = self.topology.get_distance(host_1, host_2)

                for host in phy_hosts:
                    cost_1 = self.topology.get_distance(host.get_edge_switch(), host_1)
                    cost_2 = self.topology.get_distance(host.get_edge_switch(), host_2)
                    min_cost = min(cost_1, cost_2)

                    cost_dict = {cost_1: vm_1, cost_2: vm_2}
                    if min_cost < comm_cost:
                        replicated_vm = cost_dict[min_cost].replicate()
                        if host.can_fit(replicated_vm.get_size()):
                            host.replicate_vm(replicated_vm)
                            replicated_vm.assign_parent(host)
                            pair.add_replicated(replicated_vm)
                        else:
                            phy_hosts.remove(host)

    def get_cost(self):
        pass
