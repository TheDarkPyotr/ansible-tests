import sys
import json
import re


def convert_single_to_double_quotes(json_str):
    """Convert single quotes to double quotes in a JSON string."""
    # Replace single quotes with double quotes, except when inside strings
    json_str = re.sub(r"(?<!\\)'", '"', json_str)
    return json_str


def compute_worker_cluster_association(data):
    """Compute the association between workers and clusters."""
    clusters = data.get("topology_descriptor", {}).get("cluster_list", [])
    workers = data.get("group_workers_full", [])

    cluster_worker_map = {}
    worker_index = 0

    for cluster in clusters:
        cluster_number = cluster.get("cluster_number")
        number_of_nodes = cluster.get("number_of_nodes", 0)

        if number_of_nodes > 0:
            cluster_worker_map[cluster_number] = []
            for _ in range(number_of_nodes):
                if worker_index < len(workers):
                    cluster_worker_map[cluster_number].append(workers[worker_index])
                    worker_index += 1

    return cluster_worker_map


def process_json_string(json_str):
    """Process JSON string to compute worker-cluster association."""
    # Convert single quotes to double quotes
    json_str = convert_single_to_double_quotes(json_str)

    # Load JSON data
    try:
        input_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return f"JSON decode error: {e}"

    # Compute the association between workers and clusters
    association = compute_worker_cluster_association(input_data)

    # Return the result as a JSON string
    return json.dumps(association, indent=4)


def main():
    # Read input JSON from stdin
    input_data_str = sys.stdin.read()

    # Process the JSON string
    result = process_json_string(input_data_str)

    # Print the result
    print(result)


if __name__ == "__main__":
    main()
