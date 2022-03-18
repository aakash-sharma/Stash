import sys
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


stats = defaultdict(lambda: defaultdict(dict))
stats2 = defaultdict(lambda: defaultdict(dict))

gpu_map = {
        "p2.xlarge" : "gpus-10",
        "chameleon.xlarge" : "gpus-11",
        "p2.8xlarge" : "gpus-8",
        "p2.16xlarge-io1" : "gpus-16",
        "p2.16xlarge" : "gpus-16"}

instances = []

def process_json(model, gpu, json_path):

    with open(json_path) as fd:
        dagJson = json.load(fd)

    stats[model][gpu]["TRAIN_SPEED_INGESTION"] = dagJson["SPEED_INGESTION"]
    stats[model][gpu]["TRAIN_SPEED_DISK"]  = dagJson["SPEED_DISK"]
    stats[model][gpu]["TRAIN_SPEED_CACHED"] = dagJson["SPEED_CACHED"]
    stats[model][gpu]["DISK_THR"] = dagJson["DISK_THR"]
    #stats[model][gpu]["MEM_THR"] = dagJson["MEM_THR"]
    stats[model][gpu]["TRAIN_TIME_DISK"] = dagJson["RUN2"]["TRAIN"]
    stats[model][gpu]["TRAIN_TIME_CACHED"] = dagJson["RUN3"]["TRAIN"]
    stats[model][gpu]["CPU_UTIL_DISK_PCT"] = dagJson["RUN2"]["CPU"]
    stats[model][gpu]["CPU_UTIL_CACHED_PCT"] = dagJson["RUN3"]["CPU"]
    stats[model][gpu]["GPU_UTIL_DISK_PCT"] = dagJson["RUN2"]["GPU_UTIL"]
    stats[model][gpu]["GPU_UTIL_CACHED_PCT"] = dagJson["RUN3"]["GPU_UTIL"]
    stats[model][gpu]["GPU_MEM_UTIL_DISK_PCT"] = dagJson["RUN2"]["GPU_MEM_UTIL"]
    stats[model][gpu]["GPU_MEM_UTIL_CACHED_PCT"] = dagJson["RUN3"]["GPU_MEM_UTIL"]
    stats[model][gpu]["MEMCPY_TIME"] = dagJson["RUN1"]["MEMCPY"]

    stats[model][gpu]["PREP_STALL_TIME"] = dagJson["RUN3"]["TRAIN"] - dagJson["RUN1"]["TRAIN"]
    stats[model][gpu]["FETCH_STALL_TIME"] = dagJson["RUN2"]["TRAIN"] - stats[model][gpu]["PREP_STALL_TIME"]

    stats[model][gpu]["PREP_STALL_PCT"] = stats[model][gpu]["PREP_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_DISK"] * 100
    stats[model][gpu]["FETCH_STALL_PCT"] = stats[model][gpu]["FETCH_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_DISK"] * 100


def process_json2(model, gpu, json_path):

    with open(json_path) as fd:
        dagJson = json.load(fd)

    stats[model][gpu]["TRAIN_SPEED_INGESTION"] = dagJson["SPEED_INGESTION"]
    stats[model][gpu]["TRAIN_SPEED_DISK"]  = dagJson["SPEED_DISK"]
    stats[model][gpu]["TRAIN_SPEED_CACHED"] = dagJson["SPEED_CACHED"]
    stats[model][gpu]["DISK_THR"] = dagJson["DISK_THR"]
    stats[model][gpu]["TRAIN_TIME_DISK"] = dagJson["RUN2"]["TRAIN"]
    stats[model][gpu]["TRAIN_TIME_CACHED"] = dagJson["RUN3"]["TRAIN"]
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
    stats[model][gpu]["PREP_STALL_PCT"] = stats[model][gpu]["PREP_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_DISK"] * 100
    stats[model][gpu]["FETCH_STALL_PCT"] = stats[model][gpu]["FETCH_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME_DISK"] * 100



def plotModels(instance):

    fig1, axs1 = plt.subplots(2, 1)
    
    gpu = gpu_map[instance]
    X = [model for model in stats.keys()]
    X_axis = np.arange(len(X))

    Y_PREP_STALL_TIME = [stats[model][gpu]["PREP_STALL_TIME"] for model in X]
    Y_FETCH_STALL_TIME = [stats[model][gpu]["FETCH_STALL_TIME"] for model in X]
    Y_TRAIN_TIME = [stats[model][gpu]["TRAIN_TIME"] for model in X]
    Y_PREP_STALL_PCT = [stats[model][gpu]["PREP_STALL_PCT"] for model in X]
    Y_FETCH_STALL_PCT = [stats[model][gpu]["FETCH_STALL_PCT"] for model in X]

    axs1[0].bar(X_axis-0.2, Y_TRAIN_TIME, 0.2, label = 'Train time')
    axs1[0].bar(X_axis, Y_PREP_STALL_TIME, 0.2, label = 'Prep stall time')
    axs1[0].bar(X_axis+0.2, Y_FETCH_STALL_TIME, 0.2, label = 'Fetch stall time')

    axs1[1].bar(X_axis-0.2, Y_PREP_STALL_PCT, 0.2, label = 'Prep stall %')
    axs1[1].bar(X_axis, Y_FETCH_STALL_PCT, 0.2, label = 'Fetch stall %')

    axs1[0].set_xticks(X_axis)
    axs1[0].set_xticklabels(X)
    axs1[0].set_xlabel("Models")
    axs1[0].set_ylabel("Time")
    axs1[0].legend()
    

    axs1[1].set_xticks(X_axis)
    axs1[1].set_xticklabels(X)
    axs1[1].set_xlabel("Models")
    axs1[1].set_ylabel("Percentage")
    axs1[1].legend()

    fig1.suptitle("Stall analysis " + instance)
    plt.show()

