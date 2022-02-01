#!/usr/bin/env python3
# vim: fileencoding=utf-8
#
"""
Import a TorquePro PID file and transform it into an EngineLink PID file.

The TorquePro filename must be <name>.csv. The resuluting filename will be
 <name>-EL.csv.
"""
import tp_to_el

tp_to_el.main()
