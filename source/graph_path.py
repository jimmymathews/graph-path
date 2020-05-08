
version = '0.2'
# Uses 'pygtrie' library, https://github.com/google/pygtrie (released under Apache License 2.0). May 3 2020

# Python standard library
from enum import Enum

# project-level
from options_utilities import *
from graph_computations import *
from simple_utilities import *
from controller import GPController

class GUI:
    def __init__(self, graph, using_vertical_layout, description_capable, descriptions_file, case_insensitive, showing_plot, being_quiet, neighborhood_size):
        self.controller = GPController(graph, using_vertical_layout, description_capable, descriptions_file, case_insensitive, showing_plot, being_quiet, neighborhood_size)

    def start(self):
        self.controller.handle_io()

def main():
    [graph, show_statistics, using_vertical_layout, description_capable, descriptions_file, lettercase_insensitive, showing_plot, being_quiet, neighborhood_size] = parse_options_and_input(version)

    if show_statistics:
        do_show_statistics(graph)

    gui = GUI(graph, using_vertical_layout, description_capable, descriptions_file, lettercase_insensitive, showing_plot, being_quiet, neighborhood_size)
    gui.start()