def compare():

    models = list(stats.keys())

    for instance in instances:

        gpu = gpu_map[instance]

        for model in models:

            if gpu not in stats[model]:
                del stats[model]


    fig1, axs1 = plt.subplots(2, 1, figsize=(30,20))
    fig2, axs2 = plt.subplots(3, 1, figsize=(30,20))
    fig3, axs3 = plt.subplots(3, 1, figsize=(30,20))
    fig4, axs4 = plt.subplots(3, 1, figsize=(30,20))
    fig5, axs5 = plt.subplots(3, 1, figsize=(30,20))
    fig6, axs6 = plt.subplots(1, 1, figsize=(30,20))

    X = [model for model in stats.keys()]
    X_axis = np.arange(len(X))

    diff = 0

    for instance in instances:
        
        gpu = gpu_map[instance]
        print(gpu)
        
        Y_PREP_STALL_PCT = [stats[model][gpu]["PREP_STALL_PCT"] for model in X]
        Y_FETCH_STALL_PCT = [stats[model][gpu]["FETCH_STALL_PCT"] for model in X]
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
        Y_MEMCPY_TIME = [stats[model][gpu]["MEMCPY"] for model in X]

        axs1[0].bar(X_axis-0.2 + diff , Y_PREP_STALL_PCT, 0.2, label = instance)
        axs1[1].bar(X_axis-0.2 + diff, Y_FETCH_STALL_PCT, 0.2, label = instance)

        axs2[0].bar(X_axis-0.2 + diff , Y_TRAIN_TIME_DISK, 0.2, label = instance)
        axs2[1].bar(X_axis-0.2 + diff, Y_TRAIN_TIME_CACHED, 0.2, label = instance)
        axs2[2].bar(X_axis-0.2 + diff, Y_DISK_THR, 0.2, label = instance)

        axs3[0].bar(X_axis-0.2 + diff, Y_TRAIN_SPEED_INGESTION, 0.2, label = instance)
        axs3[1].bar(X_axis-0.2 + diff , Y_TRAIN_SPEED_DISK, 0.2, label = instance)
        axs3[2].bar(X_axis-0.2 + diff, Y_TRAIN_SPEED_CACHED, 0.2, label = instance)

        axs4[0].bar(X_axis-0.2 + diff , Y_CPU_UTIL_DISK_PCT, 0.2, label = instance)
        axs4[1].bar(X_axis-0.2 + diff , Y_GPU_UTIL_DISK_PCT, 0.2, label = instance)
        axs4[2].bar(X_axis-0.2 + diff , Y_GPU_MEM_UTIL_DISK_PCT, 0.2, label = instance)

        axs5[0].bar(X_axis-0.2 + diff , Y_CPU_UTIL_CACHED_PCT, 0.2, label = instance)
        axs5[1].bar(X_axis-0.2 + diff , Y_GPU_UTIL_CACHED_PCT, 0.2, label = instance)
        axs5[2].bar(X_axis-0.2 + diff , Y_GPU_MEM_UTIL_CACHED_PCT, 0.2, label = instance)

        axs6[0].bar(X_axis-0.2 + diff , Y_MEMCPY_TIME, 0.2, label = instance)

        print(Y_GPU_UTIL_CACHED_PCT)

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

    fig1.suptitle("Stall comparison" , fontsize=20, fontweight ="bold")
    fig1.savefig("figures/stall_comparison")
    
    axs2[0].set_xticks(X_axis)
    axs2[0].set_xticklabels(X)
    #axs2[0].set_xlabel("Models")
    axs2[0].set_ylabel("Time")
    axs2[0].set_title("Training time disk comparison")
    axs2[0].legend()

    axs2[1].set_xticks(X_axis)
    axs2[1].set_xticklabels(X)
    #axs2[1].set_xlabel("Models")
    axs2[1].set_ylabel("Time")
    axs2[1].set_title("Training time cached comparison")
    axs2[1].legend()

    axs2[2].set_xticks(X_axis)
    axs2[2].set_xticklabels(X)
    #axs2[1].set_xlabel("Models")
    axs2[2].set_ylabel("Throughput")
    axs2[2].set_title("Disk throughput comparison")
    axs2[2].legend()

    fig2.suptitle("Training time comparison" , fontsize=20, fontweight ="bold")
    fig2.savefig("figures/training_time")

    axs3[0].set_xticks(X_axis)
    axs3[0].set_xticklabels(X)
    #axs3[0].set_xlabel("Models")
    axs3[0].set_ylabel("Samples/sec")
    axs3[0].set_title("Training speed ingestion comparison")
    axs3[0].legend()

    axs3[1].set_xticks(X_axis)
    axs3[1].set_xticklabels(X)
    #axs3[1].set_xlabel("Models")
    axs3[1].set_ylabel("Samples/sec")
    axs3[1].set_title("Training speed disk comparison")
    axs3[1].legend()

    axs3[2].set_xticks(X_axis)
    axs3[2].set_xticklabels(X)
    #axs3[2].set_xlabel("Models")
    axs3[2].set_ylabel("Samples/sec")
    axs3[2].set_title("Training speed cached comparison")
    axs3[2].legend()

    fig3.suptitle("Training speed comparison", fontsize=20, fontweight ="bold")
    fig3.savefig("figures/training_speed")

    axs4[0].set_xticks(X_axis)
    axs4[0].set_xticklabels(X)
    #axs4[0].set_xlabel("Models")
    axs4[0].set_ylabel("Average CPU utilization")
    axs4[0].set_title("CPU utilization comparison")
    axs4[0].legend()

    axs4[1].set_xticks(X_axis)
    axs4[1].set_xticklabels(X)
    #axs4[1].set_xlabel("Models")
    axs4[1].set_ylabel("Average GPU utilization")
    axs4[1].set_title("GPU utilization comparison")
    axs4[1].legend()

    axs4[2].set_xticks(X_axis)
    axs4[2].set_xticklabels(X)
    #axs4[2].set_xlabel("Models")
    axs4[2].set_ylabel("Average GPU memory utilization")
    axs4[2].set_title("GPU memory utilization comparison")
    axs4[2].legend()

    fig4.suptitle("CPU and GPU utilization DISK comparison", fontsize=20, fontweight ="bold")
    fig4.savefig("figures/cpu_gpu_util_disk")

    axs5[0].set_xticks(X_axis)
    axs5[0].set_xticklabels(X)
    #axs5[0].set_xlabel("Models")
    axs5[0].set_ylabel("Average CPU utilization")
    axs5[0].set_title("CPU utilization comparison")
    axs5[0].legend()

    axs5[1].set_xticks(X_axis)
    axs5[1].set_xticklabels(X)
    #axs5[1].set_xlabel("Models")
    axs5[1].set_ylabel("Average GPU utilization")
    axs5[1].set_title("GPU utilization comparison")
    axs5[1].legend()

    axs5[2].set_xticks(X_axis)
    axs5[2].set_xticklabels(X)
    #axs5[2].set_xlabel("Models")
    axs5[2].set_ylabel("Average GPU memory utilization")
    axs5[2].set_title("GPU memory utilization comparison")
    axs5[2].legend()

    fig5.suptitle("CPU and GPU utilization CACHED comparison", fontsize=20, fontweight ="bold")
    fig5.savefig("figures/cpu_gpu_util_cached")

    axs6[0].set_xticks(X_axis)
    axs6[0].set_xticklabels(X)
    axs6[0].set_ylabel("memcpy time")
    axs6[0].set_title("memcpy")
    axs6[0].legend()
    plt.show()

