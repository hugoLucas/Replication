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

        self.vm_freq_range = 1
        self.vm_comm_range = 1000

        self.allocated_vm_pairs = []
        self.replicated_vm_pairs = []

    """
    Builds a set of random virtual machine pairs and allocates them in the data center 
    topology in order to simulate a pre-existing data center. 
    """
    def set_up_data_center(self):
        self.create_virtual_machines()
        self.allocate_virtual_machines()

    """
    Creates a set of virtual machine pairs to allocate inside of a graph topology 
    """
    def create_virtual_machines(self):
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
        free_indices = range(0, len(self.allocated_vm_pairs))
        for pair in self.allocated_vm_pairs:
            vm_1, vm_2 = pair.get_vms()

            host_1 = self.get_random_host(free_indices, physical_hosts, vm_1.get_size())
            host_1.add_vm(vm_1)
            vm_1.assign_parent(host_1)

            host_2 = self.get_random_host(free_indices, physical_hosts, vm_2.get_size())
            host_2.add_vm(vm_2)
            vm_2.assign_parent(host_2)

    """
    Reverts the state of the simulation back to its creation state
    """
    def revert_state(self):
        return

    @staticmethod
    def get_random_host(free_indices, hosts, vm_size):
        index = random.randint(0, len(free_indices) - 1)
        host = hosts[free_indices[index]]

        while not host.can_fit(vm_size):
            free_indices.remove(free_indices[index])

            index = random.randint(0, len(free_indices) - 1)
            host = hosts[free_indices[index]]

        return host