
from pygtrie import *
from simple_utilities import *
from terminal_utilities import *
from model import GPModel
from view import GPView

class GPController:
    def __init__(self, graph, using_vertical_layout, description_capable, lettercase_insensitive):
        self.enter_count=0
        self.using_vertical_layout = using_vertical_layout
        self.description_capable = description_capable
        self.lettercase_insensitive = lettercase_insensitive
        self.lettercase_handler = lambda x : x
        if(self.lettercase_insensitive):
            self.lettercase_handler = lambda x : x.upper()
        node_names = sorted([self.lettercase_handler(graph.vs[i]['name']) for i in range(len(graph.vs))])
        if(self.lettercase_insensitive):
            graph.vs["uppercase name"] = node_names
        self.model = GPModel(graph, node_names)
        self.view = GPView(self.model, using_vertical_layout, description_capable)
        self.reset_state()

    def reset_state(self):
        self.model.reset_manipulable_state()
        self.candidate = 0
        self.pushed = None
        self.neighbor = None

    def handle_io(self):
        '''
        Boilerplate MVC controller handling loop.
        '''
        with CursorOff():
            gc = GetChar()
            while True:
                c = gc.get_char()
                self.handle_char_input(c)
                self.view.refresh()

    def handle_char_input(self, c):
        ns = self.model.nodes

        if c!='\t':
            self.pushed = None
            self.candidate = 0
            self.matches = []
            self.neighbor = None

        if c=='\r' or c=='\n':
            if(self.enter_count == 0):
                self.advance_editor()
            self.enter_count = self.enter_count + 1
            if(self.enter_count == 2):
                self.view.push_up_cached_view()
                self.reset_state()
            if(self.enter_count == 3):
                exit()
            return
        self.enter_count = 0

        if c=='\t' and (ns[-1] == '' or self.neighbor is not None):
            self.show_next_neighbor()
            return
        elif c=='\t' and self.model.partial_name_completion is not None:
            self.complete_partial_name()
            return
        
        if c=='' or c==' ' or (c=='\t' and self.model.partial_name_completion==''):
            self.advance_editor()
        elif ord(c) >= 32 and ord(c) <= 126:
            c = self.lettercase_handler(c)
            self.append(c)
        elif ord(c) == 127:
            if(ns[-1] == ''):
                self.regress_editor()
            else:
                self.lop_off_char()

    def show_next_neighbor(self):
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
        self.model.partial_name_completion = ''
        self.view.refresh()

    def complete_partial_name(self):
        ns = self.model.nodes
        if len(self.model.partial_name_completion) > 0:
            ns[-1] = ns[-1] + self.model.partial_name_completion
            self.model.partial_name_completion = ''
            # self.model.partial_name_completion = None # Check if this is full completion?
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
        if self.model.partial_name_completion == '':
            if len(ns)>1:
                self.lookup_path()
            else:
                ns.append('')
            self.model.partial_name_completion = None

    def regress_editor(self):
        ns = self.model.nodes
        if(len(ns) > 1 and ns[-1] == ''):
            ns.pop()
            ns[-1] = ''
        self.model.partial_name_completion = None        

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
                    self.model.partial_name_completion = common[len(n):len(common)]
                    ns[-1] = n
        except KeyError as ke:
            ns[-1] = ''
            self.model.partial_name_completion = ''

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

