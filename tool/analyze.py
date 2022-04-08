import sys
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import csv
import statistics
import glob


stats = defaultdict(lambda: defaultdict(dict))
stats2 = defaultdict(lambda: defaultdict(dict))

gpu_map = {
        "p2.xlarge" : "K80-1",
        "chameleon.xlarge" : "gpus-11",
        "p2.8xlarge" : "K80-8",
        "p2.8xlarge_2" : "K80-8_2",
        "p2.16xlarge" : "K80-16",
        "p3.2xlarge" : "V100-1",
        "p3.8xlarge" : "V100-4",
        "p3.16xlarge" : "V100-8"}

instances = []

def process_json(model, gpu, json_path):

    with open(json_path) as fd:
        dagJson = json.load(fd)

    stats[model][gpu]["TRAIN_SPEED_INGESTION"] = dagJson["SPEED_INGESTION"]
    stats[model][gpu]["TRAIN_SPEED_DISK"]  = dagJson["SPEED_DISK"]
    stats[model][gpu]["TRAIN_SPEED_CACHED"] = dagJson["SPEED_CACHED"]
    stats[model][gpu]["DISK_THR"] = dagJson["DISK_THR"]
#    stats[model][gpu]["MEM_THR"] = dagJson["MEM_THR"]
    stats[model][gpu]["TRAIN_TIME_INGESTION"] = dagJson["RUN1"]["TRAIN"]
    stats[model][gpu]["TRAIN_TIME_DISK"] = dagJson["RUN2"]["TRAIN"]
    stats[model][gpu]["TRAIN_TIME_CACHED"] = dagJson["RUN3"]["TRAIN"]
    stats[model][gpu]["CPU_UTIL_DISK_PCT"] = dagJson["RUN2"]["CPU"]
    stats[model][gpu]["CPU_UTIL_CACHED_PCT"] = dagJson["RUN3"]["CPU"]
    stats[model][gpu]["GPU_UTIL_DISK_PCT"] = dagJson["RUN2"]["GPU_UTIL"]
    stats[model][gpu]["GPU_UTIL_CACHED_PCT"] = dagJson["RUN3"]["GPU_UTIL"]
    stats[model][gpu]["GPU_MEM_UTIL_DISK_PCT"] = dagJson["RUN2"]["GPU_MEM_UTIL"]
    stats[model][gpu]["GPU_MEM_UTIL_CACHED_PCT"] = dagJson["RUN3"]["GPU_MEM_UTIL"]
    stats[model][gpu]["MEMCPY_TIME"] = dagJson["RUN1"]["MEMCPY"]
    stats[model][gpu]["COMPUTE_TIME"] = dagJson["RUN3"]["COMPUTE"]
    stats[model][gpu]["COMPUTE_BWD_TIME"] = dagJson["RUN3"]["COMPUTE_BWD"]
    stats[model][gpu]["COMPUTE_FWD_TIME"] = stats[model][gpu]["COMPUTE_TIME"] - stats[model][gpu]["COMPUTE_BWD_TIME"]

    stats[model][gpu]["PREP_STALL_TIME"] = dagJson["RUN3"]["TRAIN"] - dagJson["RUN1"]["TRAIN"]
    stats[model][gpu]["FETCH_STALL_TIME"] = dagJson["RUN2"]["TRAIN"] - stats[model][gpu]["PREP_STALL_TIME"]
    if "RUN0" in dagJson:
        stats[model][gpu]["INTERCONNECT_STALL_TIME"] = dagJson["RUN1"]["TRAIN"] - dagJson["RUN0"]["TRAIN"]

    stats[model][gpu]["PREP_STALL_PCT"] = stats[model][gpu]["PREP_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_CACHED"] * 100
    stats[model][gpu]["FETCH_STALL_PCT"] = stats[model][gpu]["FETCH_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_DISK"] * 100
    stats[model][gpu]["INTERCONNECT_STALL_PCT"] = stats[model][gpu]["INTERCONNECT_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_INGESTION"] * 100



