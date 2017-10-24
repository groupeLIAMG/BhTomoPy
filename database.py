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

# Functions from 'database' require a module as first parameter. This is a way of allowing the coexistence
# of multiple instances of session throughout the program (one per module). Moreover, because the
# SQLAlchemy objects exist as attributes, they are permanent. Note that any object may replace modules,
# but using the latter is quite convenient, as they are easily accessible.

# To retrieve an object from a database, use <module>.query(<Class>).filter(<Class>.name == <str>).first()
# Note that an object must always be extracted from a filter object by using the *.first() method.
# One could also use <module>.session.query(<Class>).all()[<indice>] to retrieve an object, but this is less
# SQLAlchemy-esque (and probably quite less efficient, as all the instances are retrieved).

# Be wary that a database could fail to load if it is open in another program. The 'verify_database_active'
# function serves the purpose of validating whether or not it is the case.

# One can get the current module so that it can be sent as a parameter like so:
# import sys
# current_module = sys.modules[__name__]

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.automap import automap_base

from PyQt5 import QtWidgets

from borehole import Borehole
from mog import Mog, AirShots
from model import Model
from utils import Base


def create_data_management(module):
    """
    Initiate a module's SQLAlchemy attributes.
    """
    new_data_management(module, ':memory:')


def new_data_management(module, file):

    module.engine = create_engine("sqlite:///" + file)   # 'engine' interacts with the file
    verify_database_active(module.engine)
    module.Session = sessionmaker(bind=module.engine)    # 'Session' acts as a factory for upcoming sessions; the features of 'Session' aren't exploited in BhTomoPy
    module.session = module.Session()                    # the objects are stored in 'session' and can be manipulated from there
    strong_reference_session(module.session)
    Base.metadata.create_all(module.engine)              # this creates the mapping for a specific engine
    module.modified = False                              # 'modified' keeps track of whether or not data has been modified since last save


def load(module, file):
    """
    Safely closes the current file opened in a module and opens a new file.
    """

    try:
        module.session.close()
        module.engine.dispose()

        new_data_management(module, file)

    except AttributeError:
        create_data_management(module)
        load(module, file)
    except OperationalError:
        convert_database(module, file)


def save_as(module, file):
    """
    Closes the current file, safely transfers its items to a new file and overwrites the selected file.
    To simply save a 'session' within the current file, the 'session.commit()' method is preferable.
    * Watch out, though, the session may not be wary of changes caused by methods such as *.append. In such
    cases, to commit properly, one must flag the attribute as modified. This can be achieved with the
    sqlalchemy.orm.attributes.flag_modified method, which takes an mapped object as first parameter and
    the attribute's name (a string) as second parameter.

    e.g.: mog.tt_covar.append(structure) will not be detected because the append method doesn't replace the object.
          mog.data.date = '00-00-0000' will not be detected because the assignment acts on an attribute's attribute.
    Rather write:
          mog.tt_covar.append(structure)
          flag_modified(mog, 'tt_covar')
          mog.data.date = '00-00-0000'
          flag_modified(mog, 'data')

    This happens because PickleType doesn't track changes made in place. Refer to:
    https://bitbucket.org/zzzeek/sqlalchemy/issues/2994/pickletype-gets-not-updated-in-database-in

    TODO: One should consider coding mutable custom types in order to eradicate this issue:
    http://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/mutable.html?highlight=mutation
    """

    try:

        # TODO Reflecting the mapping instead of merging might make the code more efficient

        items = get_many(module)  # temporarily stores the saved items

        module.session.close()
        module.engine.dispose()

        new_data_management(module, file)

        for item in get_many(module):  # overwrites the selected file
            module.session.delete(item)

        items = [module.session.merge(item) for item in items]  # conforms the stored items to the new session
        module.session.add_all(items)

        module.session.commit()

    except AttributeError:
        create_data_management(module)
        save_as(module, file)


