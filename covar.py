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

from enum import IntEnum

import numpy as np


class Covariance:
    """
    Base class for Covariance models
    """
    def __init__(self, r, a, s):
        self.range = r
        self.angle = a
        self.sill = s
        self.type = None # To be defined by CovarianceModels

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
        

class CovarianceCubic(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Cubic
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * (1.0-3.0*np.minimum(h,1)**2 + 2.0*np.minimum(h,1)**3)
        
class CovarianceExponential(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Exponential
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * np.exp(-h)
    
class CovarianceGaussian(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Gaussian
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * np.exp(-h**2)
        
class CovarianceGravimetric(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Gravimetric
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * (h**2 + 1)**-0.5

class CovarianceHoleEffectCosine(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Hole_Effect_Cosine
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * np.cos(2.0*np.pi*h)

class CovarianceHoleEffectSine(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Hole_Effect_Sine
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * np.sin(np.maximum(np.finfo(float).eps,2.0*np.pi*h))/np.maximum(np.finfo(float).eps,2.0*np.pi*h)

class CovarianceLinear(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Linear
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * (1.0-h)
        
class CovarianceMagnetic(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Magnetic
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * (h**2 + 1)**-1.5
    
class CovarianceNugget(Covariance):
    def __init__(self, s):
        Covariance.__init__(self,np.array([1.0, 1.0]), np.array([0.0]), s)
        self.type = CovarianceModels.Nugget
        
    def compute(self, x, x0):
        d = x.ndim
        if d==2:
            d=x.shape[1]
        self.range = np.ones((d,))
        if d==3:
            self.angle = np.zeros((3,))
        else:
            self.angle = np.array([0.0])
            
        h = self.compute_h(x, x0)
        return self.sill * (h==0)
        
class CovarianceSpherical(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Spherical
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * (1-(1.5*np.minimum(h,1) - 0.5*(np.minimum(h,1))**3))
        
class CovarianceThinPlate(Covariance):
    def __init__(self,r,a,s):
        Covariance.__init__(self,r,a,s)
        self.type = CovarianceModels.Thin_Plate
        
    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self.sill * h**2 * np.log(np.maximum(h,np.finfo(float).eps))
    


class CovarianceModels(IntEnum):
    Cubic = 0
    Spherical = 1
    Gaussian = 2
    Exponential = 3
    Linear = 4
    Thin_Plate = 5
    Gravimetric = 6
    Magnetic = 7
    Hole_Effect_Sine = 8
    Hole_Effect_Cosine = 9
    Nugget = 10
    
    @staticmethod
    def buildCov(type,r,a,s):
        if type==0:
            return CovarianceCubic(r,a,s)
        elif type==1:
            return CovarianceSpherical(r,a,s)
        elif type==2:
            return CovarianceGaussian(r,a,s)
        elif type==3:
            return CovarianceExponential(r,a,s)
        elif type==4:
            return CovarianceLinear(r,a,s)
        elif type==5:
            return CovarianceThinPlate(r,a,s)
        elif type==6:
            return CovarianceGravimetric(r,a,s)
        elif type==7:
            return CovarianceMagnetic(r,a,s)
        elif type==8:
            return CovarianceHoleEffectSine(r,a,s)
        elif type==9:
            return CovarianceHoleEffectCosine(r,a,s)
        elif type==10:
            return CovarianceNugget(s)
        else:
            raise ValueError('Undefined covariance model')
    
    @staticmethod
    def detDefault2D():
        return CovarianceSpherical(np.array([4.0,4.0]),np.array([0.0]), 1.0)

    @staticmethod
    def detDefault3D():
        return CovarianceSpherical(np.array([4.0,4.0,4.0]),np.array([0.0,0.0,0.0]), 1.0)


if __name__ == '__main__':
    
    x=np.array([[0.0,0.0],
                [0.0,1.0],
                [0.0,10.0],
                [0.0,20.0],
                [0.0,25.0]])
                
    cm = Covariance(np.array([10.0,3.0]), np.array([30]), 2.5)
    
    cm = CovarianceCubic(np.array([10.0,3.0]), np.array([30]), 2.5)
    
    h = cm.compute_h(x,x)
    k = cm.compute(x,x)

    cm = CovarianceExponential(np.array([10.0,3.0]), np.array([30]), 2.5)
    k2 = cm.compute(x,x)

    cm = CovarianceGaussian(np.array([10.0,3.0]), np.array([30]), 2.5)
    k3 = cm.compute(x,x)

    cm = CovarianceGravimetric(np.array([10.0,3.0]), np.array([30]), 2.5)
    k4 = cm.compute(x,x)

    cm = CovarianceHoleEffectCosine(np.array([10.0,3.0]), np.array([30]), 2.5)
    k5 = cm.compute(x,x)
    
    cm = CovarianceHoleEffectSine(np.array([10.0,3.0]), np.array([30]), 2.5)
    k6 = cm.compute(x,x)
    
    cm = CovarianceLinear(np.array([10.0,3.0]), np.array([30]), 2.5)
    k7 = cm.compute(x,x)

    cm = CovarianceMagnetic(np.array([10.0,3.0]), np.array([30]), 2.5)
    k8 = cm.compute(x,x)
    
    cm = CovarianceNugget(np.array([2.5]))
    k9 = cm.compute(x,x)
    
    cm = CovarianceSpherical(np.array([10.0,3.0]), np.array([30]), 2.5)
    k10 = cm.compute(x,x)

    cm = CovarianceModels.buildCov(5, np.array([10.0,3.0]), np.array([30]), 2.5)
    k11 = cm.compute(x,x)
    
    
    
    
    cm = Covariance(np.array([10.0,3.0,5.0]), np.array([30,15,10.0]), 2.5)
    
    x=np.array([[0.0,0.0,0.0],
                [0.0,1.0,5.0],
                [0.0,10.0,4.0],
                [0.0,20.0,8.0],
                [0.0,25.0,3.0]])
                
    h2 = cm.compute_h(x,np.zeros((1,3)))