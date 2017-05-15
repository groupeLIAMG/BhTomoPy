
#include <inttypes.h>
#include <stdio.h>

#include "csegy.h"


/* returns true if on big endian, else false */
int IsBigEndian() { // grabed at http://unixpapa.com/incnote/byteorder.html
    long one = 1;
    return !(*((char *)(&one)));
}

void Swap2Bytes(int16_t *x) {
    *x=(((*x>>8)&0xff) | ((*x&0xff)<<8));
}

void Swap4Bytes(int32_t *x) {
    *x=(((*x>>24)&0xff) | ((*x&0xff)<<24) | ((*x>>8)&0xff00) | ((*x&0xff00)<<8));
}

void SwapFloat(float *x) {
    int32_t *y = (int32_t *)x;
    *y=(((*y>>24)&0xff) | ((*y&0xff)<<24) | ((*y>>8)&0xff00) | ((*y&0xff00)<<8));
}

void ibm2float(int32_t from[], int32_t to[], size_t n, int endian) {
    /***********************************************************************
     * ibm2float - convert between 32 bit IBM and IEEE floating numbers
     ************************************************************************
     * Input:
     * from     input vector
     * to       output vector, can be same as input vector
     * endian   byte order =0 little endian (DEC, PC's)
     * =1 other systems
     *************************************************************************
     * Notes:
     * Up to 3 bits lost on IEEE -> IBM
     *
     * IBM -> IEEE may overflow or underflow, taken care of by
     * substituting large number or zero
     *
     * Only integer shifting and masking are used.
     *************************************************************************
     * Credits: CWP: Brian Sumner,  c.1985
     *************************************************************************/
    register int32_t fconv, fmant, t;
    register size_t i;

    for (i = 0;i < n; ++i) {

        fconv = from[i];

        /* if little endian, i.e. endian=0 do this */
        if (endian == 0) fconv = (fconv << 24) | ((fconv >> 24) & 0xff) |
                ((fconv & 0xff00) << 8) | ((fconv & 0xff0000) >> 8);

        if (fconv) {
            fmant = 0x00ffffff & fconv;
            /* The next two lines were added by Toralf Foerster */
            /* to trap non-IBM format data i.e. conv=0 data  */
            if (fmant == 0)
                printf("mantissa is zero data may not be in IBM FLOAT Format !");
            t = (int32_t) ((0x7f000000 & fconv) >> 22) - 130;
            while (!(fmant & 0x00800000)) { --t; fmant <<= 1; }
            if (t > 254) fconv = (0x80000000 & fconv) | 0x7f7fffff;
            else if (t <= 0) fconv = 0;
            else fconv =   (0x80000000 & fconv) | (t << 23)
            | (0x007fffff & fmant);
        }
        to[i] = fconv;
    }
    return;
}

void int32_t2float(int32_t from[], float to[], size_t n, int endian)
/****************************************************************************
Author:	J.W. de Bruijn, May 1995
****************************************************************************/
{
	register size_t i;

    if (endian == 0) {
        for (i = 0; i < n; ++i) {
            Swap4Bytes(&from[i]);
            to[i] = (float) from[i];
        }
    } else {
        for (i = 0; i < n; ++i) {
            to[i] = (float) from[i];
        }
    }
    return;
}

void int16_t2float(int16_t from[], float to[], size_t n, int endian)
/****************************************************************************
short_to_float - type conversion for additional SEG-Y formats
*****************************************************************************
Author: Delft: J.W. de Bruijn, May 1995
Modified by: Baltic Sea Reasearch Institute: Toralf Foerster, March 1997
****************************************************************************/
{
	register int i;

	if (endian == 0) {
		for (i = n - 1; i >= 0 ; --i) {
			Swap2Bytes(&from[i]);
			to[i] = (float) from[i];
		}
	} else {
		for (i = n - 1; i >= 0 ; --i)
			to[i] = (float) from[i];
	}
    return;
}

 void integer1_to_float(signed char from[], float to[], int n)
/****************************************************************************
integer1_to_float - type conversion for additional SEG-Y formats
*****************************************************************************
Author: John Stockwell,  2005
****************************************************************************/
{
  	while (n--) {
		to[n] = from[n];
	}
}

