
from pygtrie import *  # third-party library
from simple_utilities import *

class GPModel():
    def __init__(self, graph, node_names):
        self.graph = graph
        self.recreate_index(node_names)
        self.clear_all_manipulable_state()

    def recreate_index(self, node_names):
        self.trie = CharTrie()
        for name in node_names:
            self.trie[name] = True

    def clear_all_manipulable_state(self):
        self.nodes = ['']
        self.clear_field_entry_handling_state()

    def clear_field_entry_handling_state(self):
        self.cached_typed_prefix = None
        self.full_completion_candidate = None
        self.neighbor = None

    def number_nodes(self):
        return len(self.nodes)

    def field(self):
        return self.nodes[-1]

    def set_field(self, n):
        self.nodes[-1] = n
        if not self.check_node_validity(n):
            print("Warning: Invalid node name query string was allowed in to model.")
            exit()

    def clear_field(self):
        self.nodes[-1] = ""

    def check_node_validity(self, n):
        if n == "":
            return True
        try:
            it = self.trie.iteritems(prefix=n)
            matches = [elt[0] for elt in it]
            if len(matches) != 0:
                common = common_prefix(matches)
                if(len(common) >= len(n)):
                    return True
        except KeyError as ke:
            return False
        return False

    def get_inevitable_name_completion(self):
        inevitable_name_completion = None
        try:
            it = self.trie.iteritems(prefix=self.field())
            matches = [elt[0] for elt in it]
            if len(matches) != 0:
                common = common_prefix(matches)
                if(len(common) >= len(self.field())):
                    inevitable_name_completion = common[len(self.field()):len(common)]
        except KeyError as ke:
            inevitable_name_completion = None

        return inevitable_name_completion
