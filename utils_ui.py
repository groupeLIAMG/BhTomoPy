# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 08:09:12 2016

@author: giroux
"""

from PyQt4 import QtGui, QtCore
import dbm
import os
import shelve
import sys

def chooseMOG(filename=None):
    d = QtGui.QDialog()

    l0 = QtGui.QLabel(parent=d);
    l0.setAlignment(QtCore.Qt.AlignCenter)
    l0.setStyleSheet('background-color: white')
    
    b0 = QtGui.QPushButton("Choose Database", d)
    b1 = QtGui.QPushButton("Ok", d)
    b2 = QtGui.QPushButton("Cancel", d)
    
    b3 = QtGui.QComboBox(d)

    l0.move(10,10)
    b0.move(10,40)
    b1.setMinimumWidth( b2.width() )
    b2.setMinimumWidth( b1.minimumWidth() )
    b0.setMinimumWidth( 10+2*b1.minimumWidth())
    l0.setMinimumWidth( 10+2*b1.minimumWidth())
    b3.setMinimumWidth( 2*b1.minimumWidth())
    
    b3.move(15,70)
    
    b2.move(10,100)
    b1.move(20+b1.minimumWidth(),100)

    def cancel():
        nonlocal d
        d.done(0)
        
    def ok():
        nonlocal d
        d.done(1)
    
    def choose_db():
        nonlocal d
        nonlocal l0
        filename = QtGui.QFileDialog.getOpenFileName(d, 'Choose Database')
        if filename is not '':
            if '.db' in filename:
                filename = filename[:-3]
            l0.setText( os.path.basename(filename) )
            load_mogs(filename)
        
        
        
    def load_mogs(filename):
        nonlocal b3
        nonlocal l0
        try:
            sfile = shelve.open(filename, flag='r')            
            mogs = sfile['mogs']
            for mog in mogs:
                b3.addItem(mog.name)
            sfile.close()
        except dbm.error:
            QtGui.QMessageBox.warning(b3, '', 'Database not in shelve format',
                        QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton,
                        QtGui.QMessageBox.NoButton)
            l0.setText( '' )
        except KeyError:
            QtGui.QMessageBox.warning(b3, '', 'File does not contain MOGS',
                QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton,
                          QtGui.QMessageBox.NoButton)
            l0.setText( '' )



    if filename is not None and filename is not '':
        l0.setText( os.path.basename(filename) )
        load_mogs(filename)
    else:
        l0.setText('')


    b1.clicked.connect( ok )
    b2.clicked.connect( cancel )
    b0.clicked.connect( choose_db )
    
    d.setWindowTitle("Choose MOG")
    d.setWindowModality(QtCore.Qt.ApplicationModal)
    isOk = d.exec_()
    
    if isOk == 1:
        mog_no = b3.currentIndex()
        if mog_no == -1:
            isOk = 0            
    else:
        mog_no = -1;
        
    return mog_no, filename, isOk



if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    mog_no, fname, ok = chooseMOG()
    
    print(mog_no)

    sys.exit(app.exec_())
