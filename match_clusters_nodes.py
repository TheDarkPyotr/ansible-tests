#!/usr/bin/env python3
import json
import sys


def main():
    input_data = json.load(sys.stdin)
    cluster_host_ranges = input_data["cluster_host_ranges"]
    worker_map = input_data["worker_map"]

    node_to_cluster = {}
    for cluster_id, nodes in worker_map.items():
        for node in nodes:
            node_to_cluster[node] = cluster_id

    result = {}
    for node, cluster_id in node_to_cluster.items():
        cluster_hostname = cluster_host_ranges.get(cluster_id, "undefined")
        result[node] = cluster_hostname

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