int read_segy_b_header(const char* filename, PyObject* bh) {

    const char *fnames[] = {  // follows CWP/SU naming convention for bytes 3201-3260
    "jobid",  // int
    "lino",   // int
    "reno",   // int
    "ntrpr",  // short
    "nart",   // short
    "hdt",    // unsigned short
    "dto",    // unsigned short
    "hns",    // unsigned short
    "nso",    // unsigned short
    "format", // short

    "fold",   // short
    "tsort",  // short
    "vscode", // short
    "hsfs",   // short
    "hsfe",   // short
    "hslen",  // short
    "hstyp",  // short
    "schn",   // short
    "hstas",  // short
    "hstae",  // short

    "htatyp", // short
    "hcorr",  // short
    "bgrcv",  // short
    "rcvm",   // short
    "mfeet",  // short
    "polyt",  // short
    "vpol",   // short

    // bytes after 3500
    "rev",    // unsigned short
    "fixl",   // short
    "extfh",  // short
    };

    const short word_length[] = {
        4, 4, 4, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2
    };

    const short signed_word[] = {
        1, 1, 1, 1, 1, 0, 0, 0, 0, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 0, 1, 1
    };

    FILE *fid;

    //  open file
    fid = fopen(filename, "r");

    if ( fid==NULL ) {
        return 1;
    }

    if ( !PyDict_Check(bh) ) {
        return 2;
    }
    PyDict_Clear(bh);

    int bt = IsBigEndian();

    int16_t *stmp = (int16_t *)malloc(sizeof(int16_t));
    int32_t *itmp = (int32_t *)malloc(sizeof(int32_t));
    double *dtmp = (double *)malloc(sizeof(double));

    long offset = 3200L;
    long val;
    for ( size_t nf=0; nf<27; ++nf ) {

        if ( fseek(fid, offset, SEEK_SET) == -1 ) {
            fclose(fid);
            return 2;
        }

        switch ( word_length[ nf ] ) {
            case 2:
                fread(stmp, 2, 1, fid);
                if ( bt == 0 ) {
                    Swap2Bytes( stmp );
                }
                if ( signed_word[nf] ) {
                    val = *stmp;
                } else {
                    uint16_t utmp;
                    memcpy(&utmp, stmp, 2);
                    val = utmp;
                }
                if ( PyDict_SetItemString(bh, fnames[nf], PyLong_FromLong(val))==-1 )
                    return 2;
                break;
            case 4:
                fread(itmp, 4, 1, fid);
                if ( bt == 0 ) {
                    Swap4Bytes( itmp );
                }
                if ( signed_word[nf] ) {
                    val = *itmp;
                } else {
                    uint32_t utmp;
                    memcpy(&utmp, itmp, 4);
                    val = utmp;
                }
                if ( PyDict_SetItemString(bh, fnames[nf], PyLong_FromLong(val))==-1 )
                    return 2;
                break;
            default:
                return 2; //This should never happen!
        }

        offset += word_length[nf];
    }

    // get SEG Y Format revision number

    if ( fseek(fid, 3500L, SEEK_SET) == -1 ) {
        fclose(fid);
        return 2;
    }
    fread(stmp, 2, 1, fid);
    if ( bt == 0 ) {
        Swap2Bytes( stmp );
    }
    uint16_t utmp;
    memcpy(&utmp, stmp, 2);
    val = utmp;
    if ( PyDict_SetItemString(bh, fnames[27], PyLong_FromLong(val))==-1 )
        return 2;

    // get Fixed length trace flag

    if ( fseek(fid, 3502L, SEEK_SET) == -1 ) {
        fclose(fid);
        return 2;
    }

    fread(stmp, 2, 1, fid);
    if ( bt == 0 ) {
        Swap2Bytes( stmp );
    }
    val = *stmp;
    if ( PyDict_SetItemString(bh, fnames[28], PyLong_FromLong(val))==-1 )
        return 2;

    // get Number of 3200-byte, Extended Textual File Header records

    if ( fseek(fid, 3504L, SEEK_SET) == -1 ) {
        fclose(fid);
        return 2;
    }

    fread(stmp, 2, 1, fid);
    if ( bt == 0 ) {
        Swap2Bytes( stmp );
    }
    val = *stmp;
    if ( PyDict_SetItemString(bh, fnames[29], PyLong_FromLong(val))==-1 )
        return 2;

    fclose(fid);


    free(stmp);
    free(itmp);
    free(dtmp);
    return 0;
}


