from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules = cythonize(['users.py', 'trackManager.py', 'serviceConverter.py', 'jwtManager.py', 'historyManager.py', 'fileUtils.py', 'docManager.py']))