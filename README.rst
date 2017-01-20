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

Please download mtcars.txt_ and run bkheatmap as follows:

.. _mtcars.txt: https://gist.githubusercontent.com/wwliao/9ee916c1c0295b2f570e239bc91581b3/raw/a961160be56810cb0a461d86d3a04012a89a713f/mtcars.txt

Use as a module in the Python script

.. code-block:: python

   import os
   import pandas as pd
   from bkheatmap import bkheatmap

   infile = "mtcars.txt"
   prefix = os.path.splitext(infile)[0]

   df = pd.read_table(infile, index_col=0)
   bkheatmap(df, prefix=prefix, scale="column")

Or use as a command in the shell

.. code-block:: bash

   $ bkheatmap --scale column mtcars.txt

Then a HTML file will be generated like this_.

.. _this: http://wwliao.name/downloads/mtcars.bkheatmap.html