def get_many(module):
    """
    Gets all instances stored within a session.
    """

    items = []

    for item in (Borehole, Mog, AirShots, Model):

        items += module.session.query(item).all()

    return items


def delete(module, item):
    """
    Deletes an item, even if the item was just added (i.e. not committed, pending).
    """

    from sqlalchemy import inspect
    if inspect(item).persistent:
        module.session.delete(item)
    else:
        module.session.expunge(item)
    module.modified = True


def airshots_cleanup(module):
    """
    Deletes airshots that aren't associated with a mog.
    """

    used_airshots = []

    for mog in module.session.query(Mog).all():
        for airshot in mog.av, mog.ap:
            if airshot is not None and airshot not in used_airshots:
                used_airshots.append(airshot)

    for airshot in module.session.query(AirShots).all():
        if airshot not in used_airshots:
            delete(module, airshot)


def long_url(module):
    """
    Returns a string of the form '*.db',
    possibly with additional preceding directories.
    """
    return str(module.engine.url)[10:]


def short_url(module):
    """
    A failsafe method for obtaining strictly the url of the engine,
    i.e. '*.db', without any preceding directories.
    """
    return os.path.basename(long_url(module))


def strong_reference_session(session):
    """
    Modifies a session in such a way that the objects it contains aren't
    garbage-collected by mistake.
    Taken from SQLAlchemy's website.
    """
    @event.listens_for(session, "pending_to_persistent")
    @event.listens_for(session, "deleted_to_persistent")
    @event.listens_for(session, "detached_to_persistent")
    @event.listens_for(session, "loaded_as_persistent")
    def strong_ref_object(sess, instance):
        if 'refs' not in sess.info:
            sess.info['refs'] = refs = set()
        else:
            refs = sess.info['refs']

        refs.add(instance)

    @event.listens_for(session, "persistent_to_detached")
    @event.listens_for(session, "persistent_to_deleted")
    @event.listens_for(session, "persistent_to_transient")
    def deref_object(sess, instance):
        sess.info['refs'].discard(instance)


def convert_database(module, file):
    """
    Converts an outdated database into a database that is conform to the actual mapping.
    Such an outdated database may appear because an attribute has been added or removed,
    or because an attribute's name has been altered.
    """

    warning = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, 'Database outdated',
                                    "This database's mapping might be outdated. " +
                                    "Proceeding will cause this database to be updated. " +
                                    "Do you want to proceed?")
    warning.addButton(QtWidgets.QMessageBox.Yes)
    warning.addButton(QtWidgets.QMessageBox.No)
    warning.setDefaultButton(QtWidgets.QMessageBox.No)

    if warning.exec_() == QtWidgets.QMessageBox.Yes:

        # TODO not functional

        # class dummy_module():
        #     pass
        # module_ = dummy_module()

        # module_.engine  = create_engine("sqlite:///" + file)
        # module_.Session = sessionmaker(bind=module_.engine)
        # module_.session = module_.Session()
        # strong_reference_session(module_.session)

        # Base = automap_base()
        # Base.prepare(module_.engine, reflect=True)

        # module_.session.commit()

        load(module, file)


def verify_database_active(engine):
    """
    Verifies whether a database associated with an engine is open or not. If it is, throws a warning.
    """
    url = os.path.basename(str(engine.url)[10:])
    if url != ':memory:':
        try:
            if not os.path.exists(url):
                return
            os.rename(url, url)  # Renaming the file fails if the database is already in use

        except OSError:
            warning = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, 'Database in use',
                                            "This database is already in use. " +
                                            "Please close other instances of BhTomoPy before proceeding.\n" +
                                            "Try again?")
            warning.addButton(QtWidgets.QMessageBox.Yes)
            warning.addButton(QtWidgets.QMessageBox.No)
            warning.setDefaultButton(QtWidgets.QMessageBox.Yes)

            if warning.exec_() == QtWidgets.QMessageBox.Yes:
                verify_database_active(engine)
            else:  # TODO exiting might not be the desired action
                exit()
