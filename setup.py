#!/usr/bin/python

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "pyabm",
    version = "0.4dev",
    packages = find_packages(),
    package_data = {'pyabm' : ['rcparams.default',
                               'pyabmrc.windows',
                               'pyabmrc.linux']},
    zip_safe = True,
    install_requires = ['numpy >= 1.6.1',
                        'matplotlib >= 0.98.4',
                        'GDAL >= 1.6'],
    author = "Alex Zvoleff",
    author_email = "azvoleff@mail.sdsu.edu",
    description = "Agent-based modeling toolkit",
    keywords = "agent-based modeling ABM simulation model",
    license = "GPL v3 or later",
    url = "http://rohan.sdsu.edu/~zvoleff/research/pyabm",   # project home page, if any
    long_description = ''.join(open('README.rst').readlines()[6:]),
	classifiers = [
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Life",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules"]
)
