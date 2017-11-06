
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
        Represents a virtual machine in a topology.

        Args:
            self.phys_parent (PhysicalHost): the host that stores this VM
            self.size (int): the number of memory units needed to store this VM
            self.freq (int): the frequency this VM communicates with its pair
            self.pair (VirtualMachine): the other VM paired up with this VM
    """

    def __init__(self, freq=1, name=None, vm_size=1):
        super(VirtualMachine, self).__init__(name)
        self.phys_parent = None
        self.size = vm_size
        self.freq = freq
        self.pair = None

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

        Args:
            self.vms (list): a list of VirtualMachines stored in this PhysicalMachine
            self.current_capacity (int): the current number of memory units used by the stored VirtualMachines
            self.capacity (int): the maximum memory units contained in this PhysicalMachine
            self.edge_switch (PhysicalSwitch): the edge switch in a Fat Tree topology that this object is connected to
            self.replicated_vms (list): a list of replicated VirtualMachines store in this Physical Machine
            self.replicated_capacity (int): the number of memory units occupied by replicated VMs
    """

    def __init__(self, capacity=5, name=None):
        super(PhysicalMachine, self).__init__(name)

        self.replicated_capacity = 0
        self.current_capacity = 0
        self.capacity = capacity
        self.replicated_vms = []
        self.edge_switch = None
        self.vms = []

    def clear_physical_machine(self):
        """
        Reverts the object back to its initial state in order to run another simulation
        :return: None
        """
        self.current_capacity = 0
        self.replicated_vms = []
        self.vms = []

    def clear_replicated_machines(self):
        """
        Clears a PhysicalHost of all replicated VirtualMachine objects.
        :return: None
        """
        self.current_capacity -= self.replicated_capacity
        self.replicated_capacity = 0
        self.replicated_vms = []

    def can_fit(self, vm_size):
        """
        Determines if another virtual machine of a given size can fit inside this PhysicalMachine
        :param vm_size: (int) the size of VirtualMachine that needs placement
        :return: (bool) true if the VirtualMachine can fit, false otherwise
        """
        if self.current_capacity + vm_size <= self.capacity:
            return True
        return False

    def add_vm(self, vm):
        """
        Adds a VirtualMachine to this object and updates the current memory unit utilization of this object.
        :param vm: (VirtualMachine) the VM to add to this object
        :return: None
        """
        self.current_capacity += vm.get_size()
        self.vms.append(vm)

    def replicate_vm(self, vm):
        """
        Adds a copy of a VirtualMachine object to this object. This is done in order to make the reset of a simulation
        easier.
        :param vm:
        :return:
        """
        self.replicated_capacity += vm.get_size()
        self.current_capacity += vm.get_size()
        self.replicated_vms.append(vm)

    def set_edge_switch(self, switch):
        """
        Sets the edge switch this PhysicalMachine is connected to.
        :param switch: (PhysicalSwitch) switch connected to this object
        :return: None
        """
        self.edge_switch = switch

    def get_vms(self):
        """
        Returns a list of VirtualMachine objects currently in this object.
        :return: (list) a list of VirtualMachine objects
        """
        return self.vms


class PhysicalSwitch(Node, object):
    """
        Represents a physical switch in a topology.

        Args:
            self.pod_number (int): the pod number where this switch is located (counting from left-to-right)
            self.vertical_number (int): the column number of where this switch is located (counting from left-to-right)
            self.height_number (int): the row number of where this switch is located (counting from bottom-to-top)
    """

    def __init__(self, name=None):
        super(PhysicalSwitch, self).__init__(name)

        self.pod_number = 0
        self.vertical_number = 0
        self.height_number = 0

    def set_p(self, num):
        self.pod_number = num

    def set_v(self, num):
        self.vertical_number = num

    def set_h(self, num):
        self.height_number = num

    def get_p(self):
        return self.pod_number

    def get_v(self):
        return self.vertical_number

    def get_h(self):
        return self.height_number


class VMPair:
    """
        Represents a pair of two VMs that communicate in a topology.

        Args:
            self.vm_list (list): the pair of VirtualMachine objects that compose this object
            self.frequency (int): the communication frequency between the pair of VirtualMachines in self.vm_list
            self.replicated (bool): true if a VM in the pair has been replicated, false otherwise
            self.rep_vm_list (list): list of VM in this pair that have been replicated
    """

    def __init__(self, vm_list, freq=1):
        self.replicated = False
        self.vm_list = vm_list
        self.rep_vm_list = []
        self.frequency = freq

    def add_replicated_vm(self, vm):
        self.rep_vm_list.append(vm)

    def get_vms(self):
        return self.vm_list

    def get_communication_frequency(self):
        return self.frequency

    def set_replicated(self, bool_val):
        self.replicated = bool_val

    def reset_pair(self):
        self.replicated = False
        self.rep_vm_list = []
