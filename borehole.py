# -*- coding: utf-8 -*-
"""
Copyright 2016 Bernard Giroux
email: Bernard.Giroux@ete.inrs.ca

This file is part of BhTomoPy.

BhTomoPy is free software: you can redistribute it and/or modify
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

#---- STANDARD LIBRARY IMPORTS ----

import csv

class Borehole(object):
    
    def __init__(self, name=None):
        self.name = name
        self.X = [0, 0]
        self.Y = [0, 0]
        self.Z = [0, 0]
        self.Zsurf = 0
        self.Zwater = 0
        self.Diam = 0
        
class BoreholeSet(object):
    
    def __init__(self, name=None):
        self.bholes = []
        
    def add_bhole(self, name, X, Y, Z, Zsurf, Zwater, Diam):        
        bhole = Borehole(name)
        bhole.X, bhole.Y, bhole.Z = X, Y, Z
        bhole.Zsurf = Zsurf
        bhole.Zwater = Zwater
        bhole.Diam = Diam
        
        self.bholes.insert(0, bhole)
        print('Added bhole %s to the set of boreholes.' % name)
        
    def del_bhole(self, index):
        del self.bholes[index]
        
    def get_bhole(self, index):
        return self.bholes[index]
        
    def load_bholes(self, fname):
        print('Loading borehole set from: %s' % fname)
        self.bholes = []
         
        with open(fname, 'r') as f:
            reader = list(csv.reader(f, delimiter='\t'))
            
        for line in reader:
            self.add_bhole(line[0].decode('utf-8'),
                           [float(line[1]), float(line[2])],
                           [float(line[3]), float(line[4])],
                           [float(line[5]), float(line[6])],
                           float(line[7]),
                           float(line[8]),
                           float(line[9]))
        print('Borehole set loaded.')                  
        return self.bholes        
                           
    def save_bholes(self, fname):
        print('Saving borehole set in: %s...' % fname)
        fcontent = []
        for bhole in self.bholes:
            fcontent.append([bhole.name,
                             bhole.X[0], bhole.X[1],
                             bhole.Y[0], bhole.Y[1],
                             bhole.Z[0], bhole.Z[1],
                             bhole.Zsurf, bhole.Zwater, bhole.Diam])
                             
        with open(fname, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(fcontent)
        print('Borehole set saved.')
        
if __name__ == '__main__':
    
    bh = Borehole('B01' )
    