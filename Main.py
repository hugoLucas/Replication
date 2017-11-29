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
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1 + confidence)/2.0, n-1)
    return m, m-h, m+h


def calc_mean_and_width(data):
    data_m, data_t, data_b = mean_confidence_interval(data, confidence=0.95)

    return data_m, np.abs(data_m - data_t)


def run_simulation(num_vm_pairs, host_capacity):
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


def data_set_mean(b, g, c, m, e):
    b_m, b_w = calc_mean_and_width(b)
    g_m, g_w = calc_mean_and_width(g)
    c_m, c_w = calc_mean_and_width(c)
    m_m, m_w = calc_mean_and_width(m)
    e_m, e_w = calc_mean_and_width(e)

    return b_m, b_w, g_m, g_w, c_m, c_w, m_m, m_w, e_m, e_w


def plot_subset(mean_vector, width_vector, offset, bar_color, bar_hatch):
    current_offset = offset
    for mean_val, width_val in zip(mean_vector, width_vector):
        plt.bar(current_offset, mean_val, yern=width_val, capsize=5, edgecolor=bar_color, hatch=bar_hatch, fill=False)
        offset += 6


def graph_simulation(capacity, title_x, title_y):
    b1, g1, c1, m1, e1 = run_simulation(500, capacity)
    b2, g2, c2, m2, e2 = run_simulation(1000, capacity)
    b3, g3, c3, m3, e3 = run_simulation(1500, capacity)
    b4, g4, c4, m4, e4 = run_simulation(2000, capacity)

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
    plt.ylabel(title_x, fontsize=30)
    plt.xlabel(title_y, fontsize=35)
    plt.show()




