#!/usr/bin/env python3
import json
import sys
import re


def convert_single_to_double_quotes(json_str):
    """Convert single quotes to double quotes in a JSON string."""
    # Replace single quotes with double quotes, except when inside strings
    json_str = re.sub(r"(?<!\\)'", '"', json_str)
    return json_str


def main():
    # Read input JSON from stdin
    input_data_str = sys.stdin.read()

    # Convert single quotes to double quotes
    input_data_str = convert_single_to_double_quotes(input_data_str)

    # Load JSON data
    input_data = json.loads(input_data_str)
    cluster_host_ranges = input_data["cluster_host_ranges"]
    worker_map = input_data["worker_map"]

    # Create a mapping from nodes to clusters
    node_to_cluster = {}
    for cluster_id, nodes in worker_map.items():
        for node in nodes:
            node_to_cluster[node] = cluster_host_ranges.get(cluster_id, "undefined")

    # Print the resulting mapping
    print(json.dumps(node_to_cluster, indent=2))


if __name__ == "__main__":
    main()
