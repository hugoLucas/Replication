class ClusterAlgorithm:

    def __init__(self, base_topo, virtual_machine_pairs):
        self.vm_pairs = virtual_machine_pairs
        self.topology = base_topo


    """
    Cluster Algorithm: replicate vms in a cluster, starting from highest frequency
    1. attempt to place replication in same machine
    2. attempt to place replication in pm under same edge switch
    3. attempt to place replication in same pod
    run algorithm for all communication pairs
    """
    def allocate(self):
        vm_pairs = sorted(self.vm_pairs, key=lambda v: v.get_communication_frequency(), reverse=True)
        phy_hosts = filter(lambda v: v.has_space(), self.topology.get_hosts())

        for pair in vm_pairs:
            vm_1, vm_2 = pair.get_vms()
            host_1, host_2 = vm_1.get_parent(), vm_2.get_parent()
            comm_cost = self.topology.get_distance(host_1.get_edge_switch(), host_2.get_edge_switch())
            vm_size = vm_1.get_size()
            set_flag = 0

            if vm_1.get_parent() == vm_2.get_parent():
                set_flag = 1
            elif set_flag == 0 and vm_1.get_parent() != vm_2.get_parent():
                if host_1.can_fit(vm_size):
                    replicated_vm = vm_2.replicate()
                    host_1.replicate_vm(replicated_vm)
                    replicated_vm.assign_parent(host_1)
                    pair.add_replicated_vm(replicated_vm)
                    set_flag = 1
                elif host_2.can_fit(vm_size):
                    replicated_vm = vm_1.replicate()
                    host_2.replicate_vm(replicated_vm)
                    replicated_vm.assign_parent(host_2)
                    pair.add_replicated_vm(replicated_vm)
                    set_flag = 1

            if set_flag == 0 and host_1.get_edge_switch() != host_2.get_edge_switch():
                #get physical machines under edge switch
                # check pms space under same edge switch
                # try to get in same pm under edge switch
                for host in phy_hosts:
                    if set_flag == 0:
                        if host.get_edge_switch() == host_1.get_edge_switch():
                            if host.can_fit(vm_size):
                                replicated_vm = vm_2.replicate()
                                host.replicate_vm(replicated_vm)
                                replicated_vm.assign_parent(host)
                                pair.add_replicated_vm(replicated_vm)
                                set_flag = 1

                        if set_flag == 0:
                            if host.get_edge_switch() == host_2.get_edge_switch():
                                if host.can_fit(vm_size):
                                    replicated_vm = vm_1.replicate()
                                    host.replicate_vm(replicated_vm)
                                    replicated_vm.assign_parent(host)
                                    pair.add_replicated_vm(replicated_vm)
                                    set_flag = 1
            else:
                set_flag = 1

            if set_flag == 0 and host_1.get_edge_switch().get_p() != host_2.get_edge_switch().get_p():
                for host in phy_hosts:
                    if set_flag == 0:
                        if host.get_edge_switch().get_p() == host_1.get_edge_switch().get_p():
                            if host.can_fit(vm_size):
                                replicated_vm = vm_2.replicate()
                                host.replicate_vm(replicated_vm)
                                replicated_vm.assign_parent(host)
                                pair.add_replicated_vm(replicated_vm)
                                set_flag = 1

                        if set_flag == 0:
                            if host.get_edge_switch().get_p() == host_2.get_edge_switch().get_p():
                                if host.can_fit(vm_size):
                                    replicated_vm = vm_1.replicate()
                                    host.replicate_vm(replicated_vm)
                                    replicated_vm.assign_parent(host)
                                    pair.add_replicated_vm(replicated_vm)
                                    set_flag = 1

            elif set_flag == 0:
                set_flag == 1


    def get_cost(self):
        """
        Calculates the total communication cost for all the replicated pairs in the topology
        :return: (int) total communication cost
        """
        communication_cost = 0
        for pair in self.vm_pairs:
            hop_cost = 0
            vm_1, vm_2 = pair.get_vms()
            comm_frequency = pair.get_communication_frequency()
            if pair.was_replicated():
                replicated_vm = pair.get_replicated_vms()[0]
                if replicated_vm.get_name() == vm_1.get_name():
                    if replicated_vm.get_parent() == vm_2.get_parent():
                        hop_cost = 0
                    elif replicated_vm.get_parent().get_edge_switch() == vm_2.get_parent().get_edge_switch():
                        hop_cost = self.topology.get_distance(replicated_vm.get_parent().get_edge_switch(), vm_2.get_parent().get_edge_switch()) + 1
                    else:
                        hop_cost = self.topology.get_distance(replicated_vm.get_parent().get_edge_switch(), vm_2.get_parent().get_edge_switch()) + 2
                else:
                    if replicated_vm.get_parent() == vm_1.get_parent():
                        hop_cost = 0
                    elif replicated_vm.get_parent().get_edge_switch() == vm_1.get_parent().get_edge_switch():
                        hop_cost = self.topology.get_distance(replicated_vm.get_parent().get_edge_switch(), vm_1.get_parent().get_edge_switch()) + 1
                    else:
                        hop_cost = self.topology.get_distance(vm_1.get_parent().get_edge_switch(), replicated_vm.get_parent().get_edge_switch()) + 2

                communication_cost += (hop_cost * comm_frequency)
            else:
                if vm_2.get_parent() == vm_1.get_parent():
                    hop_cost = 0
                elif vm_1.get_parent().get_edge_switch() == vm_2.get_parent().get_edge_switch():
                    hop_cost = self.topology.get_distance(vm_1.get_parent().get_edge_switch(), vm_2.get_parent().get_edge_switch()) + 1
                else:
                    hop_cost = self.topology.get_distance(vm_1.get_parent().get_edge_switch(), vm_2.get_parent().get_edge_switch()) + 2
                communication_cost += (hop_cost * comm_frequency)

        return communication_cost