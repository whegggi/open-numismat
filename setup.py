#!/usr/bin/env python3
#
# This file is part of OpenNumismat (http://opennumismat.github.io/).
#
# OpenNumismat is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# OpenNumismat is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenNumismat; If not, see <http://www.gnu.org/licenses/>.


###############################################################################
# DOCS
###############################################################################

"""**OpenNumismat** is a handy and reliable application aimed at coin lovers,
numismatists or amateurs looking to create a numismatics collection.

With **OpenNumismat**, you will be able to create, organize and manage your own
coin catalogue with detailed description and photos for each of the items.

Main features:

- More than 60 customizable fields to describe the coin
- Up to 7 photos coins (insert image from file, clipboard, download from the
  Web at URL)
- The grouping, filters and sorting to facilitate the retrieval of coins in the
  catalog
- Generate and print reports, saving as HTML, PDF, MS Word
- Export customized lists as MS Excel, HTML and CSV
- Duplication of coins to quickly add a similar coin
- Batch edit coins
- Ability to add and customize the lists to display the required data
- Does not require additional software to work with a database
- Importing from Colnect, CoinManage, Collection Studio,
  Tellico (additional software may be required), uCoin.net
- Support languages: English, Russian, Ukrainian, Spanish, French, Hungarian,
  Portuguese, German, Greek, Czech, Italian, Polish, Catalan, Dutch, Bulgarian,
  Latvian, Swedish, Persian
- Cross-platform: Windows, Linux, MacOS X

.. image:: http://opennumismat.github.io/images/screenMain.png

OpenNumismat based on PyQt framework with SQLite database engine to store data
collection.
"""


###############################################################################
# IMPORTS
###############################################################################

import os
import shutil
import sys

from setuptools import find_packages
from OpenNumismat.version import Version

try:
    from cx_Freeze import setup, Executable
    cx_Freeze_available = True
except ImportError:
    from setuptools import setup
    cx_Freeze_available = False

WIN32 = sys.platform == "win32"
DARWIN = sys.platform == "darwin"

dependencies = ['jinja2', 'matplotlib', 'numpy', 'xlrd', 'lxml', 'python-dateutil']
if WIN32:
    dependencies.append("win32com")
if WIN32 or DARWIN:
    dependencies.append("pyqt5")
    dependencies.append("xlwt")


templates_packages = []
for dirname, dirnames, filenames in os.walk('OpenNumismat/templates'):
    if filenames:
        templates_packages.append(dirname)

###############################################################################
# PRE-SETUP
###############################################################################

# Common
params = {
    "name": 'OpenNumismat',
    "version": Version,
    "author": 'Vitaly Ignatov',
    "author_email": 'opennumismat@gmail.com',
    "description": 'OpenNumismat',
    "long_description": __doc__,
    "url": 'http://opennumismat.github.io/',
    "license": "GPLv3",
    "keywords": "numismatics, coins, qt, pyqt, collecting, cataloging",
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Natural Language :: Russian",
        "Natural Language :: Spanish",
        "Natural Language :: Ukranian",
        "Natural Language :: Hungarian",
        "Natural Language :: Portuguese",
        "Natural Language :: French",
        "Natural Language :: German",
        "Natural Language :: Greek",
        "Natural Language :: Czech",
        "Natural Language :: Italian",
        "Natural Language :: Polish",
        "Natural Language :: Catalan",
        "Natural Language :: Dutch",
        "Natural Language :: Bulgarian",
        "Natural Language :: Latvian",
        "Natural Language :: Swedish",
        "Natural Language :: Persian",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],

    "install_requires": dependencies,

    # include all resources
    "include_package_data": True,
    "package_data": {'': ['*.png', '*.gif', '*.jpg', '*.ico',
        '*.js', '*.htm', '*.html', '*.css', '*.qm', '*.db', '*.ref',
        '*.mplstyle']},
#    "data_files": data_files,

    "py_modules": ['open-numismat', ],

    "packages": find_packages() + [
        'OpenNumismat/translations',
        'OpenNumismat/db'] +
          templates_packages,

    # auto create scripts
    "entry_points": {
        'console_scripts': [
            'open-numismat = OpenNumismat:run',
        ],
        'gui_scripts': [
            'open-numismat = OpenNumismat:run',
        ]
    }
}

