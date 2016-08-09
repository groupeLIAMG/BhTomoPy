# -*- coding: utf-8 -*-

"""
    Copyright 2016 Bernard Giroux
    email: bernard.giroux@ete.inrs.ca
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it /will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import numpy as np
cimport numpy as np

cimport csegy

#cdef struct c_bin_header:
#    int jobid
#    int lino
#    int reno
#    short ntrpr
#    short nart
#    unsigned short hdt
#    unsigned short dto
#    unsigned short hns
#    unsigned short nso
#    short format
#    short fold
#    short tsort
#    short vscode
#    short hsfs
#    short hsfe
#    short hslen
#    short hstyp
#    short schn
#    short hstas
#    short hstae
#    short htatyp
#    short hcorr
#    short bgrcv
#    short rcvm
#    short mfeet
#    short polyt
#    short vpol
#    unsigned short rev
#    short fixl
#    short extfh


class Segy_data():
    bh=0     # binary header
    th=0     # trace headers
    data=0   # traces

def read_segy(segyfile, traceNo=None, fields=None, thDict=None, wordLength=None):
    """
    READ_SEGY - read the content of a SEG-Y file
    s = read_segy(segyfile, traces, fields, dict, word_length)

    Input:
        segyfile (mandatory) : name of SEG-Y file
        traces (optional)  : list of desired traces within the file
        fields (optional)  : list of indices or names of trace header word to retrieve
        dict (optional)  : custom dictionary for trace header (list of strings)
        word_length (optional)  : word length in bytes for trace header (list of int)
                              (mandatory if dict given)
	               - sum(word_length) must be less than 241
                    - numel(word_length) must equal numel(dict)
                    - 4-byte IBM float words are handled by setting word_length=5

    Output:
        s : instance of a class with the following attributes
                - the binary header data (s.bh)
                - the trace header data (s.th)
                - the trace data (s.data)

    Caveat:
        Text headers are not read
        Traces of variable length are not handled (results unpredictable)
    
    """
    s = Segy_data()
    s.bh = dict()
    s.th = dict()
    
    cdef bytes py_bytes = segyfile.encode()
    cdef char* filename = py_bytes    
    
    cdef int retval = 0
    
    retval = csegy.read_segy_b_header(filename, s.bh)
    
    if retval == 1:
        raise IOError('Problem opening segy file')
    elif retval == 2:
        raise RuntimeError('Problem parsing binary header')
        
    if traceNo is None:
        traceNo = list()
    else:
        traceNo = list(traceNo)
        
    if fields is not None:
        fields = list(fields)   # make sure we have list instances
        if thDict is None:
            thDict = list()
        else:
            thDict = list(thDict)
        if wordLength is None:
            wordLength = list()
        else:
            wordLength = list(wordLength)
        retval = csegy.read_segy_tr_headers(filename, traceNo, fields, thDict, wordLength, s.th)

        if retval == 1:
            raise IOError('Problem opening segy file')
        elif retval == 2:
            raise RuntimeError('Problem parsing trace headers')

    s.data = csegy.read_segy_data(filename, traceNo)
    if type(s.data) is int:
        retval = s.data
    else:
        retval = 0
    
    if retval == 1:
        raise IOError('Problem opening segy file')
    elif retval == 2:
        raise RuntimeError('Problem parsing trace data')

    return s
