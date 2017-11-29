import ClusterAlgorithm
import ExhastiveSearch
import MemoryReduction
import GreedyAlgorithm
import GraphSimulator
import GraphTopology

import matplotlib.pyplot as plt

import numpy as np
import scipy as sp
import scipy.stats

MAX_VM_SIZE = 1
NUM_SIMS = 5
K_VAL = 8


def mean_confidence_interval(data, confidence=0.95):
    """
    Takes in an array of floats and calculates the mean and confidence interval.
    :param data: an array of floats
    :param confidence: the percentage confidence interval to calculate
    :return: the mean and the mean minus/plus the confidence interval
    """
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1 + confidence)/2.0, n-1)
    return m, m-h, m+h


def calc_mean_and_width(data):
    """
    Given a vector calls a function to calculate the 95% confidence interval.
    :param data: a vector of floats
    :return: the mean of the data and width of the confidence interval
    """
    data_m, data_t, data_b = mean_confidence_interval(data, confidence=0.95)

    return data_m, np.abs(data_m - data_t)


def data_set_mean(b, g, c, m, e):
    """
    Given vectors of communication costs for each tested algorithm, this function returns the mean and width for
    each algorithm.

    :param b: vector of communication costs for the initial random distribution
    :param g: vector of communication costs for the Greedy algorithm
    :param c: vector of communication costs for the Cluster algorithm
    :param m: vector of communication costs for the MemReduce algorithm
    :param e: vector of communication costs for the Exhastive algorithm
    :return: the mean and width for each algorithm's cost vector
    """
    b_m, b_w = calc_mean_and_width(b)
    g_m, g_w = calc_mean_and_width(g)
    c_m, c_w = calc_mean_and_width(c)
    m_m, m_w = calc_mean_and_width(m)
    e_m, e_w = calc_mean_and_width(e)

    return b_m, b_w, g_m, g_w, c_m, c_w, m_m, m_w, e_m, e_w


def run_simulation(num_vm_pairs, host_capacity):
    """
    Creates a fat tree topology and randomly distribiutes a set of virtual machine pairs. Calculates and saves the cost
    associated with a random distribution as well as selection of 4 algorithms on the same random distribution.

    :param num_vm_pairs: the number of VM pairs to place inside the topology
    :param host_capacity: the number of VMs a physical host in the topology can hold
    :return: vectors of communication costs associated with an algorithm for a certain distribution of VMs
    """
    bd, gd, cd, mrd, ehd = [], [], [], [], []
    for i in range(0, NUM_SIMS):
        topo = GraphTopology.GraphTopology(k_val=K_VAL, n_p=num_vm_pairs, n_mb=0, max_vm_size=MAX_VM_SIZE,
                                           phys_host_cap=host_capacity)
        topo.create_topology()

        sim = GraphSimulator.GraphSimulator(topo, num_vm_pairs)
        sim.set_up_data_center()
        bd.append(sim.get_base_cost())

        gd.append(sim.pass_algorithm(GreedyAlgorithm.GreedyAlgorithm))
        sim.revert_state()

        cd.append(sim.pass_algorithm(ClusterAlgorithm.ClusterAlgorithm))
        sim.revert_state()

        mrd.append(sim.pass_algorithm(MemoryReduction.MemoryReduction))
        sim.revert_state()

        ehd.append(sim.pass_algorithm(ExhastiveSearch.ExhastiveSearch))

        print "SIM {}.{} done...".format(str(num_vm_pairs), str(i + 1))
    return bd, gd, cd, mrd, ehd


