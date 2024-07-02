"""
********************************************************************************
compas_viewer
********************************************************************************

.. currentmodule:: compas_viewer


.. toctree::
    :maxdepth: 1


"""

from __future__ import print_function

import os


__author__ = ["Li Chen"]
__copyright__ = "COMPAS Association"
__license__ = "MIT License"
__email__ = "li.chen@arch.ethz.ch"
__version__ = "1.2.2"


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all__ = ["HOME", "DATA", "DOCS", "TEMP"]

__all_plugins__ = [
    "compas_viewer.scene",
]

from .viewer import Viewer  # noqa: F401, E402
