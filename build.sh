#!/bin/bash

zip -r graph_path.tmp.zip *.py
echo -e "#!/usr/bin/env python" > graph_path.zip
cat graph_path.tmp.zip >> graph_path.zip
rm graph_path.tmp.zip
chmod +x graph_path.zip
