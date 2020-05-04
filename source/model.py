
from pygtrie import *  # third-party library

class GPModel():
    def __init__(self, graph, vertical_layout, description_capable, case_insensitive):
        self.reset_state()
        self.graph = graph
        self.case_insensitive = case_insensitive
        case_manager = lambda x:x
        if(self.case_insensitive):
            case_manager = lambda x: x.upper()
        node_names = sorted([case_manager(graph.vs[i]['name']) for i in range(len(graph.vs))])
        self.trie = CharTrie()
        for name in node_names:
            self.trie[name] = True
        self.vertical_layout = vertical_layout
        self.description_capable = description_capable
        self.tick=0
