
def GPView():
init

    def display_abridged_cached(self):
        print(self.cached)
        if(self.vertical_layout):
            print(CLEAR_LINE)
            print(UP_LINE)

    def refresh(self):
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
