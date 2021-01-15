# This file creates a way for tests to include the package files locally.
# Use as follows: from .context import ajay

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ajay