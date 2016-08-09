
#ifndef _CSEGY_H_
#define _CSEGY_H_

#include "string.h"

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "Python.h"
#include "numpy/ndarrayobject.h"



int read_segy_b_header(const char*, PyObject*);
int read_segy_tr_headers(const char*, PyObject*, PyObject*, PyObject*, PyObject*, PyObject*);
PyObject* read_segy_data(const char*, PyObject*);

#endif