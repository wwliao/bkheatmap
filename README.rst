A Bokeh heatmap for Python
==========================

bkheatmap is a Python module based on Bokeh package to let you plot the 
interactive heat maps much easier!

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
   prefix = os.path.splitext(os.path.basename(infile))

   df = pd.read_table(infile, index_col=0)
   bkheatmap(df, prefix=prefix)

Use as a command in the shell

.. code-block:: bash

   $ bkheatmap table.txt

