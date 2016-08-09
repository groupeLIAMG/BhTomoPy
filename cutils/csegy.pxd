# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 09:00:30 2016

@author: giroux
"""

cdef extern from "csegy.h":
    int read_segy_b_header(const char*, object)
    int read_segy_tr_headers(const char*, object, object, object, object, object)
    object read_segy_data(const char*, object)

    