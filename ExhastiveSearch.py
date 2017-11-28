
class ExhastiveSearch:

    def __init__(self, base_topo, virtual_machine_pairs):
        self.vm_pairs = virtual_machine_pairs
        self.topology = base_topo

        self.replicated_count = 0

    def allocate(self):
        while self.replicated_count < len(self.vm_pairs):
            host_minimum = []
            single_placement, double_placement = [], []
            for host in self.topology.get_hosts():
                if host.can_fit(1):
                    single_placement = self.one_vm_cost_map(host)
                    single_placement = sorted(single_placement, key=lambda x: x[0], reverse=True)
                if host.can_fit(2):
                    double_placement = self.two_vm_cost_map(host)
                    double_placement = sorted(double_placement, key=lambda x: x[0], reverse=True)

                if len(single_placement) > 0 and len(double_placement) > 0:
                    single_min, double_min = single_placement[0][0], double_placement[0][0]
                    if single_min > double_min:
                        host_minimum.append([single_min, host, single_placement[0][1], single_placement[0][2]])
                    else:
                        host_minimum.append([double_min, host, double_placement[0][1]])
                elif len(single_placement) > 0:
                    host_minimum.append([single_placement[0][0], host, single_placement[0][1], single_placement[0][2]])

            host_minimum = sorted(host_minimum, key=lambda x: x[0], reverse=True)
            if len(host_minimum) > 0:
                best_allocation = host_minimum[0]
                if len(best_allocation) ==  4:
                    replicated_vm = best_allocation[2].replicate()
                    best_allocation[1].replicate_vm(replicated_vm)
                    replicated_vm.assign_parent(best_allocation[1])
                    best_allocation[3].add_replicated_vm(replicated_vm)
                else:
                    org_vm_1, org_vm_2 = best_allocation[2].get_vms()
                    replicated_vm_1 = org_vm_1.replicate()
                    replicated_vm_2 = org_vm_2.replicate()
                    best_allocation[1].replicate_vm(replicated_vm_1)
                    best_allocation[1].replicate_vm(replicated_vm_2)
                    replicated_vm_1.assign_parent(best_allocation[1])
                    replicated_vm_2.assign_parent(best_allocation[1])
                    best_allocation[2].add_replicated_vm(replicated_vm_1)
                    best_allocation[2].add_replicated_vm(replicated_vm_2)
                self.replicated_count += 1
            else:
                break

    def get_cost(self):
        communication_cost = 0
        for pair in self.vm_pairs:
            vm_1, vm_2 = pair.get_vms()
            comm_frequency = pair.get_communication_frequency()

            if pair.was_replicated():
                replicated_vms = pair.get_replicated_vms()

                if len(replicated_vms) == 1:
                    rep_vm = replicated_vms[0]
                    if rep_vm.get_name() == vm_1.get_name():
                        hop_cost = self.hop_cost(rep_vm, vm_2, comm_frequency)
                    else:
                        hop_cost = self.hop_cost(vm_1, rep_vm, comm_frequency)
                    communication_cost += hop_cost
                else:
                    rep_vm_1, rep_vm_2 = replicated_vms
                    hop_cost = self.hop_cost(rep_vm_1, rep_vm_2, comm_frequency)
                    communication_cost += hop_cost
            else:
                communication_cost += self.hop_cost(vm_1, vm_2, comm_frequency)

        return communication_cost

    def one_vm_cost_map(self, physical_host):
        costs = []
        for pair in self.vm_pairs:
            if not pair.was_replicated():
                vm_1, vm_2 = pair.get_vms()
                vm_1_original_parent, vm_2_original_parent = vm_1.get_parent(), vm_2.get_parent()

                freq = pair.get_communication_frequency()
                original_cost = self.cost_function(vm_1_original_parent, vm_2_original_parent) * freq
                new_cost_1 = self.cost_function(physical_host, vm_2_original_parent) * freq
                new_cost_2 = self.cost_function(vm_1_original_parent, physical_host) * freq

                if original_cost > new_cost_1 or original_cost > new_cost_2:
                    if new_cost_1 < new_cost_2:
                        costs.append([original_cost - new_cost_1, vm_1, pair])
                    else:
                        costs.append([original_cost - new_cost_2, vm_2, pair])
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
            if not pair.was_replicated():
                vm_1, vm_2 = pair.get_vms()
                vm_1_original_parent, vm_2_original_parent = vm_1.get_parent(), vm_2.get_parent()
                original_cost = self.cost_function(vm_1_original_parent, vm_2_original_parent) * \
                                pair.get_communication_frequency()

                if physical_host != vm_1_original_parent and physical_host != vm_2_original_parent:
                    costs.append([original_cost/2, pair])
        return costs

    def cost_function(self, parent_1, parent_2):
        if parent_1 == parent_2:
            return 0
        else:
            edge_1, edge_2 = parent_1.get_edge_switch(), parent_2.get_edge_switch()
            return self.topology.get_distance(edge_1, edge_2) + 2

    def hop_cost(self, vm_1, vm_2, comm_frequency):
        parent_1, parent_2 = vm_1.get_parent(), vm_2.get_parent()
        if parent_1 != parent_2:
            if parent_1.get_edge_switch() == parent_2.get_edge_switch():
                return 2
            hop_cost = self.topology.get_distance(parent_1.get_edge_switch(), parent_2.get_edge_switch()) + 2
            return hop_cost * comm_frequency
        return 0
