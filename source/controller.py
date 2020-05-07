
from pygtrie import *
from terminal_utilities import *
from model import GPModel
from view import GPView

class GPController:
    def __init__(self, graph, using_vertical_layout, description_capable, lettercase_insensitive):
        self.number_exit_like_requests=0
        self.using_vertical_layout = using_vertical_layout
        self.description_capable = description_capable
        self.lettercase_insensitive = lettercase_insensitive
        if(self.lettercase_insensitive):
            for i in range(len(graph.vs)):
                graph.vs[i]['name'] = (graph.vs[i]['name']).upper()
        node_names = sorted([graph.vs[i]['name'] for i in range(len(graph.vs))])
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
        if c == '':
            print("Warning: Received empty char input. Aborting.")
            exit()

        if ord(c) >= 32 and ord(c) <= 126:
            self.handle_ordinary_char(c)
        else:
            self.handle_control_char(c)

    def handle_ordinary_char(self, c):
        n = self.model.field()
        if c != '':
            c = c.upper() if self.lettercase_insensitive else c
            n = self.model.field() + c
        valid = self.model.check_node_validity(n)
        if not valid:
            self.model.clear_field()
            self.model.clear_field_entry_handling_state()
        else:
            self.model.set_field(n)

    def handle_control_char(self, c):
        if c != '\t':
            self.model.clear_field_entry_handling_state()

        if c not in ['\r', '\n']:
            self.number_exit_like_requests = 0

        if c == '\t':
            self.handle_tab_completion_request()
            return

        if c in ['\r', '\n']:
            self.handle_enter_request()
            return

        if ord(c) == 127:
            self.handle_backspace()

    def handle_tab_completion_request(self):
        if self.model.field() == '' or self.model.neighbor is not None:
            self.show_next_neighbor()
            return            

        if self.model.get_inevitable_name_completion() not in [None, '']:
            self.commit_to_inevitable_name_completion()
            return

        self.show_next_full_completion()

        # if self.model.full_completion_candidate is not None:
        #     print("show_next_full_completion")
            # return


    # def cycle_through_full_completions(self):
    #     print("cycle_through_full_completions  ")
    #     if self.model.completion_candidates == []:
    #         print("Recalculated") # not running
    #         self.model.compute_full_completion_candidates(self.model.field())
    #         self.completion_candidate_index = 0

    #     self.model.completion_candidate_index = (self.model.completion_candidate_index + 1) % len(self.model.completion_candidates)
    #     print(self.model.completion_candidates)
    #     print(self.model.completion_candidate_index)
    #     f = self.model.completion_candidates[self.model.completion_candidate_index]
    #     print(f)
    #     self.model.set_field(f)

    def handle_enter_request(self):
        if(self.number_exit_like_requests == 0):
            did_advance = self.advance_editor()
            if not did_advance:
                self.number_exit_like_requests = 1
            return
        if(self.number_exit_like_requests == 1):
            self.view.post_cached_view_and_reset()
            self.model.clear_all_manipulable_state()
            self.number_exit_like_requests = 2
            return
        if(self.number_exit_like_requests == 2):
            exit()

    def handle_backspace(self):
        if(self.model.field() == ''):
            self.regress_editor()
        else:
            self.lop_off_char()

    def regress_editor(self):
        if(self.model.number_nodes() > 1 and self.model.field() == ''):
            self.model.nodes.pop()
            self.model.clear_field()
            self.model.clear_field_entry_handling_state()

    def lop_off_char(self):
        f = self.model.field()
        if(f != ''):
            self.model.set_field(f[0:(len(f)-1)])



            self.handle_ordinary_char('')

    def show_next_full_completion(self):
        if self.model.cached_typed_prefix == None:
            self.model.cached_typed_prefix = self.model.field()
        it = self.model.trie.iteritems(prefix=self.model.cached_typed_prefix)
        matches = [elt[0] for elt in it]
        if self.model.full_completion_candidate is not None:
            self.model.full_completion_candidate = (self.model.full_completion_candidate + 1) % len(matches)
        else:
            self.model.full_completion_candidate = 0
        self.model.set_field(matches[self.model.full_completion_candidate])

    def show_next_neighbor(self):
        if self.model.number_nodes() <= 1:
            return
        g = self.model.graph
        neighbors = g.neighbors(g.vs.select(name=self.model.nodes[-2])[0])
        if self.model.neighbor is not None:
            self.model.neighbor = (self.model.neighbor + 1) % len(neighbors)
        else:
            self.model.neighbor = 0
        self.model.set_field(g.vs[neighbors[self.model.neighbor]]['name'])
        # self.model.partial_name_completion = ''
        # self.view.refresh()

    def commit_to_inevitable_name_completion(self):
        ic = self.model.get_inevitable_name_completion()
        if len(ic) > 0:
            self.model.set_field(self.model.field() + ic)
            self.view.refresh()

    def node_name_query_exact_match(self):
        node = self.model.field()
        pygtrie_status = self.model.trie.get(node)
        if pygtrie_status is not None:
            return True
        else:
            return False

    def node_name_query_is_prefix(self):
        node = self.model.field()
        pygtrie_status = self.model.trie.get(node)
        if self.model.trie.has_subtree(node):
            return True
        else:
            return False

    def advance_editor(self):
        if self.node_name_query_exact_match():
            if self.model.number_nodes()>1:
                self.lookup_path()
            else:
                self.model.nodes.append('')
            self.model.clear_field_entry_handling_state()
            return True
        return False

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

