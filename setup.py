# -*- coding: utf-8 -*-
"""
Copyright 2017 Bernard Giroux, Elie Dumas-Lefebvre, Jerome Simon
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

import platform
import numpy as np
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

include_dirs = ['./cutils/', np.get_include()]
if platform.system() == 'Darwin':
    extra_compile_args = ['-std=c++11', '-stdlib=libc++', '-O3']
    extra_compile_argsC = ['-O3']
    include_dirs.append('/opt/local/include')  # for boost
elif platform.system() == 'Windows':
    extra_compile_args = ['/O2']
    extra_compile_argsC = ['/O2']
    include_dirs=['./cutils/', np.get_include(),
    'C:\\Users\\giroux\OneDrive\Documents\\boost_1_66_0']
elif platform.system() == 'Linux':
    extra_compile_args = ['-std=c++11', '-O3']
    extra_compile_argsC = ['-O3']

extensions = [
    Extension('cutils.segy',
              sources=['./cutils/segy.pyx', './cutils/csegy.c'],  # additional source file(s)
              include_dirs=include_dirs,
              extra_compile_args=extra_compile_argsC,),
]

setup(
    name='cutils',
    ext_modules=cythonize(extensions, include_path=['./cutils/', ]),
)