def plot_subset(mean_vector, width_vector, offset, bar_color, bar_hatch):
    """
    Adds all the data associated with an algorithm to a MathPlotLib object for plotting. For both vectors, the i-th
    element corresponds to the i-th simulation. The number 6 is added to the offset each iteration to account for the
    other 4 algorithms and a space between simulation parameters.

    :param mean_vector: a vector of means associated with different simulation parameters
    :param width_vector: a vector of widths, used for error bar, associated with different simulation parameters
    :param offset: offset from zero used to position the bar graph for each simulation
    :param bar_color: a string name to use to set the color of the bar
    :param bar_hatch: a string symbol to set the hatch
    :return: None
    """
    current_offset = offset
    for mean_val, width_val in zip(mean_vector, width_vector):
        plt.bar(current_offset, mean_val, yern=width_val, capsize=5, edgecolor=bar_color, hatch=bar_hatch, fill=False)
        offset += 6


def capacity_calc(factor, pairs):
    """
    Encapsulates capacity formula.

    :param factor: the factor used to set amount of excess memory available to place replicated VMs after initial VM
    placement
    :param pairs: the total number of pairs in the simulation
    :return: integer capacity for each individual physical host
    """
    return int(((2 * pairs) + (factor * pairs))/128)


def graph_simulation(factor):
    """
    Runs the replication simulation and graphs the result.

    :param factor: the factor used to set amount of excess memory available to place replicated VMs after initial VM
    placement
    :return: None
    """
    b1, g1, c1, m1, e1 = run_simulation(500, capacity_calc(factor, 500))
    b2, g2, c2, m2, e2 = run_simulation(1000, capacity_calc(factor, 1000))
    b3, g3, c3, m3, e3 = run_simulation(1500, capacity_calc(factor, 1500))
    b4, g4, c4, m4, e4 = run_simulation(2000, capacity_calc(factor, 2000))

    b1m, b1w, g1m, g1w, c1m, c1w, m1m, m1w, e1m, e1w = data_set_mean(b1, g1, c1, m1, e1)
    b2m, b2w, g2m, g2w, c2m, c2w, m2m, m2w, e2m, e2w = data_set_mean(b2, g2, c2, m2, e2)
    b3m, b3w, g3m, g3w, c3m, c3w, m3m, m3w, e3m, e3w = data_set_mean(b3, g3, c3, m3, e3)
    b4m, b4w, g4m, g4w, c4m, c4w, m4m, m4w, e4m, e4w = data_set_mean(b4, g4, c4, m4, e4)

    bm_data, bw_data = [b1m, b2m, b3m, b4m], [b1w, b2w, b3w, b4w]
    gm_data, gw_data = [g1m, g2m, g3m, g4m], [g1w, g2w, g3w, g4w]
    cm_data, cw_data = [c1m, c2m, c3m, c4m], [c1w, c2w, c3w, c4w]
    mm_data, mw_data = [m1m, m2m, m3m, m4m], [m1w, m2w, m3w, m4w]
    em_data, ew_data = [e1m, e2m, e3m, e4m], [e1w, e2w, e3w, e4w]

    plot_subset(bm_data, bw_data, 1, "red", "+")
    plot_subset(gm_data, gw_data, 2, "navy", "/")
    plot_subset(cm_data, cw_data, 3, "green", "x")
    plot_subset(mm_data, mw_data, 4, "magenta", ".")
    plot_subset(em_data, ew_data, 5, "black", "-")

    plt.xticks([3, 9, 15, 21, 27], ['500', '1000', '1500', '2000'], fontsize=20)
    font = {'family': 'normal', 'weight': 'bold', 'size': 15}
    plt.rc('font', **font)

    plt.gca().minorticks_on()
    plt.gca().grid(b=True, which='major', color='black', linestyle=':')
    plt.gca().grid(b=True, which='minor', color='black', linestyle=':', linewidth=0.5)
    plt.gca().set_axisbelow(True)
    plt.yticks(fontsize=20)
    plt.gca().set_yticks(plt.gca().get_yticks()[::2])
    plt.ylabel("Number of VM Pairs", fontsize=30)
    plt.xlabel("Average Communication Cost", fontsize=35)
    plt.show()


graph_simulation(0.50)