def process_json2(model, instance, json_path):

    gpu = gpu_map[instance]
    with open(json_path) as fd:
        dagJson = json.load(fd)

    stats[model][gpu]["TRAIN_SPEED_INGESTION"] = dagJson["SPEED_INGESTION"]
    stats[model][gpu]["TRAIN_SPEED_DISK"]  = dagJson["SPEED_DISK"]
    stats[model][gpu]["TRAIN_SPEED_CACHED"] = dagJson["SPEED_CACHED"]
    stats[model][gpu]["DISK_THR"] = dagJson["DISK_THR"]
    stats[model][gpu]["TRAIN_TIME_INGESTION"] = dagJson["RUN1"]["TRAIN"]
    stats[model][gpu]["TRAIN_TIME_DISK"] = dagJson["RUN2"]["TRAIN"]
    stats[model][gpu]["TRAIN_TIME_CACHED"] = dagJson["RUN3"]["TRAIN"]
    stats[model][gpu]["MEM_DISK"] = dagJson["RUN2"]["MEM"]
    stats[model][gpu]["PCACHE_DISK"] = dagJson["RUN2"]["PCACHE"]
    stats[model][gpu]["MEM_CACHED"] = dagJson["RUN3"]["MEM"]
    stats[model][gpu]["PCACHE_CACHED"] = dagJson["RUN3"]["PCACHE"]
    stats[model][gpu]["READ_WRITE_DISK"] = dagJson["RUN2"]["READ"] + dagJson["RUN2"]["WRITE"]
    stats[model][gpu]["IO_WAIT_DISK"] = dagJson["RUN2"]["IO_WAIT"]
    stats[model][gpu]["READ_WRITE_CACHED"] = dagJson["RUN3"]["READ"] + dagJson["RUN3"]["WRITE"]
    stats[model][gpu]["IO_WAIT_CACHED"] = dagJson["RUN3"]["IO_WAIT"]

    stats[model][gpu]["CPU_UTIL_DISK_PCT"] = dagJson["RUN2"]["CPU"]
    stats[model][gpu]["CPU_UTIL_CACHED_PCT"] = dagJson["RUN3"]["CPU"]
    stats[model][gpu]["GPU_UTIL_DISK_PCT"] = dagJson["RUN2"]["GPU_UTIL"]
    stats[model][gpu]["GPU_UTIL_CACHED_PCT"] = dagJson["RUN3"]["GPU_UTIL"]
    stats[model][gpu]["GPU_MEM_UTIL_DISK_PCT"] = dagJson["RUN2"]["GPU_MEM_UTIL"]
    stats[model][gpu]["GPU_MEM_UTIL_CACHED_PCT"] = dagJson["RUN3"]["GPU_MEM_UTIL"]

    stats[model][gpu]["MEMCPY_TIME"] = dagJson["RUN1"]["MEMCPY"]
    stats[model][gpu]["COMPUTE_TIME"] = dagJson["RUN3"]["COMPUTE"]
    stats[model][gpu]["COMPUTE_BWD_TIME"] = dagJson["RUN3"]["COMPUTE_BWD"]
    stats[model][gpu]["COMPUTE_FWD_TIME"] = stats[model][gpu]["COMPUTE_TIME"] - stats[model][gpu]["COMPUTE_BWD_TIME"]

    stats[model][gpu]["CPU_UTIL_DISK_LIST"] = dagJson["RUN2"]["CPU_LIST"]
    stats[model][gpu]["CPU_UTIL_CACHED_LIST"] = dagJson["RUN3"]["CPU_LIST"]
    stats[model][gpu]["GPU_UTIL_DISK_LIST"] = dagJson["RUN2"]["GPU_UTIL_LIST"]
    stats[model][gpu]["GPU_UTIL_CACHED_LIST"] = dagJson["RUN3"]["GPU_UTIL_LIST"]
    stats[model][gpu]["GPU_MEM_UTIL_DISK_LIST"] = dagJson["RUN2"]["GPU_MEM_UTIL_LIST"]
    stats[model][gpu]["GPU_MEM_UTIL_CACHED_LIST"] = dagJson["RUN3"]["GPU_MEM_UTIL_LIST"]
    stats[model][gpu]["READ_WRITE_LIST_DISK"] = dagJson["RUN2"]["READ_LIST"] + dagJson["RUN2"]["WRITE_LIST"]
    stats[model][gpu]["READ_WRITE_LIST_CACHED"] = dagJson["RUN3"]["READ_LIST"] + dagJson["RUN3"]["WRITE_LIST"]
    stats[model][gpu]["IO_WAIT_LIST_DISK"] = dagJson["RUN2"]["IO_WAIT_LIST"]
    stats[model][gpu]["IO_WAIT_LIST_CACHED"] = dagJson["RUN3"]["IO_WAIT_LIST"]

    stats[model][gpu]["PREP_STALL_TIME"] = dagJson["RUN3"]["TRAIN"] - dagJson["RUN1"]["TRAIN"]
    stats[model][gpu]["FETCH_STALL_TIME"] = dagJson["RUN2"]["TRAIN"] - stats[model][gpu]["PREP_STALL_TIME"]
    if "RUN0" in dagJson:
        stats[model][gpu]["INTERCONNECT_STALL_TIME"] = dagJson["RUN1"]["TRAIN"] - dagJson["RUN0"]["TRAIN"]

    stats[model][gpu]["PREP_STALL_PCT"] = stats[model][gpu]["PREP_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_CACHED"] * 100
    stats[model][gpu]["FETCH_STALL_PCT"] = stats[model][gpu]["FETCH_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_DISK"] * 100
    if "INTERCONNECT_STALL_TIME" in stats[model][gpu]:
        stats[model][gpu]["INTERCONNECT_STALL_PCT"] = stats[model][gpu]["INTERCONNECT_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_INGESTION"] * 100


def process_csv(model, instance, csv_path):

    gpu = gpu_map[instance]
    stats[model][gpu]["DATA_TIME_LIST"] = []
    stats[model][gpu]["COMPUTE_TIME_LIST"] = []
    stats[model][gpu]["COMPUTE_TIME_FWD_LIST"] = []
    stats[model][gpu]["COMPUTE_TIME_BWD_LIST"] = []

    files = glob.glob(csv_path + 'time*.csv')
    csv_readers = []

    for csv_file in files:
        csv_reader = csv.reader(open(csv_file))
        next(csv_reader)
        csv_readers.append(csv_reader)

    num_lines = min(len(open(files[i]).readlines()) for i in range(len(files)))

    for i in range(num_lines-1):
        
        data_time = []
        compute_time = []
        compute_fwd_time = []
        compute_bwd_time = []

        for csv_reader in csv_readers:

            row = next(csv_reader)

            data_time.append(float(row[1]))
            compute_time.append(float(row[2]))
            compute_fwd_time.append(float(row[2]) - float(row[3]))
            compute_bwd_time.append(float(row[3]))

        stats[model][gpu]["DATA_TIME_LIST"].append(statistics.mean(data_time))
        stats[model][gpu]["COMPUTE_TIME_LIST"].append(statistics.mean(compute_time))
        stats[model][gpu]["COMPUTE_TIME_FWD_LIST"].append(statistics.mean(compute_fwd_time))
        stats[model][gpu]["COMPUTE_TIME_BWD_LIST"].append(statistics.mean(compute_bwd_time))

