#!/bin/sh
# Fox Explorer 6 launcher
FE6_HOME="${FE6_HOME:-@LIBDIR@}"
INI="$FE6_HOME/browser/foxexplorer6.ini"
if [ -f "$INI" ]; then
  exec "$FE6_HOME/@BINARY@" -app "$INI" --name foxexplorer6 --class foxexplorer6 "$@"
else
  exec "$FE6_HOME/@BINARY@" --name foxexplorer6 --class foxexplorer6 "$@"
fi
