
from pygtrie import *  # third-party library

class GPModel():
    def __init__(self, graph, node_names):
        self.graph = graph
        self.recreate_index(node_names)
        self.reset_manipulable_state()

    def reset_manipulable_state(self):
        self.nodes = ['']
        self.partial_name_completion = None

    def recreate_index(self, node_names):
        self.trie = CharTrie()
        for name in node_names:
            self.trie[name] = True
