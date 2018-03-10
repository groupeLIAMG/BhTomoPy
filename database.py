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
import re
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


class BhTomoDb():
    def __init__(self, fname=''):
        self.filename = fname
        self.air_shots = DbList()
        self.boreholes = DbList()
        self.mogs = DbList()
        self.models = DbList()

        # prepare for special cases
        # Mog.av
        # Mog.ap
        # Mog.Tx
        # Mog.Rx
        # Model.mogs
        self.p = re.compile('/mogs/.*/(av|ap|Tx|Rx)$')
        self.p2 = re.compile('/mogs/.*/(av|ap|Tx|Rx)')
        self.p3 = re.compile('/models/.*/_list_mogs')

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, fname):
        # TODO: check if db is modified before making the change
        if fname != '':
            self.f = h5py.File(fname, 'a')
        self._filename = fname

    @property
    def name(self):
        return os.path.basename(self._filename)
    
    @property
    def modified(self):
        modified = self.air_shots.modified or self.boreholes.modified or self.mogs.modified\
         or self.models.modified
        for obj in self.boreholes, self.air_shots, self.mogs, self.models:
            modified = modified or obj.modified
        return modified

    def save(self, fname=None, obj=None):
        if fname is not None:
            self.filename = fname
            
        # if empty file, create 4 main groups
        self.f.require_group('/boreholes')
        self.f.require_group('/mogs')
        self.f.require_group('/models')
        self.f.require_group('/air_shots')
            
        if obj is not None:
            # obj should be an instance of either a Borehole, Mog, Model or AirShot
            if type(obj) is Borehole:
                group = self.f.require_group('/boreholes/'+obj.name)
            elif type(obj) is Mog:
                group = self.f.require_group('/mogs/'+obj.name)
            elif type(obj) is Model:
                group = self.f.require_group('/models/'+obj.name)
            elif type(obj) is AirShots:
                group = self.f.require_group('/air_shots/'+obj.name)
            else:
                raise TypeError
            
            self._save_object(obj, group)
            self.f.flush()
            
        else:
            # save everything
            if self.boreholes.modified:
                g = self.f.require_group('/boreholes')
                self._save_list(self.boreholes, g)

            if self.mogs.modified:
                g = self.f.require_group('/mogs')
                self._save_list(self.mogs, g)

            if self.air_shots.modified:
                g = self.f.require_group('/air_shots')
                self._save_list(self.air_shots, g)

            if self.models.modified:
                g = self.f.require_group('/models')
                self._save_list(self.models, g)
            
            self.f.flush()
            self.boreholes.modified = False
            self.mogs.modified = False
            self.models.modified = False
            self.air_shots.modified = False

    def save_mog(self, mog):
        # TODO: make sure all boreholes and air_shots held in Tx, Rx, av & ap are in db
        group = self.f.require_group('/mogs/'+mog.name)
        self._save_object(mog, group)
        self.f.flush()
        
    def save_model(self, model):
        # TODO: make sure all mogs held in model.mogs are in db
        group = self.f.require_group('/models/'+model.name)
        self._save_object(model, group)
        self.f.flush()
        
    def load(self, fname=None):
        if fname is not None:
            self.filename = fname

        # make sure we load boreholes & air_shots before mogs, and mogs before models        
        self.load_air_shots()
        self.load_boreholes()
        self.load_mogs()
        self.load_models()

    def get_boreholes(self):
        boreholes = DbList()
        gr = self.f['/boreholes']
        for k in gr.keys():
            b = Borehole(gr[k].attrs['name'])
            for kk in gr[k].attrs.keys():
                b.__dict__[kk] = gr[k].attrs[kk]
            for kk in gr[k].keys():
                b.__dict__[kk] = gr[k][kk]
            boreholes.append(b)
        return boreholes
        
    def load_boreholes(self):
        self.boreholes = self.get_boreholes()

    def get_mogs(self):
        mogs = DbList()
        gr = self.f['/mogs']
        for k in gr.keys():
            m = self._load_mog(gr[k])
            mogs.append(m)
        return mogs

    def load_mogs(self):
        self.mogs = self.get_mogs()

    def get_mog(self, name):
        group = self.f['/mogs/'+name]
        return self._load_mog(group)

    def get_models(self):
        models = DbList()
        gr = self.f['/models']
        for k in gr.keys():
            m = self._load_model(gr[k])
            models.append(m)
        return models

    def load_models(self):
        self.models = self.get_models()

    def get_model(self, name):
        group = self.f['/models/'+name]
        return self._load_model(group)

    def get_air_shots(self):
        air_shots = DbList()
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
                        m.__dict__[kk] = self._load_list(gr2)
                    else:
                        m.__dict__[kk] = self._load_object(gr2)
            air_shots.append(m)
        return air_shots
    
    def load_air_shots(self):
        self.air_shots = self.get_air_shots()

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
    
    def _save_object(self, obj, group):

        # check if special case        
        if self.p.match(group.name) or self.p3.match(group.name):
            # store name
            group.attrs['name'] = obj.name
            return
        elif self.p2.match(group.name):
            # skip
            return
        
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
                self._save_list(obj.__dict__[k], g)
            else:
                #  must be one of BhTomoPy class
                g = group.require_group(k)
                g.attrs['BhTomoPyClassName'] = obj.__dict__[k].__class__.__name__
                self._save_object(obj.__dict__[k], g)

    def _save_list(self, lst, group):
        for n in range(len(lst)):
            # group name in index in list
            g = group.require_group(lst[n].name)
            self._save_object(lst[n], g)

    def _load_object(self, group, caller=None):
        
        if caller is not None:
            # check if special case        
            if self.p.match(group.name):
                name = group.attrs['name']
                p = re.compile('/mogs/.*/([apvTRx]*)')
                tmp = p.match(group.name)
                if tmp:
                    # air_shots
                    att_name = group.name[tmp.regs[1][0]:tmp.regs[1][1]]
                    if att_name == 'av' or att_name == 'ap':
                        for obj in self.air_shots:
                            if obj.name == name:
                                break
                        else:
                            # air_shots not loaded
                            air_shots = self.get_air_shots()
                            for obj in air_shots:
                                if obj.name == name:
                                    break
                            
                    elif att_name == 'Tx' or att_name == 'Rx':
                        for obj in self.boreholes:
                            if obj.name == name:
                                break
                        else:
                            boreholes = self.get_boreholes()
                            for obj in boreholes:
                                if obj.name == name:
                                    break
                    return obj
                else:
                    raise ValueError('Problem reading Mog attribute')
                return
            elif self.p3.match(group.name):
                name = group.attrs['name']
                for mog in self.mogs:
                    if mog.name == name:
                        break
                else:
                    mogs = self.get_mogs()
                    for mog in mogs:
                        if mog.name == name:
                            break
                caller.mogs.append(mog)
                return

        klass = globals()[group.attrs['BhTomoPyClassName']]
        obj = klass()
        for k in group.attrs.keys():
            obj.__dict__[k] = group.attrs[k]
        for k in group.keys():
            if type(group[k]) is h5py._hl.dataset.Dataset:  # @UndefinedVariable
                obj.__dict__[k] = group[k]
            elif type(group[k]) is h5py._hl.group.Group:  # @UndefinedVariable
                if '_list_' in group[k].name:
                    obj.__dict__[k] = self._load_list(group[k])
                else:
                    obj.__dict__[k] = self._load_object(group[k])
        return obj
    
    def _load_list(self, group, caller=None):
        lst = []
        for k in group.keys():
            lst.append(self._load_object(group[k], caller))
        return lst

    def _load_mog(self, group):
        m = Mog()
        for kk in group.attrs.keys():
            m.__dict__[kk] = group.attrs[kk]
        for kk in group.keys():
            if type(group[kk]) is h5py._hl.dataset.Dataset:  # @UndefinedVariable
                m.__dict__[kk] = group[kk]
            elif type(group[kk]) is h5py._hl.group.Group:  # @UndefinedVariable
                gr2 = group[kk]
                if '_list_' in gr2.name:
                    m.__dict__[kk] = self._load_list(gr2)
                else:
                    m.__dict__[kk] = self._load_object(gr2, m)
        return m

    def _load_model(self, group):
        m = Model()
        for kk in group.attrs.keys():
            m.__dict__[kk] = group.attrs[kk]
        for kk in group.keys():
            if type(group[kk]) is h5py._hl.dataset.Dataset:  # @UndefinedVariable
                m.__dict__[kk] = group[kk]
            elif type(group[kk]) is h5py._hl.group.Group:  # @UndefinedVariable
                # we have either a list or a custom class
                gr2 = group[kk]
                if '_list_' in gr2.name:
                    m.__dict__[kk] = self._load_list(gr2, m)
                else:
                    m.__dict__[kk] = self._load_object(gr2)
        return m
    

if __name__ == '__main__':

    if os.path.isfile('/tmp/test_db.h5'):
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
    
    db.mogs[0].Tx = db.boreholes[0]
    db.mogs[0].Rx = db.boreholes[1]
    db.mogs[0].av = db.air_shots[0]
    db.mogs[0].ap = db.air_shots[1]
    db.mogs[1].av = db.air_shots[0]
    db.mogs[1].ap = db.air_shots[1]

    db.models[0].mogs.append(db.mogs[0])
    db.models[0].mogs.append(db.mogs[1])
    
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
      
    print('Done')
    
    db2 = BhTomoDb()
    db2.filename = '/tmp/test_db.h5'
#    db2.load()
    names = db2.get_model_names()
    print(names)
    mod = db2.get_model(names[0])
    print(mod.mogs)