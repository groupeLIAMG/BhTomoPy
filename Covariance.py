# -*- coding: utf-8 -*-

"""
Created on Tue Jun 21 20:55:29 2016

@author: giroux

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

class Covariance:
    """
    Base class for Covariance models
    """
    def __init__(self, r, a, s):
        self.range = r
        self.angle = a
        self.sill = s
        self.type = '' # To be defined by CovarianceModels

    def trans(self, cx):
        d = cx.ndim
        if d==2:
            d=cx.shape[1]
            
        if d != self.range.size:
            raise ValueError('Dimensionality of input data inconsistent')
        
        if d>1:
            if d==2:
                cang = np.cos(self.angle[0]/180*np.pi)
                sang = np.sin(self.angle[0]/180*np.pi)
                rot = np.array([[cang,-sang],[sang,cang]])
            else:
                cangz = np.cos(self.angle[2]/180*np.pi)
                sangz = np.sin(self.angle[2]/180*np.pi)
                cangy = np.cos(self.angle[1]/180*np.pi)
                sangy = np.sin(self.angle[1]/180*np.pi)
                cangx = np.cos(self.angle[0]/180*np.pi)
                sangx = np.sin(self.angle[0]/180*np.pi)
                rotz = np.array([[cangz,-sangz,0],[sangz,cangz,0],[0,0,1]])
                roty = np.array([[cangy,0,sangy],[0,1,0],[-sangy,0,cangy]])
                rotx = np.array([[1,0,0],[0,cangx,-sangx],[0,sangx,cangx]])
                rot = np.dot(np.dot(rotz,roty),rotx) 
                
            cx = np.dot(cx,rot)
            t = np.tile(self.range,(cx.shape[0],1))
        else:
#            rot = np.array([])
            t = self.range
            
        cx = cx/t
        return cx#,rot
        
    def compute_h(self, x, x0):
        n1,d = x.shape
        n2,d2 = x0.shape
        if d != d2:
            raise ValueError('Dimensionality of input data inconsistent')
            
        t1 = self.trans(x)
        t2 = self.trans(x0)
        h = 0
        for id in np.arange(d):
            tmp1 = np.tile(t1[:,id],(n2,1)).T
            tmp2 = np.tile(t2[:,id],(n1,1))
            h = h+(tmp1 - tmp2)**2
            
        return np.sqrt(h)
        
        
if __name__ == '__main__':
    
    cm = Covariance(np.array([10.0,3.0]), np.array([30]), np.array([2.5]))
    
    x=np.array([[0.0,0.0],
                [0.0,1.0],
                [0.0,10.0],
                [0.0,20.0],
                [0.0,25.0]])
                
    h = cm.compute_h(x,x)
    
    cm = Covariance(np.array([10.0,3.0,5.0]), np.array([30,15,10.0]), np.array([2.5]))
    
    x=np.array([[0.0,0.0,0.0],
                [0.0,1.0,5.0],
                [0.0,10.0,4.0],
                [0.0,20.0,8.0],
                [0.0,25.0,3.0]])
                
    h2 = cm.compute_h(x,x)