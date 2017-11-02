
class Node:
    """
        Base class for every physical or virtual component of a Topology instance.

        node_cost_metrics: dictionary used to associate a Node to a series of cost metrics
        (hops, energy consumption, etc.)

        name: name of this object
    """

    def __init__(self, node_name):
        self.name = node_name
        self.node_cost_metrics = {}
        self.node_links = []

    def add_cost_metric(self, new_metric_value, new_metric_name):
        if new_metric_name not in self.node_cost_metrics:
            self.node_cost_metrics[new_metric_name] = new_metric_value
        else:
            raise ValueError

    def get_cost_metrics(self):
        return self.node_cost_metrics

    def get_name(self):
        return self.name

    def add_connection(self, link):
        self.node_links.append(link)

    def return_connections(self):
        return self.node_links


class VirtualMachine(Node, object):
    """
        Represents a virtual machine of a set size in simulations

        TODO: Implement variable communication packet sizes in order to simulate dropped packets due to
        link bandwidth limit
    """

    """ Storage requirement of virtual machine, used for variable sized VM simulations (in GB) """
    size = 1

    """ Virtual machine assigned as communication partner to this machine """
    pair = None

    """ Communication frequency between this machine and pair machine (Packets/cycle) """
    freq = 0

    """ Physical Machine this VM is assigned to """
    phys_parent = None

    def __init__(self, freq=1, name=None, vm_size=1):
        super(VirtualMachine, self).__init__(name)
        self.size = vm_size
        self.freq = freq

        if type(vm_size) is int and vm_size > 0:
            self.size = vm_size
        else:
            raise ValueError("Size of Virtual Machine must be an integer and be greater than 0")

    def assign_pair(self, vm_pair):
        if type(vm_pair) is VirtualMachine:
            self.pair = vm_pair
        else:
            raise ValueError("Pair of this Virtual Machine should be another Virtual Machine")

    def assign_parent(self, parent):
        self.phys_parent = parent

    def get_parent(self):
        return self.phys_parent

    def get_size(self):
        return self.size


class PhysicalMachine(Node, object):
    """
        Represents a physical machine capable of storing at most N virtual machines
    """

    """ Maximum capacity of physical machine (in GB) """
    capacity = 5

    """ How much physical machine memory virtual machines are currently using """
    current_capacity = 0

    """ A list of all virtual machines inside physical machine """
    vms = []

    def __init__(self, capacity=5, name=None):
        super(PhysicalMachine, self).__init__(name)
        self.vms = []

        if type(capacity) is int and capacity > 0:
            self.capacity = capacity
        else:
            raise ValueError("Capacity of Virtual Machine must be an integer and be greater than 0")

    def clear_physical_machine(self):
        self.current_capacity = 0
        self.vms = []

    def can_fit(self, vm_size):
        if self.current_capacity + vm_size <= self.capacity:
            return True
        return False

    def add_vm(self, vm):
        self.current_capacity += vm.get_size()
        self.vms.append(vm)

    def get_vms(self):
        return self.vms


class PhysicalSwitch(Node, object):
    """
        Represents a switch in a topology
    """

    """ Number of packets that have been processed by this switch """
    packets_processed = 0

    def __init__(self, name=None):
        super(PhysicalSwitch, self).__init__(name)


class VMPair:
    """
        Represents a pair of two VMs that communicate in a topology.
    """

    def __init__(self, vm_list, freq=1):
        self.vm_list = vm_list
        self.frequency = freq

    def get_vms(self):
        return self.vm_list

    def get_communication_frequency(self):
        return self.frequency
