import NetworkComponents as net

import random


class GraphSimulator:
    def __init__(self, topology, num_vm_pairs):
        """
        :param topology:
        :param num_vm_pairs:
        """
        self.topo = topology
        self.n_vm_pairs = num_vm_pairs

        self.vm_freq_range = 100

        self.allocated_vm_pairs = []
        self.base_communication_cost = 0

    def pass_algorithm(self, algorithm_class):
        """
        Given an object representing a replication algorithm, this method will return the communication
        prepare the simulation to use this algorithm on the source topology.
        :param algorithm_class:
        :return:
        """
        algorithm = algorithm_class(self.topo, self.allocated_vm_pairs)
        algorithm.allocate()
        algorithm_cost = algorithm.get_cost() * 1.0
        reduction = (algorithm_cost - self.base_communication_cost)/self.base_communication_cost

        print "####### {} #######".format(algorithm_class)
        print "Base Cost: {}".format(self.base_communication_cost)
        print "New Cost: {}".format(algorithm_cost)
        print "Reduction: {} \n\n".format(reduction)

    def set_up_data_center(self):
        """
        Builds a set of random virtual machine pairs and allocates them in the data center
        topology in order to simulate a pre-existing data center.
        """
        self.create_virtual_machines()
        self.allocate_virtual_machines()

    def create_virtual_machines(self):
        """
        Creates a set of virtual machine pairs to allocate inside of a graph topology
        """
        for i in range(1, self.n_vm_pairs + 1, 1):
            frequency = random.randint(1, self.vm_freq_range)
            vm_1 = net.VirtualMachine(frequency, "vm_" + str((2 * i) - 1), 1)
            vm_2 = net.VirtualMachine(frequency, "vm_" + str((2 * i)), 1)

            vm_1.assign_pair(vm_2)
            vm_2.assign_pair(vm_1)

            self.allocated_vm_pairs.append(net.VMPair([vm_1, vm_2], frequency))
        self.allocated_vm_pairs.sort(key=lambda x: x.get_communication_frequency(), reverse=True)

    def allocate_virtual_machines(self):
        """
        Allocates the randomly created virtual machines in order to create an initial state
        for the cloud data center
        """
        physical_hosts = self.topo.get_hosts()
        free_indices = range(0, len(physical_hosts))
        for pair in self.allocated_vm_pairs:
            vm_1, vm_2 = pair.get_vms()

            host_1 = self.get_random_host(free_indices, physical_hosts, vm_1.get_size())
            host_1.add_vm(vm_1)
            vm_1.assign_parent(host_1)

            host_2 = self.get_random_host(free_indices, physical_hosts, vm_2.get_size())
            host_2.add_vm(vm_2)
            vm_2.assign_parent(host_2)

            if vm_1.get_parent() == vm_2.get_parent():
                hops = 0
            else:
                hops = self.topo.get_distance(host_1.get_edge_switch(), host_2.get_edge_switch()) + 2
            self.base_communication_cost += (hops * pair.get_communication_frequency())

    def revert_state(self):
        """
        Reverts the simulation topology to its pre-algorithm application state
        :return: None
        """
        map(lambda v: v.clear_replicated_machines(), self.topo.get_hosts())
        map(lambda v: v.reset_pair(), self.allocated_vm_pairs)

    @staticmethod
    def get_random_host(free_indices, hosts, vm_size):
        """
        Returns a random host in order to allow the random distribution of virtual machines in the beginning
        of a new simulation.

        :param free_indices:    a list of indices belonging to VMs in hosts list that have non-zero capacity
        :param hosts:           a list of PhysicalHosts that have non-zero capacity
        :param vm_size:         an integer representing the size of the VM to be added to the returned host
        :return:
        """
        index = random.randint(0, len(free_indices) - 1)
        host = hosts[free_indices[index]]

        while not host.can_fit(vm_size):
            free_indices.remove(free_indices[index])

            index = random.randint(0, len(free_indices) - 1)
            host = hosts[free_indices[index]]

        return host
