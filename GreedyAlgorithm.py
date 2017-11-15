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
        vm_pairs = sorted(self.vm_pairs, key=lambda v: v.get_communication_frequency(), reverse=True)
        phy_hosts = filter(lambda v: v.has_space(), self.topology.get_hosts())
        while len(phy_hosts) > 0:

            if len(vm_pairs) == 0:
                break

            pair = vm_pairs.pop(0)
            vm_1, vm_2 = pair.get_vms()
            if vm_1.get_parent() != vm_2.get_parent():
                host_1, host_2 = vm_1.get_parent(), vm_2.get_parent()
                comm_cost = self.topology.get_distance(host_1.get_edge_switch(), host_2.get_edge_switch())

                for host in phy_hosts:
                    cost_1 = self.topology.get_distance(host.get_edge_switch(), host_1.get_edge_switch())
                    cost_2 = self.topology.get_distance(host.get_edge_switch(), host_2.get_edge_switch())
                    min_cost = min(cost_1, cost_2)

                    cost_dict = {cost_1: vm_2, cost_2: vm_1}
                    if min_cost < comm_cost:
                        replicated_vm = cost_dict[min_cost].replicate()
                        if host.can_fit(replicated_vm.get_size()):
                            host.replicate_vm(replicated_vm)
                            replicated_vm.assign_parent(host)
                            pair.add_replicated_vm(replicated_vm)
                        else:
                            phy_hosts.remove(host)

    def get_cost(self):
        """
        Calculates the total communication cost for all the replicated pairs in the topology
        :return: (int) total communication cost
        """
        communication_cost = 0
        for pair in self.vm_pairs:
            vm_1, vm_2 = pair.get_vms()
            comm_frequency = pair.get_communication_frequency()

            if pair.was_replicated():
                replicated_vm = pair.get_replicated_vms()[0]

                if replicated_vm.get_name() == vm_1.get_name():
                    hop_cost = self.topology.get_distance(replicated_vm.get_parent().get_edge_switch(),
                                                          vm_2.get_parent().get_edge_switch()) + 2
                else:
                    hop_cost = self.topology.get_distance(vm_1.get_parent().get_edge_switch(),
                                                          replicated_vm.get_parent().get_edge_switch()) + 2

                communication_cost += (hop_cost * comm_frequency)
            else:
                hop_cost = self.topology.get_distance(vm_1.get_parent().get_edge_switch(),
                                                      vm_2.get_parent().get_edge_switch()) + 2
                communication_cost += (hop_cost * comm_frequency)

        return communication_cost
