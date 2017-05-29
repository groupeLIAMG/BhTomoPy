# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 08:09:12 2016

@author: giroux

Copyright 2017 Bernard Giroux, Jérome Simon
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

from PyQt5 import QtWidgets, QtCore
import os
import database
from mog import Mog
from model import Model


def chooseMOG(module, filename=None):
    d = QtWidgets.QDialog()

    l0 = QtWidgets.QLabel(parent=d)
    l0.setAlignment(QtCore.Qt.AlignCenter)
    l0.setStyleSheet('background-color: white')

    b0 = QtWidgets.QPushButton("Choose Database", d)
    b1 = QtWidgets.QPushButton("Ok", d)
    b2 = QtWidgets.QPushButton("Cancel", d)

    b3 = QtWidgets.QComboBox(d)

    l0.move(10, 10)
    b0.move(10, 40)
    b1.setMinimumWidth(b2.width())
    b2.setMinimumWidth(b1.minimumWidth())
    b0.setMinimumWidth(10 + 2 * b1.minimumWidth())
    l0.setMinimumWidth(10 + 2 * b1.minimumWidth())
    b3.setMinimumWidth(2 * b1.minimumWidth())

    b3.move(15, 70)

    b2.move(10, 100)
    b1.move(20 + b1.minimumWidth(), 100)

    def cancel():
        nonlocal d
        d.done(0)

    def ok():
        nonlocal d
        d.done(1)

    def choose_db():
        nonlocal d
        nonlocal l0
        nonlocal b3
        filename = QtWidgets.QFileDialog.getOpenFileName(d, 'Choose Database')[0]
        if filename:
            if filename.find('.db') != -1:

                database.load(module, filename)
                l0.setText(os.path.basename(filename))
                load_mogs(filename)

            else:
                QtWidgets.QMessageBox.warning(b3, '', 'Database not in *.db format',
                                              QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton,
                                              QtWidgets.QMessageBox.NoButton)
                l0.setText('')

    def load_mogs(fname):
        nonlocal b3
        nonlocal l0
        nonlocal filename
        mogs = module.session.query(Mog).all()
        if mogs:
            for mog in mogs:
                b3.addItem(mog.name)
            filename = fname
        else:
            QtWidgets.QMessageBox.warning(b3, '', 'File does not contain MOGS.',
                                          QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton,
                                          QtWidgets.QMessageBox.NoButton)
            l0.setText('')

    if filename:
        l0.setText(os.path.basename(filename))
        load_mogs(filename)
    else:
        l0.setText('')

    b1.clicked.connect(ok)
    b2.clicked.connect(cancel)
    b0.clicked.connect(choose_db)

    d.setWindowTitle("Choose MOG")
    d.setWindowModality(QtCore.Qt.ApplicationModal)

    isOk = d.exec_()

    if isOk == 1:
        mog_no = b3.currentIndex()
        if mog_no != -1:
            return module.session.query(Mog).filter(Mog.name == str(b3.currentText())).first()


def chooseModel(module, filename=None):
    d = QtWidgets.QDialog()

    l0 = QtWidgets.QLabel(parent=d)
    l0.setAlignment(QtCore.Qt.AlignCenter)
    l0.setStyleSheet('background-color: white')

    b0 = QtWidgets.QPushButton("Choose Database", d)
    b1 = QtWidgets.QPushButton("Ok", d)
    b2 = QtWidgets.QPushButton("Cancel", d)

    b3 = QtWidgets.QComboBox(d)

    l0.move(10, 10)
    b0.move(10, 40)
    b1.setMinimumWidth(b2.width())
    b2.setMinimumWidth(b1.minimumWidth())
    b0.setMinimumWidth(10 + 2 * b1.minimumWidth())
    l0.setMinimumWidth(10 + 2 * b1.minimumWidth())
    b3.setMinimumWidth(2 * b1.minimumWidth())

    b3.move(15, 70)

    b2.move(10, 100)
    b1.move(20 + b1.minimumWidth(), 100)

    def cancel():
        nonlocal d
        d.done(0)

    def ok():
        nonlocal d
        d.done(1)

    def choose_db():
        nonlocal d
        nonlocal l0
        nonlocal b3
        filename = QtWidgets.QFileDialog.getOpenFileName(d, 'Choose Database')[0]
        if filename:
            if filename.find('.db') != -1:

                database.load(module, filename)
                l0.setText(os.path.basename(filename))
                load_models(module, filename)

            else:
                QtWidgets.QMessageBox.warning(b3, '', 'Database not in *.db format',
                                              QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton,
                                              QtWidgets.QMessageBox.NoButton)
                l0.setText('')

    def load_models(fname):
        nonlocal b3
        nonlocal l0
        nonlocal filename

        models = module.session.query(Model).all()
        if models:
            for model in models:
                b3.addItem(model.name)
            filename = fname
        else:
            QtWidgets.QMessageBox.warning(b3, '', 'File does not contain Models.',
                                          QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton,
                                          QtWidgets.QMessageBox.NoButton)
            l0.setText('')

    if filename:
        l0.setText(os.path.basename(filename))
        load_models(filename)
    else:
        l0.setText('')

    b1.clicked.connect(ok)
    b2.clicked.connect(cancel)
    b0.clicked.connect(choose_db)

    d.setWindowTitle("Choose Model")
    d.setWindowModality(QtCore.Qt.ApplicationModal)
    isOk = d.exec_()

    if isOk == 1:
        model_no = b3.currentIndex()
        if model_no != -1:
            return module.session.query(Model).filter(Model.name == str(b3.currentText())).first()
