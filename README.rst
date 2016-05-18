.. image:: https://img.shields.io/badge/python-2.7-blue.svg

.. image:: https://img.shields.io/badge/license-GPLv3-green.svg

Interactive Heatmap for Python
==============================

bkheatmap is a Python module based on Bokeh_ to let you plot the 
interactive heatmaps much easier!

.. _Bokeh: http://bokeh.pydata.org/

Installation
------------

.. code-block:: bash

   $ pip install bkheatmap

Usage
-----

Use as a module in the Python script

.. code-block:: python

   import os
   import pandas as pd
   from bkheatmap import bkheatmap

   infile = "table.txt"
   prefix = os.path.splitext(infile)

   df = pd.read_table(infile, index_col=0)
   bkheatmap(df, prefix=prefix)

Use as a command in the shell

.. code-block:: bash

   $ bkheatmap table.txt

