
![example.gif](example.gif)

graph-path (gp)
===============

Installation <a name="Installation"></a>
------------

Currently supported only in Linux/Mac/Unix environments. Does not require root privileges.

First install the [igraph library](https://igraph.org/c/#startc) with Python bindings. Depending on your OS and platform, you'll need to use lines like the following:

```
sudo apt install python-igraph
pacman -S python-igraph
brew install igraph
...
pip install python-igraph
```

Then run the bash install script:
```
./install.sh
```

Use `exec bash` to reload the shell so that `gp` and `man gp` are available right away without starting a new shell. The program itself is written in Python.

Uninstallation:
```
./uninstall.sh
```

Usage <a name="Usage"></a>
-----
  - *`regular character`*. Node name query.
  - *`tab`*. Partial completion. Also cycles through full completions, if there are multiple. If no partial node name is entered yet, instead of name completion, it cycles through the neighbors of the previous node.
  - *`enter`*. Finish entering node name, calculate shortest path to previous node and show all nodes. If typed again, starts a new path on a new line. If typed a third time, quits.
  - *`delete`*. If not editing a node name query, deletes last node on current path. Otherwise deletes the last character from the node query.
