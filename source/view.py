
from ansi_codes import *
from model import GPModel

class GPView():
    def __init__(self, model, using_vertical_layout):
        self.model = model
        self.using_vertical_layout = using_vertical_layout
        self.print_command = print # In case a future version wants to print somewhere else
        self.do_cached_clear_command = lambda : self.print_command(UP_LINE)

    def post_cached_view_and_reset(self):
        self.do_cached_clear_command()
        self.print_command(self.cached_base_view)
        if(self.using_vertical_layout):
            self.print_command()
        self.do_cached_clear_command = lambda : self.print_command(UP_LINE)

    def refresh(self):
        self.compute_base_view()
        self.do_cached_clear_command()
        self.print_command(self.cached_base_view + self.compute_edited_field() + self.compute_go_back_up())
        self.compute_new_clear_command()

    def compute_base_view(self):
        self.cached_base_view = ""
        if self.using_vertical_layout:
            connection_divider = '\n'
        else:
            connection_divider = GREEN + " - " + RESET
        ns = self.model.nodes
        wrap_node = lambda node : BOLD_CYAN + node + RESET
        if self.description_capable() and len(ns)>1 and self.using_vertical_layout:
            max_length = max([len(node) for node in ns[0:(len(ns)-1)]])
            wrap_node = (lambda node :
                    BOLD_CYAN + node + RESET +
                    ' '*(1+max_length - len(node)) +
                    YELLOW +
                    (self.model.descriptions_dict[node] if node in self.model.descriptions_dict.keys() else "<missing>") +
                    RESET )
        self.cached_base_view = connection_divider.join([wrap_node(node) for node in ns[0:(len(ns)-1)]])

    def description_capable(self):
        return self.model.descriptions_dict != None

    def compute_edited_field(self):
        if len(self.model.nodes) == 1:
            prompt = ""
        else:
            if self.using_vertical_layout:
                prompt = '\n'
            else:
                prompt = GREEN + '...' + RESET

        edited_field = prompt
        last_node = self.model.nodes[-1]
        if(last_node != ''):
            edited_field += BOLD_MAGENTA + last_node + RESET
            edited_field += MAGENTA + self.model.get_inevitable_name_completion() + RESET
        edited_field += CURSOR_CHAR
        return edited_field

    def compute_new_clear_command(self):
        lines = len(self.model.nodes) if self.using_vertical_layout else 1
        down_clear = (CLEAR_LINE+'\n')*lines
        go_back_up = self.compute_go_back_up()
        self.do_cached_clear_command = lambda : self.print_command(down_clear + go_back_up + UP_LINE) # stores how to clear view later

    def compute_go_back_up(self):
        lines = len(self.model.nodes) if self.using_vertical_layout else 1
        return UP_LINE*lines
