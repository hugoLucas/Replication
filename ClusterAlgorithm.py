class ClusterAlgorithm:

    def __init__(self, base_topo, virtual_machine_pairs):
        self.vm_pairs = virtual_machine_pairs
        self.topology = base_topo

    def allocate(self):
        vm_pairs = sorted(self.vm_pairs, key=lambda v: v.get_communication_frequency(), reverse=True)
        phy_hosts = filter(lambda v: v.has_space(), self.topology.get_hosts())

        for v_p in vm_pairs:
            v_1, v_2 = v_p.get_vms()

            new_host, vm = self.can_place_together(v_1, v_2)
            if new_host is not None:
                self.place_machine(new_host, vm, v_p)
            else:
                new_host, vm = self.can_place_edge_switch(v_1, v_2, phy_hosts)
                if new_host is not None:
                    self.place_machine(new_host, vm, v_p)
                else:
                    new_host, vm = self.can_place_pod(v_1, v_2, phy_hosts)
                    if new_host is not None:
                        self.place_machine(new_host, vm, v_p)

    @staticmethod
    def place_machine(host, vm, pair):
        replicated_vm = vm.replicate()
        host.replicate_vm(replicated_vm)
        replicated_vm.assign_parent(host)
        pair.add_replicated_vm(replicated_vm)

    @staticmethod
    def return_results(h_1, h_2, v_1, v_2):
        if len(h_1) > 0:
            return h_1[0], v_2
        if len(h_2) > 0:
            return h_2[0], v_1
        return None, None

    def can_place_pod(self, v_1, v_2, hosts):
        p_1, p_2 = v_1.get_parent().get_edge_switch().get_p(), v_2.get_parent().get_edge_switch().get_p()
        h_1, h_2 = filter(lambda v: p_1 == v.get_edge_switch().get_p(), hosts), \
                   filter(lambda v: p_1 == v.get_edge_switch().get_p(), hosts)
        h_1, h_2 = filter(lambda v: v.can_fit(v_2.get_size()), h_1), filter(lambda v: v.can_fit(v_1.get_size()), h_2)
        return self.return_results(h_1, h_2, v_1, v_2)

    def can_place_edge_switch(self, v_1, v_2, hosts):
        e_1, e_2 = v_1.get_parent().get_edge_switch(), v_2.get_parent().get_edge_switch()
        h_1, h_2 = filter(lambda v: v.get_edge_switch() == e_1, hosts), \
                   filter(lambda v: v.get_edge_switch() == e_2, hosts)
        h_1, h_2 = filter(lambda v: v.can_fit(v_2.get_size()), h_1), filter(lambda v: v.can_fit(v_1.get_size()), h_2)
        return self.return_results(h_1, h_2, v_1, v_2)

    @staticmethod
    def can_place_together(v_1, v_2):
        p_1, p_2 = v_1.get_parent(), v_2.get_parent()

        if p_1.can_fit(v_2.get_size()):
            return p_1, v_2
        elif p_2.can_fit(v_1.get_size()):
            return p_2, v_1
        else:
            return None, None

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
