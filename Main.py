import ClusterAlgorithm
import ExhastiveSearch
import MemoryReduction
import GreedyAlgorithm
import GraphSimulator
import GraphTopology

import matplotlib.patches as mpatches
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt

import time
import numpy as np
import scipy as sp
import scipy.stats

NUM_VM_PAIRS = 50
MAX_VM_SIZE = 1
NUM_SIMS = 100
HOST_CAP = 8
K_VAL = 4


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1 + confidence)/2.0, n-1)
    return m, m-h, m+h


def calc_mean_and_width(data):
    data_m, data_t, data_b = mean_confidence_interval(data, confidence=0.95)

    return data_m, np.abs(data_m - data_t)

base_data, greedy_data, cluster_data, mem_reduc_data, exhas_data = [], [], [], [], []
greedy_time, cluster_time, mem_reduc_time, exhas_time = 0, 0, 0, 0
for i in range(0, NUM_SIMS):
    topo = GraphTopology.GraphTopology(k_val=K_VAL, n_p=NUM_VM_PAIRS, n_mb=0, max_vm_size=MAX_VM_SIZE,
                                       phys_host_cap=HOST_CAP)
    topo.create_topology()

    sim = GraphSimulator.GraphSimulator(topo, NUM_VM_PAIRS)
    sim.set_up_data_center()

    base_data.append(sim.get_base_cost())

    greedy_start = time.time()
    greedy_data.append(sim.pass_algorithm(GreedyAlgorithm.GreedyAlgorithm))
    greedy_end = time.time()
    greedy_time += greedy_end - greedy_start
    sim.revert_state()

    cluster_start = time.time()
    cluster_data.append(sim.pass_algorithm(ClusterAlgorithm.ClusterAlgorithm))
    cluster_end = time.time()
    cluster_time += cluster_end - cluster_start
    sim.revert_state()

    mem_reduc_start = time.time()
    mem_reduc_data.append(sim.pass_algorithm(MemoryReduction.MemoryReduction))
    mem_reduc_end = time.time()
    mem_reduc_time += mem_reduc_end - mem_reduc_start
    sim.revert_state()

    exhas_start = time.time()
    exhas_data.append(sim.pass_algorithm(ExhastiveSearch.ExhastiveSearch))
    exhas_end = time.time()
    exhas_time += exhas_end - exhas_start

    print "SIM {} done...".format(str(i + 1))

print "GREEDY: {}".format(greedy_time)
print "CLUSTER: {}".format(cluster_time)
print "MEM REDUC: {}".format(mem_reduc_time)
print "EXHAS: {}".format(exhas_time)

base_mean, base_width = calc_mean_and_width(base_data)
greedy_mean, greedy_width = calc_mean_and_width(greedy_data)
cluster_mean, cluster_width = calc_mean_and_width(cluster_data)
mem_reduc_mean, mem_reduc_width = calc_mean_and_width(mem_reduc_data)
exhas_mean, exhas_width = calc_mean_and_width(exhas_data)

plt.bar(1, base_mean, yerr=base_width, capsize=5, edgecolor="red", hatch="+", fill=False)
plt.bar(2, greedy_mean, yerr=greedy_width, capsize=5, edgecolor="navy", hatch="/", fill=False)
plt.bar(3, cluster_mean, yerr=cluster_width, capsize=5, edgecolor="green", hatch="x", fill=False)
plt.bar(4, mem_reduc_mean, yerr=mem_reduc_width, capsize=5, edgecolor="magenta", hatch=".", fill=False)
plt.bar(5, exhas_mean, yerr=exhas_width, capsize=5, edgecolor="black", hatch="-", fill=False)


plt.xticks([1, 2, 3, 4, 5], ['Base', 'Greedy', 'Cluster', 'MemReduce', "Exhas"], fontsize=20)
font = {'family': 'normal', 'weight': 'bold', 'size': 15}
plt.rc('font', **font)

plt.gca().minorticks_on()
plt.gca().grid(b=True, which='major', color='black', linestyle=':')
plt.gca().grid(b=True, which='minor', color='black', linestyle=':', linewidth=0.5)
plt.gca().set_axisbelow(True)
plt.yticks(fontsize=20)
plt.gca().set_yticks(plt.gca().get_yticks()[::2])
# plt.ylabel('Total Energy Cost of VM Pairs', fontsize=30)
# plt.xlabel('Resource Capacity of PMs', fontsize=35)
plt.show()