int read_segy_tr_headers(const char* filename,
                         PyObject* traceNo,
                         PyObject* fields,
                         PyObject* thDict,
                         PyObject* wordLength,
                         PyObject* th) {

    const char *fnames_seg[] = {  // follows CWP/SU naming convention for bytes 1-180
        "tracl",  // 1
        "tracr",
        "fldr",
        "tracf",
        "ep",
        "cdp",
        "cdpt",
        "trid",
        "nvs",
        "nhs",

        "duse",  // 11
        "offset",
        "gelev",
        "selev",
        "sdepth",
        "gdel",
        "sdel",
        "swdep",
        "gwdep",
        "scalel",

        "scalco",  // 21
        "sx",
        "sy",
        "gx",
        "gy",
        "counit",
        "wevel",
        "swevel",
        "sut",
        "gut",

        "sstat", // 31
        "gstat",
        "tstat",
        "laga",
        "lagb",
        "delrt",
        "muts",
        "mute",
        "ns",
        "dt",

        "gain",  // 41
        "igc",
        "igi",
        "corr",
        "sfs",
        "sfe",
        "slen",
        "styp",
        "stas",
        "stae",

        "tatyp",  // 51
        "afilf",
        "afils",
        "nofilf",
        "nofils",
        "lcf",
        "hcf",
        "lcs",
        "hcs",
        "year",

        "day",  // 61
        "hour",
        "minute",
        "sec",
        "timbas",
        "trwf",
        "grnors",
        "grnofr",
        "grnlof",
        "gaps",

        "otrav",  // 71

        //  names below arbitrarily given
        "xcdp",   // 72 - X coord of ensemble (CDP) position of this trace
        "ycdp",   // 73 - Y coord of ensemble (CDP) position of this trace
        "ilineno",
        "clineno",
        "shotno",   // 76 - shotpoint number
        "scalsn",
        "tvmunit",   // 78 - trace value measurement units
        "tdcst",
        "tdunit",

        "trid",   // 81 - device/trace identifier
        "scalt",
        "styp",   // 83 - source type/orientation
        "sdir",
        "smeas",
        "smunit"   // 86 - source measurement units
    };
    const short NFIELDS_SEG = 86;
    char **fnames;

    const short word_length_seg[] = {
        4, 4, 4, 4, 4, 4, 4, 2, 2, 2,
        2, 4, 4, 4, 4, 4, 4, 4, 4, 2,
        2, 4, 4, 4, 4, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 4, 4, 4, 4, 4, 2, 2, 6, 2,
        2, 2, 2, 6, 6, 2
    };
    short *word_length;

    FILE *fid;

    int bt = IsBigEndian();

    //  open file
    fid = fopen(filename, "r");

    if ( fid==NULL ) {
        return 1;
    }

    // make sure th is a dict
    if ( !PyDict_Check(th) ) {
        return 2;
    }
    PyDict_Clear(th);

    int16_t *stmp = (int16_t *)malloc(sizeof(int16_t));
    int32_t *itmp = (int32_t *)malloc(sizeof(int32_t));
    double *dtmp = (double *)malloc(sizeof(double));
    float *ftmp = (float *)malloc(sizeof(float));


    // read in some info
    // read in number of samples per data trace
    if ( fseek(fid, 3220, SEEK_SET)  == -1 ) {
        fclose(fid);
        free(stmp);
        free(itmp);
        free(dtmp);
        free(ftmp);
        return 2;
    }

    fread(stmp, 2, 1, fid);
    if ( bt == 0 ) {
        // we have read a big endian word, we're on a little endian machine
        Swap2Bytes( stmp );
    }
    int nsamples = *stmp;

    // read in data sample format code
    if ( fseek(fid, 3224, SEEK_SET)  == -1 ) {
        fclose(fid);
        free(stmp);
        free(itmp);
        free(dtmp);
        free(ftmp);
        return 2;
    }
    fread(stmp, 2, 1, fid);
    if ( bt == 0 ) {
        // we have read a big endian word, we're on a little endian machine
        Swap2Bytes( stmp );
    }
    int bytesPerSample;
    switch( *stmp ) {
        case 1:
        case 2:
        case 5:
            bytesPerSample = 4;
            break;
        case 3:
            bytesPerSample = 2;
            break;
        case 8:
            bytesPerSample = 1;
            break;
        default:
            return 2;
    }

    // get Number of 3200-byte, Extended Textual File Header records
    if ( fseek(fid, 3502, SEEK_SET) == -1 ) {
        fclose(fid);
        free(stmp);
        free(itmp);
        free(dtmp);
        free(ftmp);
        return 2;
    }
    fread(stmp, 2, 1, fid);
    if ( bt == 0 ) {
        Swap2Bytes( stmp );
    }
    int nextended = *stmp;


    // make sure traceNo is a list
    if ( PyList_Check(traceNo) == 0 ) {
        free(stmp);
        free(itmp);
        free(dtmp);
        free(ftmp);
        return 2;
    }
    int32_t* traces_no;
    Py_ssize_t ntraces = PyList_Size(traceNo);
    if ( ntraces != 0 ) {
        traces_no = (int32_t*)malloc(ntraces*sizeof(int32_t));

        for ( Py_ssize_t n=0; n<ntraces; ++n) {
            PyObject* tn = PyList_GetItem(traceNo, n);
            if ( PyLong_Check(tn)==0 ) {
                free(stmp);
                free(itmp);
                free(dtmp);
                free(ftmp);
                return 2;
            }
            traces_no[n] = (int32_t)PyLong_AsLong(tn);
        }
    } else {
        // we must read for all traces

        fseek(fid, 0L, SEEK_END);
        long filesize = ftell(fid);
        fseek(fid, 0L, SEEK_SET);

        filesize -= 3600L + nextended*3200L;
        ntraces = filesize / ( 240 + bytesPerSample*nsamples );
        traces_no = (int32_t*)malloc(ntraces*sizeof(int32_t));
        for (int32_t n=0; n<ntraces; ++n)
            traces_no[n] = n;
    }

    if ( PyList_Check(thDict) == 0 || PyList_Check(wordLength) == 0 ) {
        free(stmp);
        free(itmp);
        free(dtmp);
        free(ftmp);
        return 2;
    }

    // check if user gave a dict
    Py_ssize_t NFIELDS = PyList_Size(thDict);
    if ( NFIELDS != 0 ) {
        Py_ssize_t nwordLength = PyList_Size(wordLength);

        if ( NFIELDS != nwordLength ) {
            free(stmp);
            free(itmp);
            free(dtmp);
            free(ftmp);
            return 2;
        }

        fnames = (char **)malloc(sizeof(char*)*NFIELDS);
        word_length = (short *)malloc(sizeof(short)*NFIELDS);

        for ( Py_ssize_t n=0; n<NFIELDS; ++n) {
            PyObject* tn = PyList_GetItem(thDict, n);
            if ( PyUnicode_Check(tn)==0 ) {
                free(stmp);
                free(itmp);
                free(dtmp);
                free(ftmp);
                return 2;
            }
            if ( PyUnicode_KIND(tn) != PyUnicode_1BYTE_KIND ) {
                free(stmp);
                free(itmp);
                free(dtmp);
                free(ftmp);
                return 2;
            }
            fnames[n] = (char *)malloc(sizeof(char)*(1+strlen(PyUnicode_1BYTE_DATA(tn))));
            strcpy(fnames[n], PyUnicode_1BYTE_DATA(tn));

            tn = PyList_GetItem(wordLength, n);
            if ( PyLong_Check(tn)==0 ) {
                free(stmp);
                free(itmp);
                free(dtmp);
                free(ftmp);
                return 2;
            }
            word_length[n] = (short)PyLong_AsLong(tn);
        }

    } else {
        // we use the "standard" dict
        NFIELDS = NFIELDS_SEG;
        fnames = (char **)malloc(sizeof(char*)*NFIELDS);
        word_length = (short *)malloc(sizeof(short)*NFIELDS);
        for ( Py_ssize_t n = 0; n<NFIELDS; ++n ) {
            fnames[n] = (char *)malloc(sizeof(char)*(1+strlen(fnames_seg[n])));
            strcpy(fnames[n], fnames_seg[n]);
            word_length[n] = word_length_seg[n];
        }
    }

    if ( PyList_Check(fields) == 0 ) {
        free(stmp);
        free(itmp);
        free(dtmp);
        free(ftmp);
        return 2;
    }

    // fields to read
    Py_ssize_t nfields = PyList_Size(fields);
    int16_t* fields_no=NULL;
    if ( nfields==1 ) {
        PyObject* tn = PyList_GetItem(fields, 0);

        if ( PyUnicode_Check(tn) != 0 ) {
            if ( PyUnicode_CompareWithASCIIString(tn, "ALL")==0 ) {
                nfields = NFIELDS;
                fields_no = (int16_t*)malloc(nfields*sizeof(int16_t));
                for ( int16_t n=0; n<nfields; ++n )
                    fields_no[n] = n;

            } else {
                fields_no = (int16_t*)malloc(sizeof(int16_t));
                int found = 0;
                for ( Py_ssize_t n = 0; n<NFIELDS; ++n ) {
                    if ( strcmp(PyUnicode_1BYTE_DATA(tn), fnames[n])==0 ) {
                        fields_no[0] = n;
                        found = 1;
                        break;
                    }
                }
                if ( found==0 ) {
                    free(fields_no);
                    free(stmp);
                    free(itmp);
                    free(dtmp);
                    free(ftmp);
                    return 2;
                }
            }
        } else if ( PyLong_Check(tn)!=0 ) {
            if ( PyLong_AsLong(tn)<NFIELDS && PyLong_AsLong(tn)>=0 ) {
                nfields = 1;
                fields_no = (int16_t*)malloc(nfields*sizeof(int16_t));
                fields_no[0] = (int16_t)PyLong_AsLong(tn);
            } else {
                free(stmp);
                free(itmp);
                free(dtmp);
                free(ftmp);
                return 2;
            }
        } else {
            free(stmp);
            free(itmp);
            free(dtmp);
            free(ftmp);
            return 2;
        }

    } else {
        fields_no = (int16_t*)malloc(nfields*sizeof(int16_t));
        for ( Py_ssize_t n = 0; n<nfields; ++n ) {
            PyObject* tn = PyList_GetItem(fields, n);

            if ( PyUnicode_KIND(tn) != PyUnicode_1BYTE_KIND ) {
                return 2;
            }

            int found = 0;
            for ( Py_ssize_t nn = 0; nn<NFIELDS; ++nn ) {
                if ( strcmp(PyUnicode_1BYTE_DATA(tn), fnames[nn])==0 ) {
                    fields_no[n] = nn;
                    found = 1;
                    break;
                }
            }
            if ( found==0 ) {
                free(fields_no);
                free(stmp);
                free(itmp);
                free(dtmp);
                free(ftmp);
                return 2;
            }
        }
    }

    // create arrays to hold the data

    import_array();  // to use PyArray_SimpleNewFromData

    void** thData = (void**)malloc(nfields*sizeof(void*));
    PyObject** thPyData = (PyObject**)malloc(nfields*sizeof(PyObject*));
    npy_intp dims[] = {(npy_intp)ntraces};
    for ( Py_ssize_t nf=0; nf<nfields; ++nf ) {
        switch ( word_length[ fields_no[nf] ] ) {
            case 2:
                thData[nf] = (int16_t*)malloc(ntraces*sizeof(int16_t));
                thPyData[nf] = PyArray_SimpleNewFromData(1, dims, NPY_INT16, thData[nf]);
                PyArray_ENABLEFLAGS((PyArrayObject*)thPyData[nf], NPY_ARRAY_OWNDATA);
                break;
            case 4:
                thData[nf] = (int32_t*)malloc(ntraces*sizeof(int32_t));
                thPyData[nf] = PyArray_SimpleNewFromData(1, dims, NPY_INT32, thData[nf]);
                PyArray_ENABLEFLAGS((PyArrayObject*)thPyData[nf], NPY_ARRAY_OWNDATA);
                break;
            case 5:
                thData[nf] = (float*)malloc(ntraces*sizeof(float));
                thPyData[nf] = PyArray_SimpleNewFromData(1, dims, NPY_FLOAT32, thData[nf]);
                PyArray_ENABLEFLAGS((PyArrayObject*)thPyData[nf], NPY_ARRAY_OWNDATA);
                break;
            case 6:
                thData[nf] = (double*)malloc(ntraces*sizeof(double));
                thPyData[nf] = PyArray_SimpleNewFromData(1, dims, NPY_FLOAT64, thData[nf]);
                PyArray_ENABLEFLAGS((PyArrayObject*)thPyData[nf], NPY_ARRAY_OWNDATA);
                break;
            default:
                return 2;
        }
        if ( PyDict_SetItemString(th, fnames[fields_no[nf]], thPyData[nf])==-1 )
            return 2;
    }

    long offset, offset2, ioff;
    for ( size_t n=0; n<ntraces; ++n ) {

        offset = 3600L + nextended*3200 + (traces_no[n]*(240+(bytesPerSample*nsamples)));

        for ( size_t nf=0; nf<nfields; ++nf ) {

            offset2 = offset;
            for (size_t m=0; m<fields_no[nf]; ++m) {
                ioff = word_length[m]==5 ? 4 : word_length[m];  // we use 5 for 4-byte ibm float
                offset2 += ioff;
            }

            if ( fseek(fid, offset2, SEEK_SET) == -1 ) {
                fclose(fid);
                free(fields_no);
                free(stmp);
                free(itmp);
                free(dtmp);
                free(ftmp);
                return 2;
            }

            switch ( word_length[ fields_no[nf] ] ) {
                case 2:
                    fread(stmp, 2, 1, fid);

                    if ( bt == 0 ) {
                        Swap2Bytes( stmp );
                    }

                    memcpy(((int16_t*)thData[nf])+n, stmp, 2);

                    break;
                case 4:
                    fread(itmp, 4, 1, fid);

                    if ( bt == 0 ) {
                        Swap4Bytes( itmp );
                    }

                    memcpy(((int32_t *)thData[nf])+n, itmp, 4);

                    break;
                case 5:
                    fread(itmp, 4, 1, fid);
                    ibm2float(itmp, (int32_t *)ftmp, 1, bt);

                    memcpy(((float *)thData[nf])+n, ftmp, sizeof(float));

                    break;
                case 6:
                    fread(itmp, 4, 1, fid);
                    fread(stmp, 2, 1, fid);

                    if ( bt == 0 ) {
                        Swap4Bytes( itmp );
                        Swap2Bytes( stmp );
                    }

                    *dtmp = *itmp * pow( 10.0, *stmp );

                    memcpy(((double *)thData[nf])+n, dtmp, sizeof(double));

                    break;
                default:
                    fclose(fid);
                    free(fields_no);
                    free(stmp);
                    free(itmp);
                    free(dtmp);
                    free(ftmp);
                    return 2;
            }
        }
    }

    fclose(fid);

    free(fields_no);
    free(stmp);
    free(itmp);
    free(dtmp);
    free(ftmp);
    return 0;
}


