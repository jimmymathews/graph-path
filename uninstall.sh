#!/bin/bash

red="\u001b[0;31m"
grn="\u001b[0;32m"
bold_res="\u001b[0m\u001b[1m"
res="\u001b[0m"

# args: file should_be_present
remove_if_not_missing() {
    the_file="$1"
    if [ $# -gt 1 ]; then
        should_be_present="$2"
    else
        should_be_present="true"
    fi
    if [[ -f $the_file ]]; then
        rm $the_file
        echo -e "$bold_res$the_file$res$grn removed.$res"
    else
        if [[ "$should_be_present" == "true" ]]; then
            echo -e "$bold_res$the_file$res$red was missing anyway.$res"
        fi
    fi
}

remove_if_not_missing "$HOME/bin/graph-path"
remove_if_not_missing "$HOME/bin/gp"
remove_if_not_missing "$HOME/man/man1/graph-path.1.gz"
remove_if_not_missing "$HOME/man/man1/gp.1.gz"
remove_if_not_missing "$HOME/man/man1/graph-path.1" false
remove_if_not_missing "$HOME/man/man1/gp.1" false
