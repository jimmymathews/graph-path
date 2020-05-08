
from ansi_codes import *
from pygtrie import *  # third-party library
from simple_utilities import *

class GPModel():
    def __init__(self, graph, node_names, descriptions_dict):
        self.graph = graph
        self.descriptions_dict = descriptions_dict
        self.recreate_index(node_names)
        self.clear_state()

    def recreate_index(self, node_names):
        self.trie = CharTrie()
        for name in node_names:
            self.trie[name] = True

    def clear_state(self):
        self.nodes = ['']

    def number_nodes(self):
        return len(self.nodes)

    def field(self):
        return self.nodes[-1]

    def clear_field(self):
        self.nodes[-1] = ""

    def set_field(self, n):
        self.nodes[-1] = n
        if not self.check_node_query_validity(n):
            print(YELLOW+"Warning"+RESET+": Invalid node name query string was allowed in to model.")
            exit()

    def check_node_query_validity(self, node):
        if self.node_name_query_exact_match(node) or self.node_name_query_is_prefix(node):
            return True
        else:
            return False

    def node_name_query_exact_match(self, node):
        pygtrie_status = self.trie.get(node)
        if pygtrie_status is not None:
            return True
        else:
            return False

    def node_name_query_is_prefix(self, node):
        pygtrie_status = self.trie.get(node)
        if self.trie.has_subtrie(node):
            return True
        else:
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
