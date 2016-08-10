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
    """
    Class to hold SEG-Y data
    
    Attributes are:
        bh:  Dictionnary containing binary header data
                keys are:
                                (bytes in file)
                jobid            3201-3204
                lino             3205-3208
                reno             3209-3212
                ntrpr            3213-3214
                nart             3215-3216
                hdt              3217-3218
                dto              3219-3220
                hns              3221-3222
                nso              3223-3224
                format           3225-3226

                fold             3227-3228
                tsort            3229-3230
                vscode           3231-3232
                hsfs             3233-3234
                hsfe             3235-3236
                hslen            3237-3238
                hstyp            3239-3240
                schn             3241-3242
                hstas            3243-3244
                hstae            3245-3246

                htatyp           3247-3248
                hcorr            3249-3250
                bgrcv            3251-3252
                rcvm             3253-3254
                mfeet            3255-3256
                polyt            3257-3258
                vpol             3259-3260

                rev              3501-3502
                fixl             3503-3504
                extfh            3505-3506
        
        th: Dictionnary containing traces header data
                keys are (unless custom dictionary given to read_segy)
                
                            (bytes in header)
                tracl      -  1-4
                tracr      -  5-8
                fldr       -  9-12
                tracf      -  13-16
                ep         -  17-20
                cdp        -  21-24
                cdpt       -  25-28
                trid       -  29-30
                nvs        -  31-32
                nhs        -  33-34

                duse       -  35-36
                offset     -  37-40
                gelev      -  41-44
                selev      -  45-48
                sdepth     -  49-52
                gdel       -  53-56
                sdel       -  57-60
                swdep      -  61-64
                gwdep      -  65-68
                scalel     -  69-70

                scalco     -  71-72
                sx         -  73-76
                sy         -  77-80
                gx         -  81-84
                gy         -  85-88
                counit     -  89-90
                wevel      -  91-92
                swevel     -  93-94
                sut        -  95-96
                gut        -  97-98

                sstat      -  99-100
                gstat      -  101-102
                tstat      -  103-104
                laga       -  105-106
                lagb       -  107-108
                delrt      -  109-110
                muts       -  111-112
                mute       -  113-114
                ns         -  115-116
                dt         -  117-118

                gain       -  119-120
                igc        -  121-122
                igi        -  123-124
                corr       -  125-126
                sfs        -  127-128
                sfe        -  129-130
                slen       -  131-132
                styp       -  133-134
                stas       -  135-136
                stae       -  137-138

                tatyp      -  139-140
                afilf      -  141-142
                afils      -  143-144
                nofilf     -  145-146
                nofils     -  147-148
                lcf        -  149-150
                hcf        -  151-152
                lcs        -  153-154
                hcs        -  155-156
                year       -  157-158

                day        -  159-160
                hour       -  161-162
                minute     -  163-164
                sec        -  165-166
                timbas     -  167-168
                trwf       -  169-170
                grnors     -  171-172
                grnofr     -  173-174
                grnlof     -  175-176
                gaps       -  177-178

                otrav      -  179-180
                xcdp       -  181-184
                ycdp       -  185-188
                ilineno    -  189-192
                clineno    -  193-196
                shotno     -  197-200
                scalsn     -  201-202
                tvmunit    -  203-204
                tdcst      -  205-210
                tdunit     -  211-212

                trid       -  213-214
                scalt      -  215-216
                styp       -  217-218
                sdir       -  219-224
                smeas      -  225-230
                smunit     -  231-232
                unass      -  233-240

        data: the actual traces (numpy array of size nsamples x ntraces)
                
    """
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
