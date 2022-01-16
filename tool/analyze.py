import sys
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


stats = defaultdict(lambda: defaultdict(dict))
stats2 = defaultdict(lambda: defaultdict(dict))

gpu_map = {
        "p2.2xlarge" : "gpus-1",
        "p2.8xlarge" : "gpus-8"}

instances = []

def process_json(model, gpu, json_path):

    with open(json_path) as fd:
        dagJson = json.load(fd)

    stats[model][gpu]["SPEED_INGESTION"] = dagJson["SPEED_INGESTION"]
    stats[model][gpu]["SPEED_DISK"]  = dagJson["SPEED_DISK"]
    stats[model][gpu]["SPEED_CACHED"] = dagJson["SPEED_CACHED"]
    stats[model][gpu]["DISK_THR"] = dagJson["DISK_THR"]
    stats[model][gpu]["MEM_THR"] = dagJson["MEM_THR"]
    stats[model][gpu]["TRAIN_TIME"] = dagJson["RUN2"]["TRAIN"]
    stats[model][gpu]["PREP_STALL_TIME"] = dagJson["RUN3"]["TRAIN"] - dagJson["RUN1"]["TRAIN"]
    stats[model][gpu]["FETCH_STALL_TIME"] = dagJson["RUN2"]["TRAIN"] - stats[model][gpu]["PREP_STALL_TIME"]
    stats[model][gpu]["PREP_STALL_PCT"] = stats[model][gpu]["PREP_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME"] * 100
    stats[model][gpu]["FETCH_STALL_PCT"] = stats[model][gpu]["FETCH_STALL_TIME"] / stats[model][gpu]["TRAIN_TIME"] * 100
    
    stats2[gpu][model]["SPEED_INGESTION"] = dagJson["SPEED_INGESTION"]
    stats2[gpu][model]["SPEED_DISK"]  = dagJson["SPEED_DISK"]
    stats2[gpu][model]["SPEED_CACHED"] = dagJson["SPEED_CACHED"]
    stats2[gpu][model]["DISK_THR"] = dagJson["DISK_THR"]
    stats2[gpu][model]["MEM_THR"] = dagJson["MEM_THR"]
    stats2[gpu][model]["TRAIN_TIME"] = dagJson["RUN2"]["TRAIN"]
    stats2[gpu][model]["PREP_STALL_TIME"] = dagJson["RUN3"]["TRAIN"] - dagJson["RUN1"]["TRAIN"]
    stats2[gpu][model]["FETCH_STALL_TIME"] = dagJson["RUN2"]["TRAIN"] - stats[model][gpu]["PREP_STALL_TIME"]


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


    fig1, axs1 = plt.subplots(2, 1)

    X = [model for model in stats.keys()]
    X_axis = np.arange(len(X))

    diff = 0

    for instance in instances:
        
        gpu = gpu_map[instance]
        
        Y_PREP_STALL_PCT = [stats[model][gpu]["PREP_STALL_PCT"] for model in X]
        Y_FETCH_STALL_PCT = [stats[model][gpu]["FETCH_STALL_PCT"] for model in X]

        axs1[0].bar(X_axis-0.2 + diff , Y_PREP_STALL_PCT, 0.2, label = instance)
        axs1[1].bar(X_axis-0.2 + diff, Y_FETCH_STALL_PCT, 0.2, label = instance)

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

    fig1.suptitle("Stall comparison" )
    plt.show()


def main():

    if len(sys.argv) <= 1:
        return

    for instance in sys.argv[1:]:
        instances.append(instance)
        result_path = "results-" + instance + "/" + "dali-gpu"

        model_paths = [os.path.join(result_path, o) for o in os.listdir(result_path) if os.path.isdir(os.path.join(result_path,o))]

        for model_path in model_paths:
            model = model_path.split('/')[-1]
            model_path_ = model_path + "/jobs-1"
            gpu_paths = [os.path.join(model_path_, o) for o in os.listdir(model_path_) if os.path.isdir(os.path.join(model_path_,o))]
            for gpu_path in gpu_paths:
                gpu = gpu_path.split('/')[-1]
                cpu_paths = [os.path.join(gpu_path, o) for o in os.listdir(gpu_path) if os.path.isdir(os.path.join(gpu_path,o))]
                for cpu_path in cpu_paths:
                    json_path = cpu_path + "/MODEL.json"
                    if not os.path.isfile(json_path):
                        continue

                    process_json(model, gpu, json_path)

        #plotModels(instance)

    compare()


if __name__ == "__main__":
    main()