if cx_Freeze_available:
    import PyQt5
    from PyQt5.QtCore import QLibraryInfo, PYQT_VERSION_STR

    importedQtWebEngine = False
    try:
        from PyQt5 import QtWebEngineWidgets
        importedQtWebEngine = True
    except ImportError:
        pass
        

    base = None
    if WIN32:
        base = "Win32GUI"

    if WIN32:
        if PYQT_VERSION_STR == "5.5.1":
            qt_plugin_dir = PyQt5.__path__[0] + '/plugins'
        else:
            qt_plugin_dir = QLibraryInfo.location(QLibraryInfo.PluginsPath)
        executable_ext = '.exe'
    else:
        # Path to Qt on MacPorts
        qt_plugin_dir = '/opt/local/libexec/qt5/plugins'
        executable_ext = ''

    if os.environ.get('PORTABLE'):
        start_script = "open-numismat-portable.py"
    else:
        start_script = "open-numismat.py"

    executable = Executable(start_script, base=base,
                            icon='icons/main.ico',
                            targetName=params['name'] + executable_ext)

    include_files = [
            "COPYING",
            ("OpenNumismat/translations", "translations"),
            ("OpenNumismat/templates", "templates"),
            ("OpenNumismat/db", "db"),
            (qt_plugin_dir + "/imageformats", "imageformats"),
            ("OpenNumismat/opennumismat.mplstyle", "opennumismat.mplstyle"),
        ]
    if WIN32:
        include_files.append(
                (qt_plugin_dir + "/sqldrivers/qsqlite.dll", "sqldrivers/qsqlite.dll"))
        include_files.append(
                (qt_plugin_dir + "/sqldrivers/qsqlodbc.dll", "sqldrivers/qsqlodbc.dll"))
    elif DARWIN:
        include_files.append(
                (qt_plugin_dir + "/sqldrivers/libqsqlite.dylib", "sqldrivers/libqsqlite.dylib"))

        include_files.append(("/opt/local/lib/libsqlite3.0.dylib", "libsqlite3.0.dylib"))
        include_files.append(("/opt/local/lib/libjpeg.9.dylib", "libjpeg.9.dylib"))
        include_files.append(("/opt/local/lib/libmng.2.dylib", "libmng.2.dylib"))
        include_files.append(("/opt/local/lib/libtiff.5.dylib", "libtiff.5.dylib"))
        include_files.append(("/opt/local/lib/liblcms2.dylib", "liblcms2.dylib"))
    build_exe_options = {
            "excludes": [],
            "optimize": 2,
            "include_files": include_files,
            "replace_paths": [(os.path.dirname(os.path.abspath(__file__)) + os.sep, '')],
            "include_msvcr": True  # skip error msvcr100.dll missing
    }
    if WIN32:
        build_exe_options["includes"] = ["lxml._elementpath", "gzip", "inspect", "PyQt5.QtNetwork",
                             "numpy.core._methods", "numpy.lib.format",
                             "matplotlib.backends.backend_ps", "matplotlib.backends.backend_pdf",
                             "matplotlib.backends.backend_svg"]
        if importedQtWebEngine:
            build_exe_options["includes"].append("PyQt5.QtWebEngine")
        else:
            build_exe_options["includes"].append("PyQt5.QtWebKit")
        build_exe_options["build_exe"] = 'build/' + params['name']
    elif DARWIN:
        build_exe_options["includes"] = ["lxml._elementpath", "gzip", "inspect", "PyQt5.QtNetwork",
                         "PyQt5.QtWebKit"]
        build_exe_options["packages"] = ["xlwt", "asyncio"]

    params["executables"] = [executable]
    params["options"] = {"build_exe": build_exe_options,
                         "bdist_mac": {"iconfile": "OpenNumismat.icns", "custom_info_plist": "Info.plist"}}


###############################################################################
# SETUP
###############################################################################

setup(**params)

if WIN32:
    binDir = 'build/OpenNumismat/'
    shutil.rmtree(binDir + "mpl-data/sample_data")
    shutil.rmtree(binDir + "mpl-data/images")
    shutil.rmtree(binDir + "mpl-data/fonts")
    if os.environ.get('PORTABLE'):
        if os.path.exists(params['name'] + '-' + params['version'] + '.zip'):
            os.remove(params['name'] + '-' + params['version'] + '.zip')
        shutil.make_archive(params['name'] + '-' + params['version'], 'zip', 'build/')

# Post bdist_mac
if DARWIN:
    bundleName = params['name'] + '-' + params['version'] + '.app'
    binDir = 'build/' + bundleName + '/Contents/MacOS/'
    shutil.copy("qt.conf", binDir)
    shutil.copy("OpenNumismat.icns", "build/" + bundleName + "/Contents/Resources")

###############################################################################
# MAIN
###############################################################################

if __name__ == '__main__':
    print("Setup for OpenNumismat")
