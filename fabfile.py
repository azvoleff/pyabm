from fabric.api import local, task

from tempfile import mkstemp
from shutil import move
from os import remove, close
from re import sub

python = "C:/Python27/python.exe"
python64 = "C:/Python27_64bit/python.exe"
sphinx_build = "C:/Python27/Scripts/sphinx-build.exe"
sphinx_build64 = "C:/Python27_64bit/Scripts/sphinx-build.exe"

def replace(file_path, pattern, subst):
    fh, abs_path = mkstemp()
    new_file = open(abs_path, 'w')
    old_file = open(file_path)
    for line in old_file:
        new_file.write(sub(pattern, subst, line))
    new_file.close()
    close(fh)
    old_file.close()
    remove(file_path)
    move(abs_path, file_path)

@task
def update_version(new_release, new_version=None):
    replace('setup.py', "version = '[0-9.]*(dev)?',", "version = '%s',"%new_release)
    if new_version != None:
        replace('doc/conf.py', "version = '[0-9.]*'", "version = '%s'"%new_version)
    replace('doc/conf.py', "release = '[0-9.]*(dev)?'", "release = '%s'"%new_release)
    replace('pyabm/__init__.py', "__version__ = '[0-9.]*(dev)?'", "__version__ = '%s'"%new_release)

@task
def generate_docs():
    local("%s -b dirhtml -d doc\_build\doctrees doc doc\_build\html"%sphinx_build64)
    #local("%s -b pdf -d doc\_build\doctrees doc doc\_build\pdf"%sphinx_build)

@task
def upload_to_pypi():
    local("%s setup.py register sdist bdist_egg bdist_wininst upload"%python)
    local("%s setup.py register sdist bdist_egg bdist_wininst upload"%python64)
