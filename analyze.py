#!/usr/bin/env python3
"""
Forwarding wrapper for analyse.py
"""
import os
import sys

analyse_script = os.path.join(os.path.dirname(__file__), "analyse.py")
os.execv(sys.executable, [sys.executable, analyse_script] + sys.argv[1:])
