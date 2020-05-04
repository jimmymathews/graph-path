#!/usr/bin/python

version = '0.2'
# Uses 'pygtrie' library, https://github.com/google/pygtrie (released under Apache License 2.0). May 3 2020

# Python standard library
from enum import Enum

# project-level
from pygtrie import *  # third-party library
from terminal_utilities import *
from options_utilities import *
from graph_computations import *
from simple_utilities import *

class GUI:
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

    def reset_state(self):
        self.nodes = ['']
        self.completion = None
        self.lines = 1
        self.candidate = 0
        self.pushed = None
        self.neighbor = None

    def display_abridged_cached(self):
        print(self.cached)
        if(self.vertical_layout):
            print(CLEAR_LINE)
            print(UP_LINE)

    def display(self):
        txt = (CLEAR_LINE + '\n')*self.lines + self.lines*UP_LINE
        self.lines = 1
        for i,n in enumerate(self.nodes):
            if i == len(self.nodes)-1:
                if(n != '' and self.completion != None):
                    txt += BOLD_MAGENTA + n + RESET
                    txt += MAGENTA + self.completion + RESET
                txt += CURSOR_CHAR
            else:
                if i == len(self.nodes)-2:
                    divider_str = GREEN + '...' + RESET
                else:
                    divider_str = ' ' + GREEN + '-' + RESET + ' '
                if(not self.vertical_layout):
                    divider =  divider_str
                else:
                    divider =  '\n'
                    self.lines = self.lines + 1
                txt += BOLD_CYAN + n + RESET
                if i == len(self.nodes)-2:
                    self.cached = txt
                txt += divider
            if i == 0:
                self.cached = ''
        print(txt)
        footer = self.lines*UP_LINE + UP_LINE
        print(footer)

    def handle_char_input(self, c):
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
                # print('\n'*(self.lines-1))
                self.display_abridged_cached()
                self.reset_state()
            if(self.tick == 3):
                for i in range(self.lines - 1):
                    print(CLEAR_LINE)
                exit()
            return
        self.tick = 0

        if c=='\t' and (self.nodes[-1] == '' or self.neighbor is not None):
            self.complete_with_neighbors()
            return
        elif c=='\t' and self.completion is not None:
            self.auto_complete()
            return
        
        if c=='' or c==' ' or (c=='\t' and self.completion==''):
            self.advance_editor()
        elif ord(c) >= 32 and ord(c) <= 126:
            if self.case_insensitive:
                c = c.upper()
            self.append(c)
        elif ord(c) == 127:
            if(self.nodes[-1] == ''):
                self.regress_editor()
            else:
                self.lop_off_char()

    def complete_with_neighbors(self):
        if len(self.nodes) <= 1:
            return
        neighbors = self.graph.neighbors(self.graph.vs.select(name=self.nodes[-2])[0])
        if self.neighbor is not None:
            self.neighbor = (self.neighbor + 1) % len(neighbors)
        else:
            self.neighbor = 0
        self.nodes[-1] = self.graph.vs[neighbors[self.neighbor]]['name']
        self.completion = ''
        self.display()

    def auto_complete(self):
        if len(self.completion) > 0:
            self.nodes[-1] = self.nodes[-1] + self.completion
            self.completion = ''
            self.display()
        else:
            self.append('')
            if(self.pushed is None):
                self.pushed = self.nodes[-1]
            m = self.matches[self.candidate]
            self.nodes[-1] = self.pushed + m[len(self.pushed):len(m)]
            self.display()
            self.candidate = (self.candidate + 1) % len(self.matches)

    def advance_editor(self):
        if self.completion == '':
            if len(self.nodes)>1:
                self.lookup_path()
            else:
                self.nodes = self.nodes + ['']
            self.completion = None

    def regress_editor(self):
        if(len(self.nodes) > 1 and self.nodes[-1] == ''):
            self.nodes = self.nodes[0:(len(self.nodes)-1)]
            self.nodes[-1] = ''
        self.completion = None        

    def append(self, c):
        n = self.nodes[-1] + c
        it = self.trie.iteritems(prefix=n)
        try:
            matches = [elt[0] for elt in it]
            if(self.pushed is None):
                self.matches = matches
            if len(self.matches) != 0:
                common = common_prefix(self.matches)
                if(len(common) >= len(n)):
                    self.completion = common[len(n):len(common)]
                    self.nodes[-1] = n
        except Exception as e:
            # print(e) #debug
            self.nodes[-1] = ''
            self.completion = ''

    def lop_off_char(self):
        if(self.nodes[-1] != ''):
            self.nodes[-1] = self.nodes[-1][0:(len(self.nodes[-1])-1)]
            self.append('')

    def lookup_path(self):
        v1 = self.graph.vs.select(name=self.nodes[-2])[0]
        v2 = self.graph.vs.select(name=self.nodes[-1])[0]
        shortest_paths = self.graph.get_shortest_paths(v1, to=v2, mode='ALL', output='vpath')
        if len(shortest_paths) > 0:
            p = shortest_paths[0]
            ns = self.nodes
            self.nodes = (
                ns[0:(len(ns)-2)] +
                [self.graph.vs[selector]['name'] for selector in p] +
                [''] )

def main():
    [graph, show_statistics, vertical_layout, description_capable, case_insensitive] = parse_options_and_input(version)

    if show_statistics:
        do_show_statistics(graph)

    gui = GUI(graph, vertical_layout, description_capable, case_insensitive)
    with CursorOff():
        gc = GetChar()
        while True:
            gui.handle_char_input(gc.get_char())
            gui.display()

main()
