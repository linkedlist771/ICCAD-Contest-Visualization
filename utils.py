import os
import argparse
from tqdm import tqdm

def parse_nodes_file(nodes_file):
    data = {
        'version': None,
        'num_nodes': None,
        'num_terminals': None,
        'nodes': []
    }
    node_initial_line = 6
    with open(nodes_file, 'r') as f:
        lines = f.readlines()
        
        # Extract version/comment line
        data['version'] = lines[0].strip()
        
        # Extract NumNodes and NumTerminals
        for line in lines[:10]:
            if line.startswith("NumNodes"):
                data['num_nodes'] = int(line.split(":")[1].strip())
            elif line.startswith("NumTerminals"):
                data['num_terminals'] = int(line.split(":")[1].strip())
        # Extract terminal details
        # use tqdm to show progress bar
        for line in tqdm(lines[node_initial_line:node_initial_line+data['num_nodes']]):
            parts = line.strip().split()
            terminal_data = {
                'name': parts[0],
                'w': int(parts[1]),
                'h': int(parts[2])
            }
            data['nodes'].append(terminal_data)
    assert data['num_nodes'] == len(data['nodes']), f"Number of terminals does not match:\
    {data['num_nodes']} != {len(data['nodes'])}"
    return data
   


def parse_pl_file(pl_file):
    data = {
        'version': None,
        'node_pos': []
    }
    placement_initial_line = 4

    with open(pl_file, 'r') as f:
        lines = f.readlines()
        
        # Extract version/comment line
        data['version'] = lines[0].strip()
        
        # Extract terminal details, use tqdm to show progress bar
        for line in tqdm(lines[placement_initial_line:]):  # Assuming the actual data starts from the 4th line
            parts = line.strip().split()
            terminal_data = {
                'name': parts[0],
                'x': int(parts[1]),
                'y': int(parts[2]),
                'pos_type': parts[4] if len(parts) > 4 else None  # Extracting the terminal type
            }
            
            data['node_pos'].append(terminal_data)
    return data

def get_router_data(router_dir):
    # dir_path = "data/ispd2005/adaptec1"
    dir_path = router_dir
    assert os.path.isdir(dir_path), "The path should be a directory"
    # find the file in the directory ending with .pl
    placement_file = [f for f in os.listdir(dir_path) if f.endswith(".pl")]
    assert len(placement_file) == 1, "There should be only one .pl file in the directory"
    placement_file = placement_file[0]
    placement_file = os.path.join(dir_path, placement_file)
    # similary, find the file in the directory ending with .nodes
    nodes_file = [f for f in os.listdir(dir_path) if f.endswith(".nodes")]
    assert len(nodes_file) == 1, "There should be only one .nodes file in the directory"
    nodes_file = nodes_file[0]
    nodes_file = os.path.join(dir_path, nodes_file)
    nodes_data = parse_nodes_file(nodes_file)
    pl_data = parse_pl_file(placement_file)
    return nodes_data, pl_data
    # print(pl_data)

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from multiprocessing import Pool, cpu_count


# Define a function to be run by each process
def draw_rectangles(args):
    node_pos_chunk, nodes_dict = args
    rectangles = []

    for node_pos in node_pos_chunk:
        node = nodes_dict.get(node_pos['name'])
        if node:
            rect = patches.Rectangle(
                (node_pos['x'], node_pos['y']), 
                node['w'], 
                node['h'], 
                linewidth=1, 
                edgecolor='r', 
                facecolor='none'
            )
            rectangles.append(rect)

    return rectangles

def visualize_router_data(nodes_data, pl_data):
    # Convert nodes_data into a dictionary for quick lookup
    nodes_dict = {node['name']: node for node in nodes_data['nodes']}

    # Split the node_pos list into chunks for multiprocessing
    num_processes = cpu_count()  # Get the number of available CPUs
    chunk_size = len(pl_data['node_pos']) // num_processes
    chunks = [(pl_data['node_pos'][i:i+chunk_size], nodes_dict) for i in range(0, len(pl_data['node_pos']), chunk_size)]
    
    # Use a Pool of processes to compute the rectangles
    with Pool(num_processes) as pool:
        # Using tqdm to show the progress bar
        results = list(tqdm(pool.imap(draw_rectangles, chunks), total=len(chunks), desc="Drawing rectangles"))
    
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Add the computed rectangles to the plot
    for rect_chunk in results:
        for rect in rect_chunk:
            ax.add_patch(rect)
    
    ax.set_title('Router Data Visualization')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    
    # Adjust the aspect ratio to equal and set the plot limits
    ax.set_aspect('equal', 'box')
    ax.autoscale_view()
    
    plt.show()



def main():
    dir_path = "data/ispd2005/adaptec1"
    nodes_data, pl_data = get_router_data(dir_path)
    visualize_router_data(nodes_data, pl_data)
    
    
if __name__ == "__main__":
    main()