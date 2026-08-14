# Copyright (c) 2026 Morpheus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Conway's Game of Life

A simple Conway's Game of Life in Python, using the ``pygame-ce`` library.
Read about CGoL here: https://conwaylife.com/wiki/Conway%27s_Game_of_Life
"""

__version__ = "1.0.1"
__author__ = "Morpheus"

from .cell import Cell
from .control_panel import ControlPanel
from .event_handler import EventHandler
from .grid import Grid
from .settings import Settings
from .game import ConwaysGameOfLife

__all__ = [
    "Cell", "ConwaysGameOfLife", "ControlPanel", "EventHandler", "Grid",
    "Settings"
]
