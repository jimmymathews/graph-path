
from pygtrie import *  # third-party library

class GPModel():
    def __init__(self, graph, node_names):
        self.graph = graph
        self.trie = CharTrie()
        for name in node_names:
            self.trie[name] = True
        self.reset_state()

    def reset_state(self):
        self.nodes = ['']
        self.completion = None
