import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "PyABM",
    version = ".3dev",
    packages = find_packages(),

    include_package_data = True

    exclude_package_data = {'': ['.gitignore']}

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['docutils>=0.3', 'setuptools_git >= 0.3'],

    # metadata for upload to PyPI
    author = "Alex Zvoleff",
    author_email = "azvoleff@mail.sdsu.edu",
    description = "Agent-based modeling toolkit",
    license = "GPL v3 or later",
    keywords = "agent-based modeling ABM simulation model",
    url = "http://rohan.sdsu.edu/~zvoleff/PyABM.php",   # project home page, if any

    long_description = """
'ChitwanABM' is an agent-based model of the Western Chitwan Valley, Nepal.  The 
model represents a subset of the population of the Valley using a number of 
agent types (person, household and neighborhood agents), environmental 
variables (topography, land use and land cover) and social context variables.

The ChitwanABM model relies on restricted access data from the Chitwan Valley 
Family Study (see below) to generate the agents that populate the model. This 
restricted access data can be obtained by contacting the Inter-university 
Consortium for Political and Social Research (the datasets can be found online 
at: http://dx.doi.org/10.3886/ICPSR04538.v7).

The model was constructed with the support of the National Science Foundation 
Partnerships for International Research and Education program (NSF-PIRE, grant 
OISE 0729709). The code was written by Alex Zvoleff as part of his dissertation 
research at San Diego State University (SDSU) in the Department of Geography. 
Contact Alex Zvoleff or Prof. Li An at SDSU with any questions."""

)
