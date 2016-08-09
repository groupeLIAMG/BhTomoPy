# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 12:54:52 2016

@author: giroux
"""

from cutils import segy

filename  = '/Users/giroux/CloudStation/Projets/Frio/donnees_brutes/pre-xwell-all.sgy'

d = segy.read_segy(filename, fields=['sx','sy','gx','gy','selev'])

for k in d.bh:
    print(k, d.bh[k] )

for k in d.th:
    print(k, d.th[k][1] )

print(d.data.shape)
print(d.data[:50,0])