# -*- coding: utf-8 -*-
"""
Copyright 2017 Bernard Giroux, Elie Dumas-Lefebvre, Jerome Simon
email: Bernard.Giroux@ete.inrs.ca

This file is part of BhTomoPy.

BhTomoPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import os
import numpy as np
import h5py

from borehole import Borehole
from covar import Covariance, CovarianceCubic, CovarianceExponential, CovarianceGaussian, CovarianceGravimetric # @UnusedImport
from covar import CovarianceHoleEffectCosine, CovarianceHoleEffectSine, CovarianceLinear, CovarianceMagnetic # @UnusedImport
from covar import CovarianceModel, CovarianceNugget, CovarianceSpherical, CovarianceThinPlate # @UnusedImport
from cutils import cgrid2d  # @UnresolvedImport
from grid import Grid2D, Grid3D # @UnusedImport
from inversion import InvLSQRParams, Tomo, invData # @UnusedImport
from mog import MogData, Mog, AirShots, PruneParams # @UnusedImport
from model import Model


class DbList(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.modified = False

    def append(self, item):
        for obj in self:
            if obj.name == item.name:
                raise ValueError('Two items cannot share the same name in a DbList')
        super(DbList, self).append(item)
        self.modified = True

    def remove(self, item):
        super(DbList, self).remove(item)
        self.modified = True

# TODO: map Mog.Tx, Mog.Rx, Mog.av, Mog.ap and Model.mogs to stored objects
class BhTomoDb():
    def __init__(self, fname=''):
        self.filename = fname
        self.air_shots = DbList()
        self.boreholes = DbList()
        self.mogs = DbList()
        self.models = DbList()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, fname):
        self._filename = fname
        if fname is not '':
            self.f = h5py.File(fname, 'a')
            
    @property
    def name(self):
        return os.path.basename(self._filename)
    
    @property
    def modified(self):
        modified = self.air_shots.modified or self.boreholes.modified or self.mogs.modified or self.models.modified
        for obj in self.boreholes, self.air_shots, self.mogs, self.models:
            modified = modified or obj.modified
        return modified
        

    def save(self, fname=None, obj=None):
        if fname is not None:
            self.filename = fname
            
        # if empty file, create 4 mains groups
        self.f.require_group('/boreholes')
        self.f.require_group('/mogs')
        self.f.require_group('/models')
        self.f.require_group('/air_shots')
            
        if obj is not None:
            # obj should be an instance of either a Borehole, Mog, Model or AirShot
            if type(obj) is Borehole:
                try:
                    ind = self.boreholes.index(obj)
                    group = self.f['/boreholes/'+str(ind)]
                except:
                    group = self.f.require_group('/boreholes'+str(len(self.boreholes)))
            elif type(obj) is Mog:
                try:
                    ind = self.mogs.index(obj)
                    group = self.f['/mogs/'+str(ind)]
                except:
                    group = self.f.require_group('/mogs'+str(len(self.mogs)))
            elif type(obj) is Model:
                try:
                    ind = self.models.index(obj)
                    group = self.f['/models/'+str(ind)]
                except:
                    group = self.f.require_group('/models'+str(len(self.models)))
            elif type(obj) is AirShots:
                try:
                    ind = self.air_shots.index(obj)
                    group = self.f['/air_shots/'+str(ind)]
                except:
                    group = self.f.require_group('/air_shots'+str(len(self.air_shots)))
            else:
                raise TypeError
            
            self._saveObject(obj, group)
            self.f.flush()
            
        else:
            # save everything
            if self.boreholes.modified:
                g = self.f.require_group('/boreholes')
                self._saveList(self.boreholes, g)

            if self.mogs.modified:
                g = self.f.require_group('/mogs')
                self._saveList(self.mogs, g)

            if self.models.modified:
                g = self.f.require_group('/air_shots')
                self._saveList(self.air_shots, g)

            if self.air_shots.modified:
                g = self.f.require_group('/models')
                self._saveList(self.models, g)
            
            self.f.flush()
            self.boreholes.modified = False
            self.mogs.modified = False
            self.models.modified = False
            self.air_shots.modified = False
            
    def load(self, fname=None):
        if fname is not None:
            self.filename = fname
        
        self.load_boreholes()
        self.load_mogs()
        self.load_models()
        self.load_air_shots()
        
    def load_boreholes(self):
        self.boreholes = DbList()
        gr = self.f['/boreholes']
        for k in gr.keys():
            b = Borehole(gr[k].attrs['name'])
            for kk in gr[k].attrs.keys():
                b.__dict__[kk] = gr[k].attrs[kk]
            for kk in gr[k].keys():
                b.__dict__[kk] = gr[k][kk]
            self.boreholes.append(b)

    def load_mogs(self):
        self.mogs = DbList()
        gr = self.f['/mogs']
        for k in gr.keys():
            m = Mog()
            for kk in gr[k].attrs.keys():
                m.__dict__[kk] = gr[k].attrs[kk]
            for kk in gr[k].keys():
                if type(gr[k][kk]) is h5py._hl.dataset.Dataset:  # @UndefinedVariable
                    m.__dict__[kk] = gr[k][kk]
                elif type(gr[k][kk]) is h5py._hl.group.Group:  # @UndefinedVariable
                    gr2 = gr[k][kk]
                    if '_list_' in gr2.name:
                        m.__dict__[kk] = self._loadList(gr2)
                    else:
                        m.__dict__[kk] = self._loadObject(gr2)
            
            self.mogs.append(m)
            
    def get_mog(self, index):
        group = self.f['/mogs/'+str(index)]
        return self._loadObject(group)

    def load_models(self):
        self.models = DbList()
        gr = self.f['/models']
        for k in gr.keys():
            m = Model()
            for kk in gr[k].attrs.keys():
                m.__dict__[kk] = gr[k].attrs[kk]
            for kk in gr[k].keys():
                if type(gr[k][kk]) is h5py._hl.dataset.Dataset:  # @UndefinedVariable
                    m.__dict__[kk] = gr[k][kk]
                elif type(gr[k][kk]) is h5py._hl.group.Group:  # @UndefinedVariable
                    # we have either a list or a custom class
                    gr2 = gr[k][kk]
                    if '_list_' in gr2.name:
                        m.__dict__[kk] = self._loadList(gr2)
                    else:
                        m.__dict__[kk] = self._loadObject(gr2)
            
            self.models.append(m)
            
    def get_model(self, index):
        group = self.f['/model/'+str(index)]
        return self._loadObject(group)

    def load_air_shots(self):
        self.air_shots = DbList()
        gr = self.f['/air_shots']
        for k in gr.keys():
            m = AirShots()
            for kk in gr[k].attrs.keys():
                m.__dict__[kk] = gr[k].attrs[kk]
            for kk in gr[k].keys():
                if type(gr[k][kk]) is h5py._hl.dataset.Dataset:  # @UndefinedVariable
                    m.__dict__[kk] = gr[k][kk]
                elif type(gr[k][kk]) is h5py._hl.group.Group:  # @UndefinedVariable
                    # we have either a list or a custom class
                    gr2 = gr[k][kk]
                    if '_list_' in gr2.name:
                        m.__dict__[kk] = self._loadList(gr2)
                    else:
                        m.__dict__[kk] = self._loadObject(gr2)
            
            self.air_shots.append(m)

    def get_mog_names(self):
        names = []
        gr = self.f['/mogs']
        for k in gr.keys():
            names.append(gr[k].attrs['name'])
        return names

    def get_model_names(self):
        names = []
        gr = self.f['/models']
        for k in gr.keys():
            names.append(gr[k].attrs['name'])
        return names
    
    def _loadObject(self, group):
        klass = globals()[group.attrs['BhTomoPyClassName']]
        obj = klass()
        for k in group.attrs.keys():
            obj.__dict__[k] = group.attrs[k]
        for k in group.keys():
            if type(group[k]) is h5py._hl.dataset.Dataset:  # @UndefinedVariable
                obj.__dict__[k] = group[k]
            elif type(group[k]) is h5py._hl.group.Group:  # @UndefinedVariable
                if '_list_' in group[k].name:
                    obj.__dict__[k] = self._loadList(group[k])
                else:
                    obj.__dict__[k] = self._loadObject(group[k])
        return obj
    
    def _loadList(self, group):
        lst = []
        for k in group.keys():
            lst.append(self._loadObject(group[k]))
        return lst

    def _saveObject(self, obj, group):
        
        if 'modified' in obj.__dict__.keys():
            if obj.modified == False:
                # no need to save
                return
            else:
                # reset to False before saving
                obj.modified = False
        
        # loop over attributes
        for k in obj.__dict__.keys():
            # print(k, type(obj.__dict__[k]), obj.__dict__[k])
            if obj.__dict__[k] is None:
                continue
            if type(obj.__dict__[k]) is cgrid2d.Grid2Dcpp:
                continue
            elif type(obj.__dict__[k]) is str:
                group.attrs[k] = obj.__dict__[k]
            elif type(obj.__dict__[k]) is bool:
                group.attrs[k] = obj.__dict__[k]
            elif type(obj.__dict__[k]) is float:
                group.attrs[k] = obj.__dict__[k]
            elif type(obj.__dict__[k]) is int:
                group.attrs[k] = obj.__dict__[k]
            elif type(obj.__dict__[k]) is np.float64:
                group.attrs[k] = obj.__dict__[k]
            elif type(obj.__dict__[k]) is np.int64:
                group.attrs[k] = obj.__dict__[k]
            elif type(obj.__dict__[k]) is np.ndarray:
                try:
                    if group[k].shape != obj.__dict__[k].shape:
                        # we have to delete previous dataset because new one is not same size
                        del(group[k])
                        group[k] = obj.__dict__[k]
                    else:
                        group[k][...] = obj.__dict__[k]
                except:
                    group[k] = obj.__dict__[k]
            elif type(obj.__dict__[k]) is list:
                g = group.require_group('_list_'+k)
                self._saveList(obj.__dict__[k], g)
            else:
                #  must be one of BhTomoPy class
                g = group.require_group(k)
                g.attrs['BhTomoPyClassName'] = obj.__dict__[k].__class__.__name__
                self._saveObject(obj.__dict__[k], g)

    def _saveList(self, lst, group):
        for n in range(len(lst)):
            # group name in index in list
            g = group.require_group(str(n))
            self._saveObject(lst[n], g)


if __name__ == '__main__':

    os.remove('/tmp/test_db.h5')
    db = BhTomoDb()
    db.filename = '/tmp/test_db.h5'
    db.boreholes.append(Borehole('BH1'))
    db.boreholes.append(Borehole('BH2'))
    
    md = MogData()
    md.readRAMAC('testData/formats/ramac/t0302')
    db.mogs.append(Mog('mog1', md))
    db.mogs.append(Mog('mog2', md))
    
    db.models.append(Model('model1'))
    db.air_shots.append(AirShots('air1'))
    db.air_shots[0].data.readRAMAC('testData/air_shots/av0302')
    db.air_shots.append(AirShots('air2'))
    db.air_shots[1].data.readRAMAC('testData/air_shots/ap0302')
    
    g = Grid2D(np.arange(10), np.arange(20))
    db.models[0].grid = g
    
    g.raytrace(np.ones((g.getNumberOfCells(),)), np.array([[0.5, 0.0, 0.5]]), np.array([[8.5, 0.0, 15.5]]))
    
    print(db.modified)
    
    db.save()
    
    print(db.modified)
    
    db.save(obj=db.boreholes[0])
    db.save(obj=db.mogs[0])
    db.save(obj=db.models[0])
    db.save(obj=db.air_shots[0])
    
    db.filename = '/tmp/test_db.h5'
    db.load()
    
    print('Done')
    
    db2 = BhTomoDb()
    db2.filename = '/tmp/test_db.h5'
    print(db2.get_mog_names())