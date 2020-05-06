
from pygtrie import *
from simple_utilities import *
from terminal_utilities import *
from model import GPModel
from view import GPView

class GPController:
    def __init__(self, graph, using_vertical_layout, description_capable, lettercase_insensitive):
        self.number_exit_like_requests=0
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
        if ord(c) >= 32 and ord(c) <= 126:
            self.handle_ordinary_char(c)
        else:
            self.handle_control_char(c)

    def handle_ordinary_char(self, c):
        c = self.lettercase_handler(c)
        n = self.model.field() + c
        ic = self.compute_inevitable_completion(n)
        if ic == None:
            self.model.clear_field_entry_handling_state()
            self.model.clear_field()
            self.model.partial_name_completion = "" # manage reset of this somewhere else
        elif len(ic)>= 0:
            self.model.set_field(n)
            self.model.partial_name_completion = ic

    def handle_control_char(self, c):
        if c == '':
            print("Warning: Received empty char input. Aborting.")
            exit()

        if c != '\t':
            self.stop_tab_completion()

        if c == '\t':
            self.handle_tab_completion_request()
            return

        if c == '\r' or c == '\n':
            self.handle_enter_request()
            return

        if ord(c) == 127:
            self.handle_backspace()

    def handle_tab_completion_request(self):
        if (self.model.field() == '' or self.model.neighbor is not None):
            self.show_next_neighbor()
            return
        elif self.model.partial_name_completion is not None:
            self.commit_to_name_completion()
            return

        # if self.model.partial_name_completion == '':
        #     self.advance_editor()

    def handle_enter_request(self):
        if(self.number_exit_like_requests == 0):
            advanced = self.advance_editor()
            if not advanced:
                self.number_exit_like_requests = self.number_exit_like_requests + 1
            else:
                self.number_exit_like_requests = 0
            return

        if(self.number_exit_like_requests == 1):
            self.view.post_cached_view_and_reset()
            self.model.clear_all_manipulable_state()
            self.number_exit_like_requests = self.number_exit_like_requests + 1
            return

        if(self.number_exit_like_requests == 2):
            exit()

    def handle_backspace(self):
        if(self.model.field() == ''):
            self.regress_editor()
        else:
            self.lop_off_char()


    def show_next_neighbor(self):
        if len(self.model.nodes) <= 1:
            return
        g = self.model.graph
        neighbors = g.neighbors(g.vs.select(name=self.model.nodes[-2])[0])
        if self.model.neighbor is not None:
            self.model.neighbor = (self.model.neighbor + 1) % len(neighbors)
        else:
            self.model.neighbor = 0
        self.model.set_field(g.vs[neighbors[self.model.neighbor]]['name'])
        self.model.partial_name_completion = ''
        self.view.refresh()

    def commit_to_name_completion(self):
        if len(self.model.partial_name_completion) > 0:
            self.model.set_field(self.model.field() + self.model.partial_name_completion)
            self.model.partial_name_completion = ''
            self.view.refresh()
        else:
            self.handle_ordinary_char('')
            if(self.model.cached_node_name_entry_prefix is None):
                self.model.cached_node_name_entry_prefix = self.model.field()
            m = self.model.completion_candidates[self.model.completion_candidate_index]
            self.model.set_field(self.model.cached_node_name_entry_prefix + m[len(self.model.cached_node_name_entry_prefix):len(m)])
            self.view.refresh()
            self.model.completion_candidate_index = (self.model.completion_candidate_index + 1) % len(self.model.completion_candidates)

    def stop_tab_completion(self):
        self.model.clear_field_entry_handling_state()

    def node_name_query_exact_match(self):
        # node = self.model.nodes[-1]
        node = self.model.field()
        pygtrie_status = self.model.trie.get(node)
        if pygtrie_status is not None:
            return True
        else:
            return False

    def node_name_query_is_prefix(self):
        # node = self.model.nodes[-1]
        node = self.model.field()
        pygtrie_status = self.model.trie.get(node)
        if self.model.trie.has_subtree(node):
            return True
        else:
            return False

    def advance_editor(self):
        if self.node_name_query_exact_match():
            if len(self.model.nodes)>1:
                self.lookup_path()
            else:
                self.model.nodes.append('')
            return True
            # self.model.partial_name_completion = None #?
        return False
        # else:

        #     if self.node_name_query_is_prefix():
        #         j

    def regress_editor(self):
        # ns = self.model.nodes
        if(len(self.model.nodes) > 1 and self.model.field() == ''):
            self.model.nodes.pop()
            # ns[-1] = ''
            self.model.clear_field()
        self.model.partial_name_completion = None        

    def compute_inevitable_completion(self, n):
        it = self.model.trie.iteritems(prefix=n)
        try:
            matches = [elt[0] for elt in it]
            if(self.model.cached_node_name_entry_prefix is None):
                self.model.completion_candidates = matches
            if len(self.model.completion_candidates) != 0:
                common = common_prefix(self.model.completion_candidates)
                if(len(common) >= len(n)):
                    return common[len(n):len(common)]
                    # self.model.partial_name_completion = common[len(n):len(common)]
                    # ns[-1] = n
        except KeyError as ke:
            return None
            # ns[-1] = ''
            # self.model.partial_name_completion = ''
        return ""

    def lop_off_char(self):
        # ns = self.model.nodes
        f = self.model.field()
        if(f != ''):
            self.model.set_field(f[0:(len(f)-1)])
            self.handle_ordinary_char('')

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

