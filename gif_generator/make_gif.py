from array2gif import write_gif
import os


def list_of_numpy_to_gif(dataset_list, save_path):
    write_gif(dataset_list, os.path.join(os.getcwd(), save_path), fps=5)