PyObject* read_segy_data(const char* filename, PyObject* traceNo) {

    FILE *fid;

    //  open file
    fid = fopen(filename, "r");

    if ( fid==NULL ) {
        return PyLong_FromLong(1);
    }

    int bt = IsBigEndian();

    int16_t *stmp = (int16_t *)malloc(sizeof(int16_t));
    int32_t *itmp = (int32_t *)malloc(sizeof(int32_t));

    // read in some info
    // read in number of samples per data trace
    if ( fseek(fid, 3220, SEEK_SET)  == -1 ) {
        fclose(fid);
        free(stmp);
        free(itmp);
        return PyLong_FromLong(2);
    }

    fread(stmp, 2, 1, fid);
    if ( bt == 0 ) {
        // we have read a big endian word, we're on a little endian machine
        Swap2Bytes( stmp );
    }
    int nsamples = *stmp;

    // read in data sample format code
    if ( fseek(fid, 3224, SEEK_SET)  == -1 ) {
        fclose(fid);
        free(stmp);
        free(itmp);
        return PyLong_FromLong(2);
    }
    fread(stmp, 2, 1, fid);
    if ( bt == 0 ) {
        Swap2Bytes( stmp );
    }
    short format = *stmp;
    int bytesPerSample;
    switch( format ) {
        case 1:
        case 2:
        case 5:
            bytesPerSample = 4;
            break;
        case 3:
            bytesPerSample = 2;
            break;
        case 8:
            bytesPerSample = 1;
            break;
        default:
            return PyLong_FromLong(2);
    }

    // get Number of 3200-byte, Extended Textual File Header records
    if ( fseek(fid, 3502, SEEK_SET) == -1 ) {
        fclose(fid);
        free(stmp);
        free(itmp);
        return PyLong_FromLong(2);
    }
    fread(stmp, 2, 1, fid);
    if ( bt == 0 ) {
        Swap2Bytes( stmp );
    }
    int nextended = *stmp;


    // make sure traceNo is a list
    if ( PyList_Check(traceNo) == 0 ) {
        fclose(fid);
        free(stmp);
        free(itmp);
        return PyLong_FromLong(2);
    }
    int32_t* traces_no;
    Py_ssize_t ntraces = PyList_Size(traceNo);
    if ( ntraces != 0 ) {
        traces_no = (int32_t*)malloc(ntraces*sizeof(int32_t));

        for ( Py_ssize_t n=0; n<ntraces; ++n) {
            PyObject* tn = PyList_GetItem(traceNo, n);
            if ( PyLong_Check(tn)==0 ) {
                free(stmp);
                free(itmp);
                return PyLong_FromLong(2);
            }
            traces_no[n] = (int32_t)PyLong_AsLong(tn);
        }
    } else {
        // we must read for all traces

        fseek(fid, 0L, SEEK_END);
        long filesize = ftell(fid);
        fseek(fid, 0L, SEEK_SET);

        filesize -= 3600L + nextended*3200L;
        ntraces = filesize / ( 240 + bytesPerSample*nsamples );
        traces_no = (int32_t*)malloc(ntraces*sizeof(int32_t));
        for (int32_t n=0; n<ntraces; ++n)
            traces_no[n] = n;
    }

    float* pdata = (float*)malloc(nsamples*ntraces*sizeof(float));
    npy_intp dims[] = {(npy_intp)ntraces,(npy_intp)nsamples};  // ntraces x nsamples due to memory layout
    PyObject* data = PyArray_SimpleNewFromData(2, dims, NPY_FLOAT, pdata);
    PyArray_ENABLEFLAGS((PyArrayObject*)data, NPY_ARRAY_OWNDATA);


    void *ptr;
    switch ( format ) {
        case 1:
        case 2:
            ptr = (int32_t *) malloc(nsamples*sizeof(int32_t));
            break;
        case 3:
            ptr = (int16_t *) malloc(nsamples*sizeof(int16_t));
            break;
        case 5:
            ptr = (float *) malloc(nsamples*sizeof(float));
            break;
        case 8:
            ptr = (char *) malloc(nsamples*sizeof(char));
            break;
        default:
            fclose(fid);
            free(stmp);
            free(itmp);
            return PyLong_FromLong(2);
    }

    float *fltptr;
    if ( format == 5 )
        fltptr = ptr;
    else
        fltptr = malloc(nsamples*sizeof(float));

    long offset;

    for ( size_t n=0; n<ntraces; ++n ) {

        offset = 3600L + nextended*3200 +
                (traces_no[n]*(240+(bytesPerSample*nsamples))) + 240L;

        if ( fseek(fid, offset, SEEK_SET) == -1 ) {
            fclose(fid);
            free(stmp);
            free(itmp);
            return PyLong_FromLong(2);
        }

        fread(ptr, bytesPerSample, nsamples, fid);

        switch ( format ) {
            case 1:
                ibm2float(ptr, (int32_t *)fltptr, nsamples, bt);
                break;
            case 2:
                int32_t2float((int32_t *)ptr, fltptr, nsamples, bt);
                break;
            case 3:
                int16_t2float((int16_t *)ptr, fltptr, nsamples, bt);
                break;
            case 5:
                if ( bt == 0 )
                    for ( size_t ns=0; ns<nsamples; ++ns )
                        SwapFloat(&fltptr[ns]);
                break;
            case 8:
                integer1_to_float((signed char *)ptr, fltptr, nsamples);
                break;
        }
        memcpy(pdata, fltptr, bytesPerSample*nsamples);
        pdata += nsamples;
    }


    fclose(fid);
    free(stmp);
    free(itmp);
    return PyArray_Transpose(data,NULL);  // we transpose to get an array of size nsamples x ntraces like in matlab
}
