
import csv
from pygtrie import *
from igraph import plot, layout
from terminal_utilities import *
from model import GPModel
from view import GPView
try:
    import pyperclip
    clipboard_available = True
except ImportError as e:
    clipboard_available = False
    pass

class GPController:
    def __init__(self, graph, using_vertical_layout, description_capable, descriptions_file, lettercase_insensitive, showing_plot, being_quiet, neighborhood_size):
        self.being_quiet = being_quiet
        self.number_exit_like_requests=0
        self.using_vertical_layout = using_vertical_layout
        self.lettercase_insensitive = lettercase_insensitive
        if(self.lettercase_insensitive):
            for i in range(len(graph.vs)):
                graph.vs[i]['name'] = (graph.vs[i]['name']).upper()
        node_names = sorted([graph.vs[i]['name'] for i in range(len(graph.vs))])
        descriptions_dict = None
        if(description_capable):
            descriptions_dict = self.get_descriptions_dict(graph, descriptions_file)
        self.neighborhood_size = neighborhood_size
        self.model = GPModel(graph, node_names, descriptions_dict, being_quiet)
        self.view = GPView(self.model, using_vertical_layout)
        self.showing_plot = showing_plot
        self.clear_field_entry_handling_state()

    def get_descriptions_dict(self, graph, descriptions_file):
        names = graph.vs['name']

        df = open(descriptions_file, "r")
        line1 = df.readlines()[1]
        if '\t' in line1:
            delimiter='\t'
        elif ',' in line1 and sum((1 if c==',' else 0) for c in line1) == 1:
            delimiter=','
        elif ' ' in line1 and sum((1 if c==' ' else 0) for c in line1) == 1:
            delimiter=','
        else:
            self.print_warning("Delimiter in descriptions_file could not be determined; neither tab nor comma nor space.")
            return

        line_count = 0
        for line in open(descriptions_file, 'r'): line_count += 1

        count = 0
        with open(descriptions_file, newline='') as csvfile:
            rows = csv.reader(csvfile, delimiter=delimiter, quotechar='|')
            print()
            descriptions_dict = {}
            for row in rows:
                count = count + 1
                if count == 1:
                    continue
                name = row[0]
                description = row[1]
                # if name in names:
                descriptions_dict[name] = description
                    # self.model.graph.vs.select(name=name)['description_string'] = description
                percent = round(100 * count / line_count)
                print('\r' + UP_LINE + 'Read ' + str(percent) + "% of " + YELLOW + descriptions_file + RESET + " .")
            print(UP_LINE + CLEAR_LINE + UP_LINE )

        missing = sorted(list(set(names).difference(list(descriptions_dict.keys()))))
        if len(missing) > 0:
            # missing_string = '\n'.join(missing[0:(min(len(missing), 15))])
            missing_string = '\n'.join(missing)
            if(len(missing) > 15):
                missing_string = missing_string + "\n...\n"
            self.print_warning("descriptions_file is missing the "+ str(len(missing)) +" node names:\n" + missing_string)
        return descriptions_dict

    def clear_field_entry_handling_state(self):
        self.cached_typed_prefix = None
        self.full_completion_candidate = None
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
        self.check_continuation_conditions(c)
        if ord(c) >= 32 and ord(c) <= 126:
            self.handle_ordinary_char(c)
        else:
            self.handle_control_char(c)

    def check_continuation_conditions(self, c):
        if c == '':
            self.print_warning("Received empty char input. Aborting.")
            exit()
        if c != '\t':
            self.clear_field_entry_handling_state()
        if c not in ['\r', '\n']:
            self.number_exit_like_requests = 0

    def handle_ordinary_char(self, c):
        c = c.upper() if self.lettercase_insensitive else c
        n = self.model.field() + c
        if self.model.check_node_query_validity(n):
            self.model.set_field(n)

    def handle_control_char(self, c):
        if c in ['\r', '\n']:
            self.handle_enter_request()
            return
        if c == '\t':
            self.handle_tab_completion_request()
            return
        if ord(c) == 127:
            self.handle_backspace()
            return  

        print()
        self.print_warning("Unhandled char input. Aborting.")
        exit()

    def handle_enter_request(self):
        if(self.number_exit_like_requests == 0):
            did_advance = self.advance_editor()
            if not did_advance:
                self.number_exit_like_requests = 1
            return
        if(self.number_exit_like_requests == 1):
            self.view.post_cached_view_and_reset()
            if clipboard_available:
                pyperclip.copy('\n'.join(self.model.nodes))
            if self.showing_plot and self.model.nodes != ['']:
                selection_operator = lambda vertex: vertex['name'] in self.model.nodes
                vertices = self.model.graph.vs.select(selection_operator)

                if self.neighborhood_size == 0:
                    graph2 = self.model.graph.subgraph(vertices)
                if self.neighborhood_size == 1:
                    graph2 = self.model.graph.subgraph(sum(self.model.graph.neighborhood(vertices=vertices), []))

                graph2.vs['label'] = graph2.vs['name']
                plot(graph2, layout=graph2.layout("kk"), margin=[60,60,60,60], vertex_size=15, vertex_label_size=18, vertex_color="#6495ED", vertex_label_dist=1.5)
            self.model.clear_state()
            self.number_exit_like_requests = 2
            return
        if(self.number_exit_like_requests == 2):
            exit()

    def advance_editor(self):
        if self.model.node_name_query_exact_match(self.model.field()):
            if self.model.number_nodes()>1:
                self.lookup_path()
            else:
                self.model.nodes.append('')
            self.clear_field_entry_handling_state()
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

    def handle_tab_completion_request(self):
        if self.model.field() == '' or self.neighbor is not None:
            self.show_next_neighbor()
            return            

        if self.model.get_inevitable_name_completion() not in [None, '']:
            self.commit_to_inevitable_name_completion()
            return

        self.show_next_full_completion()

    def handle_backspace(self):
        if(self.model.field() == ''):
            self.regress_editor()
        else:
            self.lop_off_char()

    def regress_editor(self):
        if(self.model.number_nodes() > 1 and self.model.field() == ''):
            self.model.nodes.pop()
            self.model.clear_field()
            self.clear_field_entry_handling_state()

    def lop_off_char(self):
        f = self.model.field()
        if(f != ''):
            self.model.set_field(f[0:(len(f)-1)])

    def show_next_full_completion(self):
        if self.cached_typed_prefix == None:
            self.cached_typed_prefix = self.model.field()
        it = self.model.trie.iteritems(prefix=self.cached_typed_prefix)
        matches = [elt[0] for elt in it]
        if self.full_completion_candidate is not None:
            self.full_completion_candidate = (self.full_completion_candidate + 1) % len(matches)
        else:
            self.full_completion_candidate = 0
        self.model.set_field(matches[self.full_completion_candidate])

    def show_next_neighbor(self):
        if self.model.number_nodes() <= 1:
            return
        g = self.model.graph
        neighbors = g.neighbors(g.vs.select(name=self.model.nodes[-2])[0])
        if self.neighbor is not None:
            self.neighbor = (self.neighbor + 1) % len(neighbors)
        else:
            self.neighbor = 0
        self.model.set_field(g.vs[neighbors[self.neighbor]]['name'])

    def commit_to_inevitable_name_completion(self):
        ic = self.model.get_inevitable_name_completion()
        if len(ic) > 0:
            self.model.set_field(self.model.field() + ic)

    def print_warning(self, message):
        if not self.being_quiet:
            print(YELLOW + "Warning" + RESET + ": " + message)
