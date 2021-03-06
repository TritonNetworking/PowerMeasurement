"""
Utility script to get data block placement of a hdfs file and plot it
"""

import os
import random
import paramiko
from datetime import datetime
import time
import re
from collections import Counter
import matplotlib.pyplot as plt
import run_experiments
import socket


# Command to run
file_path = "/user/ayelam/sort_inputs/100000mb.input"
hdfs_fsck_command = "hdfs fsck {0} -files -blocks -locations".format(file_path)
# master_node_name = "ccied21.sysnet.ucsd.edu"
master_node_name = "b09-40.sysnet.ucsd.edu"
start_line_pattern = "/user/ayelam/sort_inputs/50000mb.input 1000000000 bytes, 8 block(s):  OK"
data_line_pattern = "^([0-9]+).+DatanodeInfoWithStorage[[]([0-9]+[.][0-9]+[.][0-9]+[.][0-9]+)[:]50010.+$"
power_plots_output_dir = 'D:\Power Measurements\\v2\PowerPlots\\' + datetime.now().strftime("%m-%d")


# Creates SSH client using paramiko lib.
def create_ssh_client(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


# A simplified way to get IP Addr to Node name mapping
def get_ip_to_name_mapping(user_name, password):
    ip_to_node_dict = {}
    for node_name in run_experiments.spark_nodes:
        node_full_name = "{0}.{1}".format(node_name, run_experiments.spark_nodes_dns_suffx)
        # print(socket.gethostbyname(node_full_name))
        ip_to_node_dict[socket.gethostbyname(node_full_name)] = node_name
    return ip_to_node_dict


def main():
    user_password_info = open("root-user.pass").readline()   # One line in <user>;<password> format.
    user_name = user_password_info.split(";")[0]
    password = user_password_info.split(";")[1]

    # ip_to_node_dict = get_ip_to_name_mapping(user_name, password)

    ssh_client = create_ssh_client(master_node_name, 22, user_name, password)
    _, stdout, _ = ssh_client.exec_command(hdfs_fsck_command)
    output = stdout.readlines()

    parse_for_data = False
    blocks_counter = Counter()
    for line in output:
        if line.startswith(file_path):
            parse_for_data = True
            continue

        if parse_for_data:
            matches = re.match(data_line_pattern, line)
            if matches:
                block_id = matches.group(1)
                node_ip = matches.group(2)
                # print(node_ip)
                # node_name = ip_to_node_dict[node_ip]
                node_name = [node_name for node_name, addr in run_experiments.fat_tree_ip_mac_map.items() if addr[1] == node_ip][0] 
                blocks_counter[node_name] += 1
            else:
                parse_for_data = False

    if not blocks_counter:
        print("Something wrong!")
        exit()

    if not os.path.exists(power_plots_output_dir):
        os.mkdir(power_plots_output_dir)

    fig, ax = plt.subplots(1,1)
    fig.suptitle("Data block placement for file: " + file_path)
    values = blocks_counter.values()
    proportions = [value/sum(values) for value in values]
    ax.bar(blocks_counter.keys(), proportions)
    ax.set_ylabel("% of blocks")
    ax.set_xlabel("Nodes")

    # plt.show()
    output_plot_file_name = "file_placement_{0}.png".format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f"))
    output_full_path = os.path.join(power_plots_output_dir, output_plot_file_name)
    plt.savefig(output_full_path)


if __name__ == '__main__':
    main()

