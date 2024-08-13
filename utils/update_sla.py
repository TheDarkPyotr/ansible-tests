import sys
import json
import ast
from icmplib import ping
import requests


def validate_topology(data):
    return isinstance(data, dict)
    # todo: extend validation based on /topologies/ schema


def authenticate(
    hostname: str,
    username: str = "Admin",
    password: str = "Admin",
    organization: str = "",
):

    # Define the login endpoint URL
    login_url = f"http://{hostname}:10000/api/auth/login"

    # Create the payload with the required credentials
    payload = {"username": username, "password": password, "organization": organization}

    try:
        # Send a POST request to the login endpoint
        response = requests.post(login_url, json=payload)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            response_data = response.json()

            # Attempt to extract the token
            token = response_data.get("token") or response_data.get("token")

            if token:
                return token
            else:
                print("Authentication successful, but no token found in the response.")
                return None
        else:
            # Handle unsuccessful authentication
            print(f"Failed to authenticate: {response.status_code} - {response.text}")
            return None

    except requests.RequestException as e:
        # Handle connection errors or other exceptions
        print(f"An error occurred: {e}")
        return None


def is_reacheable(hostname: str):
    host = ping(hostname, count=1, interval=0.2)
    return host.packets_sent == host.packets_received


def update_topology(clusters, workers):

    # For each cluster, assign a worker node
    for cluster in clusters:
        cluster_number = cluster.get("cluster_number", "Unknown")
        number_of_nodes = cluster.get("number_of_nodes", 0)

        cluster_reserved = []
        used_workers = []
        for i in range(number_of_nodes):
            cluster_reserved.append(workers.pop(0))

        # print(f"Cluster {cluster_number} has {number_of_nodes} nodes")
        # Update the cluster with the assigned worker node
        apps = cluster["sla_descriptor"]["applications"]
        for app in apps:
            microservices = app["microservices"]

            service_index = 0
            for service in microservices:
                if len(cluster_reserved) > 0:
                    assigned_hostname = cluster_reserved.pop(0)
                    used_workers.append(assigned_hostname)
                else:
                    assigned_hostname = used_workers[service_index]
                    service_index += 1

                service["constraints"] = [
                    {
                        "type": "direct",
                        "node": assigned_hostname,
                        "cluster": "gpu22",
                    }
                ]

    # Print the updated topology
    # print("Updated topology:")
    # print(json.dumps(clusters, indent=4))


def check_correspondece(json_data, workers):
    # Extract the topology descriptor
    topology = json_data.get("topology_descriptor", {})

    # Extract the list of clusters
    clusters = topology.get("cluster_list", [])

    # Count the number of clusters
    num_clusters = len(clusters)
    # print(f"Number of clusters: {num_clusters}")

    # For each cluster, count the number of nodes
    total_nodes = 0
    for cluster in clusters:
        cluster_number = cluster.get("cluster_number", "Unknown")
        number_of_nodes = cluster.get("number_of_nodes", 0)
        total_nodes += number_of_nodes
        # print(f"Cluster {cluster_number} has {number_of_nodes} nodes")

    # print(f"Total number of nodes: {total_nodes}")
    # print(f"Number of workers: {len(workers)}")
    if len(workers) < total_nodes:
        # print("Insufficient worker nodes.")
        return False
    else:
        # try:
        update_topology(clusters, workers)
        return json_data
        # except Exception as e:
        print(f"Error updating topology: {e}")
        return None

    # print("Updated topology:")
    # print(json.dumps(topology, indent=4))


def main():
    if len(sys.argv) != 5:
        print("Error: Expected exactly two command-line arguments.")
        return

    json_file = sys.argv[1]
    worker_str = sys.argv[2]
    inventory_str = sys.argv[3]
    root_str = sys.argv[4]

    # print(f"JSON file: {json_file}")

    # print(f"Workers array: {worker_str}")
    # Read and parse the JSON file
    try:
        with open(json_file, "r") as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return

    # Parse the second argument as a JSON array
    try:
        worker_list = ast.literal_eval(worker_str)
        if not isinstance(worker_list, list):
            print("Error: worker parameter is not a list")
    except (SyntaxError, ValueError) as e:
        print(f"Error: converting string to list: {e}")

    try:
        cluster_inventory = ast.literal_eval(inventory_str)
        if not isinstance(cluster_inventory, list):
            print("Error: cluster parameter is not a list ", cluster_inventory)
    except (SyntaxError, ValueError) as e:
        print(f"Error converting string to list: {e}")

    try:
        root_group = ast.literal_eval(root_str)
        if not isinstance(root_group, list):
            print("Error: root parameter is not a list ", root_group)
    except (SyntaxError, ValueError) as e:
        print(f"Error converting string to list: {e}")

    # Ping root node

    # Validate the JSON data
    validity = validate_topology(json_data)

    updated_sla = {}
    if validity:
        updated_sla = check_correspondece(json_data, worker_list)

    # Output result
    if updated_sla is not None and validate_topology(updated_sla):
        # print(updated_sla)

        for hostname in root_group:
            if not is_reacheable(hostname):
                print(f"Error: Root node {hostname} is not reachable.")
            else:
                token = authenticate(hostname)
                print(f"Token: {token}")
                # requests.get(f"http://{hostname}:10000/api/auth/login")

        # Create the updated JSON file
        # updated_file = json_file.replace(".json", "_updated.json")
        # with open(updated_file, "w", encoding="utf-8") as f:
        # json.dump(updated_sla, f, ensure_ascii=False, indent=4)

    else:
        print("false")


if __name__ == "__main__":
    main()

# test purposes
# python3 ./utils/update_sla.py ./topologies/full.json "[\"cmvm21\", \"cmvm22\", \"cmvm23\", \"cmvm24\"]" "[\"worker1\", \"worker2\", \"worker3\", \"worker4\"]" "[\"131.159.25.107\"]"
