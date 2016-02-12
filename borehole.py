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


class Borehole:
    
    def __init__(self, name=None):
        self.name = name
        self.X = [0, 0]
        self.Y = [0, 0]
        self.Z = [0, 0]
        self.Zsurf = 0
        self.Zwater = 0
        self.Diam = 0
        
        

        
if __name__ == '__main__':
    
    bh = Borehole('B01' )
    