def add_text(X, Y, axs):
    for idx, value in enumerate(X):
        axs.text(value, Y[idx]+2, str(int(Y[idx])))

def compare_instances():

    models = list(stats.keys())

    for instance in instances:

        gpu = gpu_map[instance]

        for model in models:

            if gpu not in stats[model]:
                del stats[model]


    fig1, axs1 = plt.subplots(3, 1, figsize=(30,20))
    fig2, axs2 = plt.subplots(3, 1, figsize=(30,20))
    fig3, axs3 = plt.subplots(3, 1, figsize=(30,20))
    fig4, axs4 = plt.subplots(3, 1, figsize=(30,20))
    fig5, axs5 = plt.subplots(3, 1, figsize=(30,20))
    fig6, axs6 = plt.subplots(3, 1, figsize=(30,20))
    fig7, axs7 = plt.subplots(figsize=(30,20))

    X = [model for model in stats.keys()]
    X_axis = np.arange(len(X))

    diff = 0

    for instance in instances:
        
        gpu = gpu_map[instance]
        print(gpu)
        
        Y_PREP_STALL_PCT = [stats[model][gpu]["PREP_STALL_PCT"] for model in X]
        Y_FETCH_STALL_PCT = [stats[model][gpu]["FETCH_STALL_PCT"] for model in X]
        if "INTERCONNECT_STALL_PCT" in stats[model][gpu]:
            Y_INTERCONNECT_STALL_PCT = [stats[model][gpu]["INTERCONNECT_STALL_PCT"] for model in X]
        Y_TRAIN_TIME_DISK = [stats[model][gpu]["TRAIN_TIME_DISK"] for model in X]
        Y_TRAIN_TIME_CACHED = [stats[model][gpu]["TRAIN_TIME_CACHED"] for model in X]
        Y_DISK_THR = [stats[model][gpu]["DISK_THR"] for model in X]
        Y_TRAIN_SPEED_INGESTION = [stats[model][gpu]["TRAIN_SPEED_INGESTION"] for model in X]
        Y_TRAIN_SPEED_DISK = [stats[model][gpu]["TRAIN_SPEED_DISK"] for model in X]
        Y_TRAIN_SPEED_CACHED = [stats[model][gpu]["TRAIN_SPEED_CACHED"] for model in X]
        Y_CPU_UTIL_DISK_PCT = [stats[model][gpu]["CPU_UTIL_DISK_PCT"] for model in X]
        Y_CPU_UTIL_CACHED_PCT = [stats[model][gpu]["CPU_UTIL_CACHED_PCT"] for model in X]
        Y_GPU_UTIL_DISK_PCT = [stats[model][gpu]["GPU_UTIL_DISK_PCT"] for model in X]
        Y_GPU_UTIL_CACHED_PCT = [stats[model][gpu]["GPU_UTIL_CACHED_PCT"] for model in X]
        Y_GPU_MEM_UTIL_DISK_PCT = [stats[model][gpu]["GPU_MEM_UTIL_DISK_PCT"] for model in X]
        Y_GPU_MEM_UTIL_CACHED_PCT = [stats[model][gpu]["GPU_MEM_UTIL_CACHED_PCT"] for model in X]
        Y_MEMCPY_TIME = [stats[model][gpu]["MEMCPY_TIME"] for model in X]
        Y_COMPUTE_TIME = [stats[model][gpu]["COMPUTE_TIME"] for model in X]
        Y_COMPUTE_FWD_TIME = [stats[model][gpu]["COMPUTE_FWD_TIME"] for model in X]
        Y_COMPUTE_BWD_TIME = [stats[model][gpu]["COMPUTE_BWD_TIME"] for model in X]

        axs1[0].bar(X_axis-0.2 + diff , Y_PREP_STALL_PCT, 0.2, label = instance)
        axs1[1].bar(X_axis-0.2 + diff, Y_FETCH_STALL_PCT, 0.2, label = instance)
        add_text(X_axis-0.25 + diff, Y_PREP_STALL_PCT, axs1[0])
        add_text(X_axis-0.25 + diff, Y_FETCH_STALL_PCT, axs1[1])

        if "INTERCONNECT_STALL_PCT" in stats[model][gpu]:
            axs1[2].bar(X_axis-0.2 + diff, Y_INTERCONNECT_STALL_PCT, 0.2, label = instance)
            add_text(X_axis-0.25 + diff, Y_INTERCONNECT_STALL_PCT, axs1[2])

        axs2[0].bar(X_axis-0.2 + diff , Y_TRAIN_TIME_DISK, 0.2, label = instance)
        axs2[1].bar(X_axis-0.2 + diff, Y_TRAIN_TIME_CACHED, 0.2, label = instance)
        axs2[2].bar(X_axis-0.2 + diff, Y_DISK_THR, 0.2, label = instance)
        add_text(X_axis-0.25 + diff, Y_TRAIN_TIME_DISK, axs2[0])
        add_text(X_axis-0.25 + diff, Y_TRAIN_TIME_CACHED, axs2[1])
        add_text(X_axis-0.25 + diff, Y_DISK_THR, axs2[2])

        axs3[0].bar(X_axis-0.2 + diff, Y_TRAIN_SPEED_INGESTION, 0.2, label = instance)
        axs3[1].bar(X_axis-0.2 + diff , Y_TRAIN_SPEED_DISK, 0.2, label = instance)
        axs3[2].bar(X_axis-0.2 + diff, Y_TRAIN_SPEED_CACHED, 0.2, label = instance)
        add_text(X_axis-0.25 + diff, Y_TRAIN_SPEED_INGESTION, axs3[0])
        add_text(X_axis-0.25 + diff, Y_TRAIN_SPEED_DISK, axs3[1])
        add_text(X_axis-0.25 + diff, Y_TRAIN_SPEED_CACHED, axs3[2])

        axs4[0].bar(X_axis-0.2 + diff , Y_CPU_UTIL_DISK_PCT, 0.2, label = instance)
        axs4[1].bar(X_axis-0.2 + diff , Y_GPU_UTIL_DISK_PCT, 0.2, label = instance)
        axs4[2].bar(X_axis-0.2 + diff , Y_GPU_MEM_UTIL_DISK_PCT, 0.2, label = instance)
        add_text(X_axis-0.25 + diff, Y_CPU_UTIL_DISK_PCT, axs4[0])
        add_text(X_axis-0.25 + diff, Y_GPU_UTIL_DISK_PCT, axs4[1])
        add_text(X_axis-0.25 + diff, Y_GPU_MEM_UTIL_DISK_PCT, axs4[2])

        axs5[0].bar(X_axis-0.2 + diff , Y_CPU_UTIL_CACHED_PCT, 0.2, label = instance)
        axs5[1].bar(X_axis-0.2 + diff , Y_GPU_UTIL_CACHED_PCT, 0.2, label = instance)
        axs5[2].bar(X_axis-0.2 + diff , Y_GPU_MEM_UTIL_CACHED_PCT, 0.2, label = instance)
        add_text(X_axis-0.25 + diff, Y_CPU_UTIL_CACHED_PCT, axs5[0])
        add_text(X_axis-0.25 + diff, Y_GPU_UTIL_CACHED_PCT, axs5[1])
        add_text(X_axis-0.25 + diff, Y_GPU_MEM_UTIL_CACHED_PCT, axs5[2])

        axs6[0].bar(X_axis-0.2 + diff , Y_MEMCPY_TIME, 0.2, label = instance)
        axs6[1].bar(X_axis-0.2 + diff , Y_COMPUTE_FWD_TIME, 0.2, label = instance)
        axs6[2].bar(X_axis-0.2 + diff , Y_COMPUTE_BWD_TIME, 0.2, label = instance)
        add_text(X_axis-0.25 + diff, Y_MEMCPY_TIME, axs6[0])
        add_text(X_axis-0.25 + diff, Y_COMPUTE_FWD_TIME, axs6[1])
        add_text(X_axis-0.25 + diff, Y_COMPUTE_BWD_TIME, axs6[2])

        #axs7.bar(X_axis-0.2 + diff , Y_MEMCPY_TIME, 0.2, label = instance)
        #axs7.bar(X_axis-0.2 + diff , Y_COMPUTE_FWD_TIME, 0.2, bottom = Y_MEMCPY_TIME, label = instance)
        #axs7.bar(X_axis-0.2 + diff , Y_COMPUTE_BWD_TIME, 0.2, bottom = Y_COMPUTE_FWD_TIME, label = instance)

        axs7.bar(X_axis-0.2 + diff , Y_MEMCPY_TIME, 0.2, color = 'g', edgecolor='black')
        axs7.bar(X_axis-0.2 + diff , Y_COMPUTE_FWD_TIME, 0.2, bottom = Y_MEMCPY_TIME, color = 'b', edgecolor='black')
        axs7.bar(X_axis-0.2 + diff , Y_COMPUTE_BWD_TIME, 0.2, bottom = Y_COMPUTE_FWD_TIME, color = 'c', edgecolor='black')

        diff += 0.2

    axs1[0].set_xticks(X_axis)
    axs1[0].set_xticklabels(X)
    axs1[0].set_xlabel("Models")
    axs1[0].set_ylabel("Percentage")
    axs1[0].set_title("Prep stall comparison")
    axs1[0].legend()

    axs1[1].set_xticks(X_axis)
    axs1[1].set_xticklabels(X)
    axs1[1].set_xlabel("Models")
    axs1[1].set_ylabel("Percentage")
    axs1[1].set_title("Fetch stall comparison")
    axs1[1].legend()

    axs1[2].set_xticks(X_axis)
    axs1[2].set_xticklabels(X)
    axs1[2].set_xlabel("Models")
    axs1[2].set_ylabel("Percentage")
    axs1[2].set_title("Interconnect stall comparison")
    axs1[2].legend()

    fig1.suptitle("Stall comparison" , fontsize=20, fontweight ="bold")
    fig1.savefig("figures/stall_comparison")
    
    axs2[0].set_xticks(X_axis)
    axs2[0].set_xticklabels(X)
    axs2[0].set_ylabel("Time")
    axs2[0].set_title("Training time disk comparison")
    axs2[0].legend()

    axs2[1].set_xticks(X_axis)
    axs2[1].set_xticklabels(X)
    axs2[1].set_ylabel("Time")
    axs2[1].set_title("Training time cached comparison")
    axs2[1].legend()

    axs2[2].set_xticks(X_axis)
    axs2[2].set_xticklabels(X)
    axs2[2].set_ylabel("Throughput")
    axs2[2].set_title("Disk throughput comparison")
    axs2[2].legend()

    fig2.suptitle("Training time comparison" , fontsize=20, fontweight ="bold")
    fig2.savefig("figures/training_time")

    axs3[0].set_xticks(X_axis)
    axs3[0].set_xticklabels(X)
    axs3[0].set_ylabel("Samples/sec")
    axs3[0].set_title("Training speed ingestion comparison")
    axs3[0].legend()

    axs3[1].set_xticks(X_axis)
    axs3[1].set_xticklabels(X)
    axs3[1].set_ylabel("Samples/sec")
    axs3[1].set_title("Training speed disk comparison")
    axs3[1].legend()

    axs3[2].set_xticks(X_axis)
    axs3[2].set_xticklabels(X)
    axs3[2].set_ylabel("Samples/sec")
    axs3[2].set_title("Training speed cached comparison")
    axs3[2].legend()

    fig3.suptitle("Training speed comparison", fontsize=20, fontweight ="bold")
    fig3.savefig("figures/training_speed")

    axs4[0].set_xticks(X_axis)
    axs4[0].set_xticklabels(X)
    axs4[0].set_ylabel("Average CPU utilization")
    axs4[0].set_title("CPU utilization comparison")
    axs4[0].legend()

    axs4[1].set_xticks(X_axis)
    axs4[1].set_xticklabels(X)
    axs4[1].set_ylabel("Average GPU utilization")
    axs4[1].set_title("GPU utilization comparison")
    axs4[1].legend()

    axs4[2].set_xticks(X_axis)
    axs4[2].set_xticklabels(X)
    axs4[2].set_ylabel("Average GPU memory utilization")
    axs4[2].set_title("GPU memory utilization comparison")
    axs4[2].legend()

    fig4.suptitle("CPU and GPU utilization DISK comparison", fontsize=20, fontweight ="bold")
    fig4.savefig("figures/cpu_gpu_util_disk")

    axs5[0].set_xticks(X_axis)
    axs5[0].set_xticklabels(X)
    axs5[0].set_ylabel("Average CPU utilization")
    axs5[0].set_title("CPU utilization comparison")
    axs5[0].legend()

    axs5[1].set_xticks(X_axis)
    axs5[1].set_xticklabels(X)
    axs5[1].set_ylabel("Average GPU utilization")
    axs5[1].set_title("GPU utilization comparison")
    axs5[1].legend()

    axs5[2].set_xticks(X_axis)
    axs5[2].set_xticklabels(X)
    axs5[2].set_ylabel("Average GPU memory utilization")
    axs5[2].set_title("GPU memory utilization comparison")
    axs5[2].legend()

    fig5.suptitle("CPU and GPU utilization CACHED comparison", fontsize=20, fontweight ="bold")
    fig5.savefig("figures/cpu_gpu_util_cached")

    axs6[0].set_xticks(X_axis)
    axs6[0].set_xticklabels(X)
    axs6[0].set_ylabel("Avg Total Time (Seconds)")
    axs6[0].set_title("Memcpy time")
    axs6[0].legend()

    axs6[1].set_xticks(X_axis)
    axs6[1].set_xticklabels(X)
    axs6[1].set_ylabel("Avg Total Time (Seconds)")
    axs6[1].set_title("Fwd propogation compute time")
    axs6[1].legend()

    axs6[2].set_xticks(X_axis)
    axs6[2].set_xticklabels(X)
    axs6[2].set_ylabel("Avg Total Time (Seconds)")
    axs6[2].set_title("Bwd propogation compute time")
    axs6[2].legend()

    fig6.suptitle("Time comparison", fontsize=20, fontweight ="bold")
    fig6.savefig("figures/memcpy_compute_time_comparison")

    axs7.set_xticks(X_axis)
    axs7.set_xticklabels(X, fontsize=20)
    axs7.set_ylabel("Avg Total Time (Seconds)", fontsize=20)
    axs7.set_title("Stacked time comparison")
    leg = ["Memcpy Time", "Fwd Propogation Time", "Bwd Propogation Time"]
    axs7.legend(leg, fontsize=20)

    fig7.suptitle("Time comparison", fontsize=20, fontweight ="bold")
    fig7.savefig("figures/stacked_time_comparison")

    plt.show()