def compare_models():

    models = list(stats.keys())
    max_dstat_len = 0
    max_nvidia_len = 0

    X = ["Disk Throughput", "Train speed", "Memory", "Page cache"]
    X_IO = ["Read Write", "IOWait"]

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

        fig1, axs1 = plt.subplots(3, 2, figsize=(30,20))
        fig2, axs2 = plt.subplots(3, 2, figsize=(30,20))

        X_dstat_axis = np.arange(max_dstat_len)
        X_nvidia_axis = np.arange(max_nvidia_len)
        X_metrics_axis = np.arange(len(X))
        X_metrics_io_axis = np.arange(len(X_IO))
        diff = 0

        for instance in instances:
            
            gpu = gpu_map[instance]
            style = None

            if instance == "p2.xlarge":
                style = 'r--'
            elif instance == "chameleon.xlarge":
                style = 'b--'

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
            print(Y_METRICS_IO_DISK)

            diff += 0.2

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
        axs2[1,1].set_title("GPU memeory utilization comparison cached")
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
                model_path_ = model_path + "/jobs-1"
                gpu_paths = [os.path.join(model_path_, o) for o in os.listdir(model_path_) if os.path.isdir(os.path.join(model_path_,o))]
                for gpu_path in gpu_paths:
                    gpu = gpu_path.split('/')[-1] + str(itr)
                    print(gpu)
                    cpu_paths = [os.path.join(gpu_path, o) for o in os.listdir(gpu_path) if os.path.isdir(os.path.join(gpu_path,o))]
                    for cpu_path in cpu_paths:
                        json_path = cpu_path + "/MODEL.json"
                        json_path2 = cpu_path + "/MODEL2.json"
                        if not os.path.isfile(json_path):
                            continue

                        process_json(model, gpu, json_path)
                        process_json2(model, gpu, json_path2)
        itr += 1

    compare()
    compare_models()


if __name__ == "__main__":
    main()


