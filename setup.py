# -*- coding: utf-8 -*-
"""
Copyright 2017 Bernard Giroux, Elie Dumas-Lefebvre, Jérome Simon
email: Bernard.Giroux@ete.inrs.ca

This file is part of BhTomoPy.

BhTomoPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

#
# python setup.py build_ext --inplace

import numpy as np
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


extensions = [
    Extension('cutils.cgrid2d',
              sources=['./cutils/cgrid2d.pyx', './cutils/Grid2Dttcr.cpp'],  # additional source file(s)
              include_dirs=['./cutils/', np.get_include()],
              language='c++',             # generate C++ code
              extra_compile_args=['-std=c++11'],),
    Extension('cutils.segy',
              sources=['./cutils/segy.pyx', './cutils/csegy.c'],  # additional source file(s)
              include_dirs=['./cutils/', np.get_include()],
              extra_compile_args=['-std=c99'],),
]

setup(
    name='cutils',
    ext_modules=cythonize(extensions, include_path=['./cutils/', ]),
)
