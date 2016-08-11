#
# python setup.py build_ext --inplace

import numpy as np
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


extensions = [
    Extension('cutils.cgrid2d',
              sources=['./cutils/cgrid2d.pyx', './cutils/Grid2Dttcr.cpp'],  # additional source file(s)
              include_dirs=['./cutils/',np.get_include()],
              language='c++',             # generate C++ code
              extra_compile_args=['-std=c++11'],),
    Extension('cutils.segy',
              sources=['./cutils/segy.pyx', './cutils/csegy.c'],  # additional source file(s)
              include_dirs=['./cutils/',np.get_include()],
              extra_compile_args=['-std=c99'],),
]

setup(
    name='cutils',
    ext_modules = cythonize(extensions, include_path=['./cutils/',]),
)
