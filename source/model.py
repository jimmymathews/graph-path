
from pygtrie import *  # third-party library

class GPModel():
    def __init__(self, graph, node_names):
        self.graph = graph
        self.recreate_index(node_names)
        self.clear_all_manipulable_state()

    def clear_all_manipulable_state(self):
        self.nodes = ['']
        self.clear_field_entry_handling_state()

    def clear_field_entry_handling_state(self):
        self.clear_partial_name_completion_state()
        self.clear_neighbor_completion_state()

    def clear_partial_name_completion_state(self):
        self.completion_candidates = []
        self.completion_candidate_index = 0
        self.cached_node_name_entry_prefix = None

    def clear_neighbor_completion_state(self):
        self.neighbor = None

    def field(self):
        return self.nodes[-1]

    def set_field(self, n):
        self.nodes[-1] = n

    def clear_field(self):
        self.nodes[-1] = ""

    def recreate_index(self, node_names):
        self.trie = CharTrie()
        for name in node_names:
            self.trie[name] = True
