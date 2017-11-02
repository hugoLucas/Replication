import igraph
import math as m
import random as r
import NetworkComponents as networks


class GraphTopology:

    def __init__(self, k_val, n_p, n_mb, max_vm_size, phys_host_cap=None):
        self.k = k_val
        self.n_pairs = n_p
        self.n_middleboxes = n_mb
        self.max_vm_size = max_vm_size

        self.hosts, self.edge_switches, self.agg_switches, self.core_switches = [], [], [], []
        self.middleboxes = []
        self.master_graph = None

        self.phys_host_cap = phys_host_cap

    def create_topology(self):
        fat_tree = igraph.Graph()
        k = self.k

        num_hosts = num_core_switches = int(m.pow(k / 2, 2))
        num_agg_switches = num_edge_switches = num_connections = k / 2

        # Make all the hosts, 2.0 needed to make expression float and thus roundable up to the nearest integer
        if self.phys_host_cap is None:
            host_capacity = int(m.ceil((self.n_pairs * 2.0 * self.max_vm_size) / (num_hosts * k)))
        else:
            host_capacity = self.phys_host_cap
        for i in range(0, num_hosts * k):
            host_name = "host_{}".format(i + 1)
            host = networks.PhysicalMachine(host_capacity, host_name)

            fat_tree.add_vertex(name=host_name)
            fat_tree.vs.select(name=host_name)["host"] = host
            self.hosts.append(host)

        # Make all the edge switches
        pod_number, pod_index = 0, 0
        vertical_number = 1
        for i in range(0, int(num_edge_switches * k)):
            edge_switch_name = "edge_switch_" + str(i + 1)
            edge_switch = networks.PhysicalSwitch(edge_switch_name)
            edge_switch.set_p(pod_number)
            edge_switch.set_v(vertical_number)
            edge_switch.set_h(2)
            pod_index += 1
            vertical_number += 1

            if pod_index == k / 2:
                pod_index = 0
                pod_number += 1
                vertical_number = 0

            fat_tree.add_vertex(name=edge_switch_name)
            fat_tree.vs.select(name=edge_switch_name)["edge_switch"] = edge_switch
            self.edge_switches.append(edge_switch)

        # Make all the aggregate switches
        pod_number, pod_index = 0, 0
        vertical_number = 0
        for i in range(0, int(num_agg_switches * k)):
            agg_switch_name = "agg_switch_" + str(i + 1)
            agg_switch = networks.PhysicalSwitch(agg_switch_name)
            agg_switch.set_p(pod_number)
            agg_switch.set_v(vertical_number)
            agg_switch.set_h(1)
            pod_index += 1
            vertical_number += 1

            if pod_index == k/2:
                pod_index = 0
                pod_number += 1
                vertical_number = 0

            fat_tree.add_vertex(name=agg_switch_name)
            fat_tree.vs.select(name=agg_switch_name)["agg_switch"] = agg_switch
            self.agg_switches.append(agg_switch)

        # Make all the core switches
        for i in range(0, num_core_switches):
            core_switch_name = "core_switch_" + str(i + 1)
            core_switch = networks.PhysicalSwitch(core_switch_name)

            fat_tree.add_vertex(name=core_switch_name)
            fat_tree.vs.select(name=core_switch_name)["core_switch"] = core_switch
            self.core_switches.append(core_switch)

        # Link Hosts to Edge Switches
        n_host = 0
        for edge_switch in self.edge_switches:
            for i in range(0, int(num_connections)):
                fat_tree.add_edge(source=edge_switch.get_name(), target=self.hosts[n_host].get_name())
                self.hosts[n_host].set_edge_switch(edge_switch)
                n_host += 1

        # Link Aggregation Switches to Edge Switches
        num_edge, n_edge = 0, 0
        for agg_switch in self.agg_switches:
            start_value = num_edge
            for i in range(0, int(num_edge_switches)):
                fat_tree.add_edge(source=agg_switch.get_name(), target=self.edge_switches[num_edge].get_name())
                num_edge += 1
            num_edge = start_value

            n_edge += 1
            if n_edge >= int(num_edge_switches):
                num_edge += num_edge_switches
                n_edge = 0

        # Link Core Switches to Aggregation Switches
        num_edge, agg_switch_index = 0, 0
        for core_switch in self.core_switches:
            start_value = agg_switch_index
            for i in range(0, k):
                fat_tree.add_edge(source=core_switch.get_name(), target=self.agg_switches[agg_switch_index].get_name())
                agg_switch_index += num_connections
            agg_switch_index = start_value
            num_edge += 1
            if num_edge >= int(num_edge_switches):
                agg_switch_index += 1
                num_edge = 0

        self.master_graph = fat_tree

    def create_middleboxes(self):
        middlebox_host = []
        for i in range(1, self.n_middleboxes + 1):
            new_middlebox = networks.MiddleBox("MiddleBox_" + str(i))
            random_parent_switch = self.get_random_switch()

            while random_parent_switch.get_name() in middlebox_host:
                random_parent_switch = self.get_random_switch()

            new_middlebox.set_parent_switch(random_parent_switch)
            middlebox_host.append(random_parent_switch.get_name())
            self.middleboxes.append(new_middlebox)

    def get_random_switch(self):
        switches = self.agg_switches + self.edge_switches
        return switches[r.randint(0, len(switches) - 1)]

    def get_hosts(self):
        return self.hosts

    def get_topology_graph(self):
        return self.master_graph

    def get_middleboxes(self):
        return self.middleboxes

    def set_middleboxes(self, mbs):
        self.middleboxes = mbs

    def reset_physical_hosts(self):
        map(lambda phys_mach: phys_mach.clear_physical_machine(), self.hosts)

    def get_switches(self):
        return self.agg_switches + self.core_switches + self.edge_switches

    @staticmethod
    def get_distance(node1, node2):
        p1, v1, h1 = node1.get_p(), node1.get_v(), node1.get_h()
        p2, v2, h2 = node2.get_p(), node2.get_v(), node2.get_h()

        if p1 == p2:
            if v1 == v2:
                return 1
            else:
                if h1 == h2:
                    return 2
                else:
                    return 1
        else:
            if v1 == v2:
                if h1 == h2:
                    return 2 * h1
                else:
                    return 3
            else:
                if h1 == h2:
                    return 4
                else:
                    return 3