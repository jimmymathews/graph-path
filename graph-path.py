#!/usr/bin/python

version = "0.1"

import argparse
from igraph import Graph
import sys
import os
from pygtrie import *
from enum import Enum

try:
    import tty, termios
except ImportError:
    try:
        import msvcrt
    except ImportError:
        raise ImportError('getch not available')
    else:
        getch = msvcrt.getch
else:
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

red = "\u001b[0;31m"
grn = "\u001b[0;32m"
yel = "\u001b[0;33m"
blu = "\u001b[0;34m"
mag = "\u001b[0;35m"
cyn = "\u001b[0;36m"
res = "\u001b[0m"

bold_red = "\u001b[1;31m"
bold_grn = "\u001b[1;32m"
bold_yel = "\u001b[1;33m"
bold_blu = "\u001b[1;34m"
bold_mag = "\u001b[1;35m"
bold_cyn = "\u001b[1;36m"
bold_res ="\u001b[0m\u001b[1m"

up_line     = "\u001b[1A"
clear_line  = "\u001b[K"
push_cursor = "\u001b[s"
pop_cursor  = "\u001b[u"
cursor_char = "\u001b[47m \u001b[0m"

def common_prefix(strings):
    if len(strings) == 1:
        return strings[0]
    accumulator = ""
    k=min([len(s) for s in strings])
    while True:
        next_char = strings[0][len(accumulator)]
        for string in strings:
            if next_char != string[len(accumulator)]:
                return accumulator
        accumulator += next_char
        if k == len(accumulator):
            return accumulator

class GUI:
    def __init__(self, graph, vertical, description_capable, case_insensitive):
        self.reset_state()
        self.graph = graph
        self.case_insensitive = case_insensitive
        case_manager = lambda x:x
        if(self.case_insensitive):
            case_manager = lambda x: x.upper()
        node_names = sorted([case_manager(graph.vs[i]["name"]) for i in range(len(graph.vs))])
        # self.prefix_set = PrefixSet(iterable=node_names, factory=CharTrie)
        self.trie = CharTrie()
        for name in node_names:
            self.trie[name] = True
        self.vertical = vertical
        self.description_capable = description_capable
        self.tick=0

    def reset_state(self):
        self.nodes = [""]
        self.completion = None
        self.lines = 1
        self.candidate = 0
        self.pushed = None
        self.neighbor = None

    def display_abridged_cached(self):
        print(self.cached)
        if(self.vertical):
            print(clear_line)
            print(up_line)

    def display(self):
        txt = (clear_line + '\n')*self.lines + self.lines*up_line
        self.lines = 1
        for i,n in enumerate(self.nodes):
            if i == len(self.nodes)-1:
                if(n != "" and self.completion != None):
                    txt += bold_mag + n + res
                    txt += mag + self.completion + res
                txt += cursor_char
            else:
                if i == len(self.nodes)-2:
                    divider_str = grn + "..." + res
                else:
                    divider_str = " " + grn + "-" + res + " "
                if(not self.vertical):
                    divider =  divider_str
                else:
                    divider =  "\n"
                    self.lines = self.lines + 1
                txt += bold_cyn + n + res
                if i == len(self.nodes)-2:
                    self.cached = txt
                txt += divider
            if i == 0:
                self.cached = ""
        print(txt)
        footer = self.lines*up_line + up_line
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
                    print(clear_line)
                exit()
            return
        self.tick = 0

        if c=='\t' and (self.nodes[-1] == "" or self.neighbor is not None):
            self.complete_with_neighbors()
            return
        elif c=='\t' and self.completion is not None:
            self.auto_complete()
            return
        
        if c=='' or c==' ' or (c=='\t' and self.completion==""):
            self.advance_editor()
        elif ord(c) >= 32 and ord(c) <= 126:
            if self.case_insensitive:
                c = c.upper()
            self.append(c)
        elif ord(c) == 127:
            if(self.nodes[-1] == ""):
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
        self.nodes[-1] = self.graph.vs[neighbors[self.neighbor]]["name"]
        self.completion = ""
        self.display()

    def auto_complete(self):
        if len(self.completion) > 0:
            self.nodes[-1] = self.nodes[-1] + self.completion
            self.completion = ""
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
        if self.completion == "":
            if len(self.nodes)>1:
                self.lookup_path()
            else:
                self.nodes = self.nodes + [""]
            self.completion = None

    def regress_editor(self):
        if(len(self.nodes) > 1 and self.nodes[-1] == ""):
            self.nodes = self.nodes[0:(len(self.nodes)-1)]
            self.nodes[-1] = ""
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
            self.nodes[-1] = ""
            self.completion = ""

    def lop_off_char(self):
        if(self.nodes[-1] != ""):
            self.nodes[-1] = self.nodes[-1][0:(len(self.nodes[-1])-1)]
            self.append("")

    def lookup_path(self):
        v1 = self.graph.vs.select(name=self.nodes[-2])[0]
        v2 = self.graph.vs.select(name=self.nodes[-1])[0]
        shortest_paths = self.graph.get_shortest_paths(v1, to=v2, mode="ALL", output="vpath")
        if len(shortest_paths) > 0:
            p = shortest_paths[0]
            ns = self.nodes
            self.nodes = (
                ns[0:(len(ns)-2)] +
                [self.graph.vs[selector]["name"] for selector in p] +
                [""] )

def parse_input():
    parser = argparse.ArgumentParser(description=("graph-path  Explore paths in a graph" + " " + version))
    parser.add_argument('graph_file',           type=str, nargs=1, help='format is graphml with a "name" attribute. Edge list format is also acceptable, using space-separated integer pairs. Formats automatically detected by the igraph library may also work.')
    parser.add_argument('-n', '--names',        type=str, nargs=1, help='(optional) comma or tab separated values with 2 columns: node name as it appears (graph_file), and a preferred alias. This is useful if the node names in graph file are not the preferred names.')
    parser.add_argument('-d', '--descriptions', type=str, nargs=1, help='(optional) comma or tab separated values with 2 columns: node name (or alias), and longer description.')
    parser.add_argument('-v', '--vertical',   action='store_true', help='(optional) if set, lists nodes vertically (this is easier for copy and paste).')
    parser.add_argument('-c', '--case',       action='store_true', help='(optional) if set, character input is case-insensitive (convenient if node names are capitalized).')
    parser.add_argument('-s', '--stats',      action='store_true', help='(optional) show statistics.')
    args = parser.parse_args()
    graph_file = args.graph_file[0]
    graph = Graph.Read(graph_file)
    description_capable = False
    return [graph, args.stats, args.vertical, description_capable, args.case]

class CursorOff(object):
    def __enter__(self):
        os.system('setterm -cursor off')

    def __exit__(self, *args):
        os.system('setterm -cursor on')


[graph, show_stats, vertical, description_capable, case_insensitive] = parse_input()

if show_stats:
    print(grn + " average path length = " + bold_grn + str(0.1*round(10*graph.average_path_length())))
    print(grn + "            diameter = " + bold_grn + str(graph.diameter()))

gui = GUI(graph, vertical, description_capable, case_insensitive)
with CursorOff():
    while True:
        c = getch()
        gui.handle_char_input(c)
        gui.display()
