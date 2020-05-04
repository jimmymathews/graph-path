
from ansi_codes import *
from model import GPModel

class GPView():
    def __init__(self, model, vertical_layout, description_capable):
        self.model = model
        self.vertical_layout = vertical_layout
        self.description_capable = description_capable
        self.reset_state()

    def reset_state(self):
        self.lines = 1

    def display_abridged_cached(self):
        print(self.cached)
        if(self.vertical_layout):
            print(CLEAR_LINE)
            print(UP_LINE)

    def refresh(self):
        ns = self.model.nodes
        txt = (CLEAR_LINE + '\n')*self.lines + self.lines*UP_LINE
        self.lines = 1
        for i,n in enumerate(ns):
            if i == len(ns)-1:
                if(n != '' and self.model.completion != None):
                    txt += BOLD_MAGENTA + n + RESET
                    txt += MAGENTA + self.model.completion + RESET
                txt += CURSOR_CHAR
            else:
                if i == len(ns)-2:
                    divider_str = GREEN + '...' + RESET
                else:
                    divider_str = ' ' + GREEN + '-' + RESET + ' '
                if(not self.vertical_layout):
                    divider =  divider_str
                else:
                    divider =  '\n'
                    self.lines = self.lines + 1
                txt += BOLD_CYAN + n + RESET
                if i == len(ns)-2:
                    self.cached = txt
                txt += divider
            if i == 0:
                self.cached = ''
        print(txt)
        footer = self.lines*UP_LINE + UP_LINE
        print(footer)
