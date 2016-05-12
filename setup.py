#!/usr/bin/env python

from setuptools import setup, find_packages

import bkheatmap

version = bkheatmap.__version__

with open("README.rst") as f:
    readme = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().strip().splitlines()

setup(name="bkheatmap",
      version=version,
      description="A Bokeh heatmap for Python",
      long_description=readme,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Visualization",
      ],
      keywords="Bokeh heatmap",
      url="https://github.com/wwliao/bkheatmap",
      author="Wen-Wei Liao",
      author_email="gattacaliao@gmail.com",
      license="GPLv3",
      packages=find_packages(),
      install_requires=install_requires,
      entry_points={
        'console_scripts': ["bkheatmap=bkheatmap:main"],
      },
      include_package_data=True,
      zip_safe=False)
