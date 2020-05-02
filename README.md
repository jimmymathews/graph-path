
![example.gif](example.gif)

graph-path (gp)
===============

Installation <a name="Installation"></a>
------------

Currently supported only in Linux/Mac/Unix environments. Does not require root privileges.

The install script requires `bash`:
```
./install.sh
exec bash
```

The `exec bash` line reloads the shell so that `gp` and `man gp` are available right away without starting a new shell. The program itself only requires Python.

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
