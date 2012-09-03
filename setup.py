import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "pyabm",
    version = ".3dev",
    packages = find_packages(),
    include_package_data = True,
    exclude_package_data = {'': ['.gitignore']},
    zip_safe = True,
    install_requires = ['docutils >= 0.3',
                        'setuptools_git >= 0.3',
                        'numpy >= 1.6.2',
                        'GDAL > 1.6'],

    author = "Alex Zvoleff",
    author_email = "azvoleff@mail.sdsu.edu",
    description = "Agent-based modeling toolkit",
    license = "GPL v3 or later",
    keywords = "agent-based modeling ABM simulation model",
    url = "http://rohan.sdsu.edu/~zvoleff/pyabm.php",   # project home page, if any
    long_description = """
pyabm is an agent-based modeling toolkit written to simplify coding and 
running agent-based models in the Python programming language. pyabm 
includes basic classes for creation of agents, has tools to output model 
results (as text files, plots or ESRI shapefiles), has a parameter handling 
system to ease the process of model testing and validation, and has 
utilities to assist in running multiple scenarios with varying model 
parameters.

Construction of pyabm is supported as part of an ongoing National Science 
Foundation Partnerships for International Research and Education (NSF PIRE) 
project `(grant OISE 0729709) <http://pire.psc.isr.umich.edu>`_
Development of pyabm is ongoing, and the documentation is still a work in 
progress.

See the `pyabm website <http://rohan.sdsu.edu/~zvoleff/research/PyABM.php>`_ 
for more information, past releases, publications, and recent presentations.
""",
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
