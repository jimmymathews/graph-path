#!/usr/bin/bash

if test -f "/usr/local/share/man/man1/graph-path.1.gz"; then
    sudo rm /usr/local/share/man/man1/graph-path.1.gz
fi

if test -f "/usr/local/share/man/man1/gp.1.gz"; then
    sudo rm /usr/local/share/man/man1/gp.1.gz
fi

sudo cp gp.1 /usr/local/share/man/man1/graph-path.1
sudo cp gp.1 /usr/local/share/man/man1/gp.1
sudo gzip /usr/local/share/man/man1/graph-path.1
sudo gzip /usr/local/share/man/man1/gp.1

she="#!"
bang=`echo -e "$(which python)\n"`
echo "$she$bang" > gp
cat graph-path.py >> gp
chmod +x gp
sudo mv gp /usr/local/bin/
if test -f "/usr/local/bin/graph-path"; then
    sudo rm /usr/local/bin/graph-path
fi
sudo ln -s /usr/local/bin/gp /usr/local/bin/graph-path
