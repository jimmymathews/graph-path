#!/bin/bash

red="\u001b[0;31m"
grn="\u001b[0;32m"
bold_res="\u001b[0m\u001b[1m"
res="\u001b[0m"


## Executable installation

# she="#!"
# bang=`echo -e "$(which python)\n"`
echo "#!/usr/bin/env python" > gp
cat graph-path.py >> gp
chmod +x gp
if [[ ! -d ~/bin ]]; then
    mkdir ~/bin
fi
echo -e "$grn""Installing executable to $bold_res""~/bin/gp$res"
mv gp ~/bin/
if [[ -f ~/bin/graph-path ]]; then
    rm ~/bin/graph-path
fi
ln -s ~/bin/gp ~/bin/graph-path


## Manpage installation
if [[ ! -d ~/man ]]; then
    mkdir ~/man
fi
if [[ ! -d ~/man/man1 ]]; then
    mkdir ~/man/man1
fi

# args: filename_source filename_target
install_man() {
    src=$1
    trg=$2
    cp $src ~/man/man1/$trg
    if [ -f ~/man/man1/"$trg".gz ]; then
        rm ~/man/man1/"$trg".gz
    fi
    gzip ~/man/man1/$trg
}

install_man gp.1 graph-path.1
install_man gp.1 gp.1
echo -e "$grn""Installing manpage to $bold_res""~/man/man1/gp.1.gz$res"


## Add to path

# args: line file
check_if_line_in_file() {
    line="$1"
    the_file="$2"
    while IFS= read -r fline; do
        if [ "$fline" == "$line" ]; then
            line_in_file="true"
            return
        fi
    done < "$the_file"
    line_in_file="false"
}

#args: line file
safe_add_line_to_file() {
    line="$1"
    the_file="$2"
    check_if_line_in_file "$1" "$2"
    case "$line_in_file" in
    "true")
        added_line="false"
    ;;
    "false")
        added_line="true"
        echo "$line" >> "$the_file"    
    ;;
    esac
}

if [[ ! -f ~/.bash_profile ]]; then
    echo -e "$red""Error: $res"".bash_profile""$red not found.$res"
    exit
fi
if [[ ! -f ~/.bashrc ]]; then
    echo -e "$red""Warning: $res"".bashrc""$red not found, can't install manpage.$res"
    bashrc_missing="true"
else
    bashrc_missing="false"
fi

profile_file="$HOME/.bash_profile"
alt_profile_file="$HOME/.bashrc"

bin_path_add='export PATH="$HOME/bin:$PATH"'
man_path_add='export MANPATH="$(manpath -g):$HOME/man"'

safe_add_line_to_file "$bin_path_add" "$profile_file"
if [ "$added_line" == "true" ]; then
    echo -e "$grn""Added $bold_res""~/bin""$grn to path."
fi

if [ ! "$bashrc_missing" == "true" ]; then
    safe_add_line_to_file "$bin_path_add" "$alt_profile_file"
    safe_add_line_to_file "$man_path_add" "$alt_profile_file"
    if [[ "$added_line" == "true" ]]; then
        echo -e "$grn""Added $bold_res""~/man""$grn to path.$res"
        source "$alt_profile_file"
    fi
fi
source "$profile_file"
