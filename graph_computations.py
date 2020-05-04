
from igraph import Graph
from ansi_codes import *

# * route through terminal module
def do_show_statistics(graph):
    print(GREEN + ' average path length = ' + BOLD_GREEN + str(0.1*round(10*graph.average_path_length())))
    print(GREEN + '            diameter = ' + BOLD_GREEN + str(graph.diameter()))
