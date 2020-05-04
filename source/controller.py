
from pygtrie import *
from simple_utilities import *
from terminal_utilities import *
from model import GPModel
from view import GPView

class GPController:
    def __init__(self, graph, vertical_layout, description_capable, case_insensitive):
        self.tick=0
        self.vertical_layout = vertical_layout
        self.description_capable = description_capable
        self.case_insensitive = case_insensitive
        case_manager = lambda x : x
        if(self.case_insensitive):
            case_manager = lambda x : x.upper()
        node_names = sorted([case_manager(graph.vs[i]['name']) for i in range(len(graph.vs))])
        self.model = GPModel(graph, node_names)
        self.view = GPView(self.model, vertical_layout, description_capable)
        self.reset_state()

    def handle_io(self):
        with CursorOff():
            gc = GetChar()
            while True:
                c = gc.get_char()
                self.handle_char_input(c)
                self.view.refresh()

    def reset_state(self):
        self.model.reset_state()
        self.view.reset_state()
        self.candidate = 0
        self.pushed = None
        self.neighbor = None

    def handle_char_input(self, c):
        ns = self.model.nodes

        if c!='\t':
            self.pushed = None
            self.candidate = 0
            self.matches = []
            self.neighbor = None

        if c=='\r' or c=='\n':
            if(self.tick == 0):
                self.advance_editor()
            self.tick = self.tick + 1
            if(self.tick == 2):
                self.view.display_abridged_cached()
                self.reset_state()
            if(self.tick == 3):
                for i in range(self.view.lines - 1):
                    print(CLEAR_LINE)
                exit()
            return
        self.tick = 0

        if c=='\t' and (ns[-1] == '' or self.neighbor is not None):
            self.complete_with_neighbors()
            return
        elif c=='\t' and self.model.completion is not None:
            self.auto_complete()
            return
        
        if c=='' or c==' ' or (c=='\t' and self.model.completion==''):
            self.advance_editor()
        elif ord(c) >= 32 and ord(c) <= 126:
            if self.case_insensitive:
                c = c.upper()
            self.append(c)
        elif ord(c) == 127:
            if(ns[-1] == ''):
                self.regress_editor()
            else:
                self.lop_off_char()

    def complete_with_neighbors(self):
        ns = self.model.nodes
        if len(ns) <= 1:
            return
        g = self.model.graph
        neighbors = g.neighbors(g.vs.select(name=ns[-2])[0])
        if self.neighbor is not None:
            self.neighbor = (self.neighbor + 1) % len(neighbors)
        else:
            self.neighbor = 0
        ns[-1] = g.vs[neighbors[self.neighbor]]['name']
        self.model.completion = ''
        self.view.refresh()

    def auto_complete(self):
        ns = self.model.nodes
        if len(self.model.completion) > 0:
            ns[-1] = ns[-1] + self.model.completion
            self.model.completion = ''
            self.view.refresh()
        else:
            self.append('')
            if(self.pushed is None):
                self.pushed = ns[-1]
            m = self.matches[self.candidate]
            ns[-1] = self.pushed + m[len(self.pushed):len(m)]
            self.view.refresh()
            self.candidate = (self.candidate + 1) % len(self.matches)

    def advance_editor(self):
        ns = self.model.nodes
        if self.model.completion == '':
            if len(ns)>1:
                self.lookup_path()
            else:
                ns.append('')
            self.model.completion = None

    def regress_editor(self):
        ns = self.model.nodes
        if(len(ns) > 1 and ns[-1] == ''):
            ns.pop()
            ns[-1] = ''
        self.model.completion = None        

    def append(self, c):
        ns = self.model.nodes
        n = ns[-1] + c
        it = self.model.trie.iteritems(prefix=n)
        try:
            matches = [elt[0] for elt in it]
            if(self.pushed is None):
                self.matches = matches
            if len(self.matches) != 0:
                common = common_prefix(self.matches)
                if(len(common) >= len(n)):
                    self.model.completion = common[len(n):len(common)]
                    ns[-1] = n
        except KeyError as ke:
            ns[-1] = ''
            self.model.completion = ''

    def lop_off_char(self):
        ns = self.model.nodes
        if(ns[-1] != ''):
            ns[-1] = ns[-1][0:(len(ns[-1])-1)]
            self.append('')

    def lookup_path(self):
        ns = self.model.nodes
        g = self.model.graph
        v1 = g.vs.select(name=ns[-2])[0]
        v2 = g.vs.select(name=ns[-1])[0]
        shortest_paths = g.get_shortest_paths(v1, to=v2, mode='ALL', output='vpath')
        if len(shortest_paths) > 0:
            p = shortest_paths[0]
            ns.pop()
            ns.pop()
            for selector in p:
                ns.append(g.vs[selector]['name'])    
            ns.append('')

