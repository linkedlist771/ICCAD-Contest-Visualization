from utils import *

def main():
    dir_path = "data/ispd2005/adaptec1"
    nodes_data, pl_data = get_router_data(dir_path)
    visualize_router_data(nodes_data, pl_data, save_figure=True)

if __name__ == "__main__":
    main()