def compare_models():

    models = list(stats.keys())
    max_dstat_len = 0
    max_nvidia_len = 0
    max_itrs = 0

    X = ["Disk Throughput", "Train speed", "Memory", "Page cache"]
    X_IO = ["Read Write", "IOWait"]
    X_ITR = ["Data time", "Fwd Prop Time", "Bwd Prop Time"]
    styles = ['r--', 'b--']
    colors = [['green', 'red', 'blue'], ['orange', 'cyan', 'purple']]

#    models = ["alexnet"]

    for model in models:

        for instance in instances:
            gpu = gpu_map[instance]
            if gpu not in stats[model]:
                del stats[model]
                continue


            max_dstat_len = max(max_dstat_len, len(stats[model][gpu]["CPU_UTIL_DISK_LIST"]))
            max_dstat_len = max(max_dstat_len, len(stats[model][gpu]["CPU_UTIL_CACHED_LIST"]))
            max_nvidia_len = max(max_nvidia_len, len(stats[model][gpu]["GPU_UTIL_DISK_LIST"]))
            max_nvidia_len = max(max_nvidia_len, len(stats[model][gpu]["GPU_UTIL_CACHED_LIST"]))
            max_itrs = max(max_itrs, len(stats[model][gpu]["DATA_TIME_LIST"]))

        fig1, axs1 = plt.subplots(3, 2, figsize=(30,20))
        fig2, axs2 = plt.subplots(3, 2, figsize=(30,20))
        #fig3, axs3 = plt.subplots(3, 1, figsize=(30,20))
        fig3, axs3 = plt.subplots(figsize=(60,40))

        X_dstat_axis = np.arange(max_dstat_len)
        X_nvidia_axis = np.arange(max_nvidia_len)
        X_metrics_axis = np.arange(len(X))
        X_metrics_io_axis = np.arange(len(X_IO))
        X_itrs_axis = np.arange(max_itrs)
        diff = 0
        idx = 0

        for instance in instances:
            
            gpu = gpu_map[instance]
            if gpu not in stats[model]:
                continue

            style = styles[idx]
            color = colors[idx]
            idx += 1

            """
            if instance == "p2.xlarge":
                style = 'r--'
                color = ['green', 'red', 'blue']
            elif instance == "p3.2xlarge":
                style = 'b--'
                color = ['orange', 'cyan', 'purple']
            """

            overlapping = 0.50
        
            Y_METRICS_DISK = []
            Y_METRICS_CACHED = []
            Y_METRICS_IO_DISK = []
            Y_METRICS_IO_CACHED = []

            print(model, gpu)

            Y_METRICS_DISK.append(stats[model][gpu]["DISK_THR"])
            Y_METRICS_DISK.append(stats[model][gpu]["TRAIN_SPEED_DISK"])
            Y_METRICS_DISK.append(stats[model][gpu]["MEM_DISK"])
            Y_METRICS_DISK.append(stats[model][gpu]["PCACHE_DISK"])
            Y_METRICS_IO_DISK.append(stats[model][gpu]["READ_WRITE_DISK"])
            Y_METRICS_IO_DISK.append(stats[model][gpu]["IO_WAIT_DISK"])
            
            Y_METRICS_CACHED.append(stats[model][gpu]["DISK_THR"])
            Y_METRICS_CACHED.append(stats[model][gpu]["TRAIN_SPEED_CACHED"])
            Y_METRICS_CACHED.append(stats[model][gpu]["MEM_CACHED"])
            Y_METRICS_CACHED.append(stats[model][gpu]["PCACHE_CACHED"])
            Y_METRICS_IO_CACHED.append(stats[model][gpu]["READ_WRITE_CACHED"])
            Y_METRICS_IO_CACHED.append(stats[model][gpu]["IO_WAIT_CACHED"])

            Y_CPU_UTIL_DISK = stats[model][gpu]["CPU_UTIL_DISK_LIST"]
            Y_CPU_UTIL_CACHED = stats[model][gpu]["CPU_UTIL_CACHED_LIST"]

            Y_GPU_UTIL_DISK = stats[model][gpu]["GPU_UTIL_DISK_LIST"]
            Y_GPU_UTIL_CACHED = stats[model][gpu]["GPU_UTIL_CACHED_LIST"]

            Y_GPU_MEM_UTIL_DISK = stats[model][gpu]["GPU_MEM_UTIL_DISK_LIST"]
            Y_GPU_MEM_UTIL_CACHED = stats[model][gpu]["GPU_MEM_UTIL_CACHED_LIST"]

            Y_IO_WAIT_LIST_DISK = stats[model][gpu]["IO_WAIT_LIST_DISK"]
            Y_IO_WAIT_LIST_CACHED = stats[model][gpu]["IO_WAIT_LIST_CACHED"]

            Y_DATA_TIME_LIST = stats[model][gpu]["DATA_TIME_LIST"]
            Y_COMPUTE_TIME_FWD_LIST = stats[model][gpu]["COMPUTE_TIME_FWD_LIST"]
            Y_COMPUTE_TIME_BWD_LIST = stats[model][gpu]["COMPUTE_TIME_BWD_LIST"]

            if len(Y_CPU_UTIL_DISK) < max_dstat_len:
                Y_CPU_UTIL_DISK.extend([0] * (max_dstat_len - len(Y_CPU_UTIL_DISK)))
            if len(Y_CPU_UTIL_CACHED) < max_dstat_len:
                Y_CPU_UTIL_CACHED.extend([0] * (max_dstat_len - len(Y_CPU_UTIL_CACHED)))
            if len(Y_GPU_UTIL_DISK) < max_nvidia_len:
                Y_GPU_UTIL_DISK.extend([0] * (max_nvidia_len - len(Y_GPU_UTIL_DISK)))
            if len(Y_GPU_UTIL_CACHED) < max_nvidia_len:
                Y_GPU_UTIL_CACHED.extend([0] * (max_nvidia_len - len(Y_GPU_UTIL_CACHED)))
            if len(Y_GPU_MEM_UTIL_DISK) < max_nvidia_len:
                Y_GPU_MEM_UTIL_DISK.extend([0] * (max_nvidia_len - len(Y_GPU_MEM_UTIL_DISK)))
            if len(Y_GPU_MEM_UTIL_CACHED) < max_nvidia_len:
                Y_GPU_MEM_UTIL_CACHED.extend([0] * (max_nvidia_len - len(Y_GPU_MEM_UTIL_CACHED)))
            if len(Y_IO_WAIT_LIST_DISK) < max_dstat_len:
                Y_IO_WAIT_LIST_DISK.extend([0] * (max_dstat_len - len(Y_IO_WAIT_LIST_DISK)))
            if len(Y_IO_WAIT_LIST_CACHED) < max_dstat_len:
                Y_IO_WAIT_LIST_CACHED.extend([0] * (max_dstat_len - len(Y_IO_WAIT_LIST_CACHED)))
            if len(Y_DATA_TIME_LIST) < max_itrs:
                Y_DATA_TIME_LIST.extend([0] * (max_itrs - len(Y_DATA_TIME_LIST)))
            if len(Y_COMPUTE_TIME_FWD_LIST) < max_itrs:
                Y_COMPUTE_TIME_FWD_LIST.extend([0] * (max_itrs - len(Y_COMPUTE_TIME_FWD_LIST)))
            if len(Y_COMPUTE_TIME_BWD_LIST) < max_itrs:
                Y_COMPUTE_TIME_BWD_LIST.extend([0] * (max_itrs - len(Y_COMPUTE_TIME_BWD_LIST)))

            axs1[0,0].bar(X_metrics_axis -0.2 + diff, Y_METRICS_CACHED, 0.2, label = instance)
            axs1[0,1].plot(X_dstat_axis, Y_CPU_UTIL_CACHED, style, alpha=overlapping, label = instance)
            axs1[1,0].plot(X_nvidia_axis, Y_GPU_UTIL_CACHED, style, alpha=overlapping, label = instance)
            axs1[1,1].plot(X_nvidia_axis, Y_GPU_MEM_UTIL_CACHED, style, alpha=overlapping, label = instance)
            axs1[2,0].bar(X_metrics_io_axis -0.2 + diff, Y_METRICS_IO_CACHED, 0.2, label = instance)
            axs1[2,1].plot(X_dstat_axis, Y_IO_WAIT_LIST_CACHED, style, alpha=overlapping, label = instance)

            axs2[0,0].bar(X_metrics_axis - 0.2 + diff, Y_METRICS_DISK, 0.2, label = instance)
            axs2[0,1].plot(X_dstat_axis, Y_CPU_UTIL_DISK, style, alpha=overlapping, label = instance)
            axs2[1,0].plot(X_nvidia_axis, Y_GPU_UTIL_DISK, style, alpha=overlapping, label = instance)
            axs2[1,1].plot(X_nvidia_axis, Y_GPU_MEM_UTIL_DISK, style, alpha=overlapping, label = instance)
            axs2[2,0].bar(X_metrics_io_axis -0.2 + diff, Y_METRICS_IO_DISK, 0.2, label = instance)
            axs2[2,1].plot(X_dstat_axis, Y_IO_WAIT_LIST_DISK, style, alpha=overlapping, label = instance)

            #axs3[0].plot(X_itrs_axis, Y_DATA_TIME_LIST, style, alpha=overlapping, label = instance)
            #axs3[1].plot(X_itrs_axis, Y_COMPUTE_TIME_FWD_LIST, style, alpha=overlapping, label = instance)
            #axs3[2].plot(X_itrs_axis, Y_COMPUTE_TIME_BWD_LIST, style, alpha=overlapping, label = instance)

            xtra_space = 0            

            axs3.bar(X_itrs_axis - 0.2 + diff + xtra_space, Y_DATA_TIME_LIST, 0.2, color = color[0]) 
            axs3.bar(X_itrs_axis - 0.2 + diff + xtra_space, Y_COMPUTE_TIME_FWD_LIST, 0.2, bottom = Y_DATA_TIME_LIST, color = color[1])
            axs3.bar(X_itrs_axis - 0.2 + diff + xtra_space, Y_COMPUTE_TIME_BWD_LIST, 0.2, bottom = Y_COMPUTE_TIME_FWD_LIST, color = color[2])

            diff += 0.2
            xtra_space += 0.05

        axs1[0,0].set_xticks(X_metrics_axis)
        axs1[0,0].set_xticklabels(X)
        axs1[0,0].set_xlabel("Metrics")
        axs1[0,0].set_ylabel("Values")
        axs1[0,0].set_title("Metric comparison cached")
        axs1[0,0].legend()

        axs1[0,1].set_xlabel("Time")
        axs1[0,1].set_ylabel("Percentage")
        axs1[0,1].set_title("CPU utilization comparison cached")
        axs1[0,1].legend()

        axs1[1,0].set_xlabel("Time")
        axs1[1,0].set_ylabel("Percentage")
        axs1[1,0].set_title("GPU utilization comparison cached")
        axs1[1,0].legend()

        axs1[1,1].set_xlabel("Time")
        axs1[1,1].set_ylabel("Percentage")
        axs2[1,1].set_title("GPU memory utilization comparison cached")
        axs1[1,1].legend()

        axs1[2,0].set_xticks(X_metrics_io_axis)
        axs1[2,0].set_xticklabels(X_IO)
        axs1[2,0].set_xlabel("Metrics")
        axs1[2,0].set_ylabel("Values")
        axs1[2,0].set_title("IO Metric comparison cached")
        axs1[2,0].legend()

        axs1[2,1].set_xlabel("Time")
        axs1[2,1].set_ylabel("Percentage")
        axs1[2,1].set_title("IO wait percentage cached")
        axs1[2,1].legend()

        fig1.suptitle("Cached comparison - " + model , fontsize=20, fontweight ="bold")
        fig1.savefig("figures/cached_comparison - " + model)

        axs2[0,0].set_xticks(X_metrics_axis)
        axs2[0,0].set_xticklabels(X)
        axs2[0,0].set_xlabel("Metrics")
        axs2[0,0].set_ylabel("Values")
        axs2[0,0].set_title("Metric comparison cached")
        axs2[0,0].legend()

        axs2[0,1].set_xlabel("Time")
        axs2[0,1].set_ylabel("Percentage")
        axs2[0,1].set_title("CPU utilization comparison cached")
        axs2[0,1].legend()

        axs2[1,0].set_xlabel("Time")
        axs2[1,0].set_ylabel("Percentage")
        axs2[1,0].set_title("GPU utilization comparison cached")
        axs2[1,0].legend()

        axs2[1,1].set_xlabel("Time")
        axs2[1,1].set_ylabel("Percentage")
        axs2[1,1].set_title("GPU memory utilization comparison cached")
        axs2[1,1].legend()

        axs2[2,0].set_xticks(X_metrics_io_axis)
        axs2[2,0].set_xticklabels(X_IO)
        axs2[2,0].set_xlabel("Metrics")
        axs2[2,0].set_ylabel("Values")
        axs2[2,0].set_title("IO Metric comparison disk")
        axs2[2,0].legend()

        axs2[2,1].set_xlabel("Time")
        axs2[2,1].set_ylabel("Percentage")
        axs2[2,1].set_title("io wait percentage disk")
        axs2[2,1].legend()

        fig2.suptitle("Disk comparison - " + model , fontsize=20, fontweight ="bold")
        fig2.savefig("figures/disk_comparison - " + model)

        """
        axs3[0].set_xlabel("Iterations")
        axs3[0].set_ylabel("Avg Time (seconds)")
        axs3[0].set_title("Data load time comparison")
        axs3[0].legend()

        axs3[1].set_xlabel("Iterations")
        axs3[1].set_ylabel("Fwd Propogation Time (seconds)")
        axs3[1].set_title("Fwd Propgation time comparison")
        axs3[1].legend()

        axs3[2].set_xlabel("Iterations")
        axs3[2].set_ylabel("Bwd Propogation Time (seconds)")
        axs3[2].set_title("Bwd Propgation time comparison")
        axs3[2].legend()
        """

        axs3.set_xlabel("Iterations")
        axs3.set_ylabel("Avg Time (seconds)")
        axs3.set_title("Data load time comparison")
        axs3.legend()


        fig3.suptitle("Iteration time compare - " + model , fontsize=20, fontweight ="bold")
        fig3.savefig("figures/itr_time_comparison - " + model)

        plt.show()


