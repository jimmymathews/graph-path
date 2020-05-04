
import argparse
from igraph import Graph

def parse_options_and_input(version):
    parser = argparse.ArgumentParser(description=('graph-path  Explore paths in a graph' + ' v' + version))
    parser.add_argument('graph_file',                 type=str, nargs=1, help='format is graphml with a "name" attribute. Edge list format is also acceptable, using space-separated integer pairs. Formats automatically detected by the igraph library may also work.')
    parser.add_argument('-n', '--names',              type=str, nargs=1, help='(optional) Comma or tab separated values with 2 columns: node name as it appears (graph_file), and a preferred alias. This is useful if the node names in graph file are not the preferred names.')
    parser.add_argument('-d', '--descriptions',       type=str, nargs=1, help='(optional) Comma or tab separated values with 2 columns: node name (or alias), and longer description.')
    parser.add_argument('-v', '--vertical-layout',  action='store_true', help='(optional) If set, lists nodes vertically (this is easier for copy and paste).')
    parser.add_argument('-c', '--case-insensitive', action='store_true', help='(optional) If set, character input is case-insensitive (convenient if node names are capitalized).')
    parser.add_argument('-s', '--statistics',       action='store_true', help='(optional) Show graph statistics.')
    parser.add_argument('--version',                   action='version', help='(optional) Print version and exit.', version=version)
    args = parser.parse_args()
    graph_file = args.graph_file[0]
    graph = Graph.Read(graph_file)
    description_capable = False # not yet implemented
    return [graph, args.statistics, args.vertical_layout, description_capable, args.case_insensitive]