def main():

    if len(sys.argv) <= 1:
        return

    result_dir = sys.argv[1]

    itr = 0
    for instance in sys.argv[2:]:
        instances.append(instance)
        result_path1 = result_dir + "/" + instance + "/" + "dali-gpu"
        result_path2 = result_dir + "/" + instance + "/" + "dali-cpu"

        for result_path in [result_path1, result_path2]:
            try:
                model_paths = [os.path.join(result_path, o) for o in os.listdir(result_path) if os.path.isdir(os.path.join(result_path,o))]
            except:
                continue

            for model_path in model_paths:
                model = model_path.split('/')[-1]
                batch_paths = [os.path.join(model_path, o) for o in os.listdir(model_path) if os.path.isdir(os.path.join(model_path,o))]
                for batch_path in batch_paths:
                    gpu_paths = [os.path.join(batch_path, o) for o in os.listdir(batch_path) if os.path.isdir(os.path.join(batch_path,o))]
                    for gpu_path in gpu_paths:
                        #gpu = gpu_path.split('/')[-1] + str(itr)
                        gpu = gpu_path.split('/')[-1] 
                        cpu_paths = [os.path.join(gpu_path, o) for o in os.listdir(gpu_path) if os.path.isdir(os.path.join(gpu_path,o))]
                        for cpu_path in cpu_paths:
                            json_path = cpu_path + "/MODEL.json"
                            json_path2 = cpu_path + "/MODEL2.json"
                            if not os.path.isfile(json_path2):
                                continue

                            #process_json(model, gpu, json_path2)
                            #process_json(model, gpu, json_path)
                            process_json2(model, instance, json_path2)

                            csv_path = cpu_path + "/rank-0/run3-preprocess/"
                            process_csv(model, instance, csv_path)
        itr += 1

    compare_instances()
    compare_models()


if __name__ == "__main__":
    main()


