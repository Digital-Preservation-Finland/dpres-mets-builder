**NOTE: The project is not ready for production use. It is published prematurely to give an opportunity to get acquainted with the project in advance and to get feedback.**

To give feedback, please open a GitHub issue or pull request.

METS builder
============
A library for easy composing of METS files that conform to the Finnish national METS schema.

Installation
------------
Installation and usage requires Python 3.6 or newer. The software is tested with Python 3.6 on Centos 7.x release.

Create virtual environment and install requirements::

    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools
    pip install -r requirements_github.txt
    pip install .

To deactivate the virtual environment, run ``deactivate``. To reactivate it, run the ``source`` command above.

Usage
-----
See documentation under ``doc/``.

Copyright
---------
Copyright (C) 2022 CSC - IT Center for Science Ltd.

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU Lesser General Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
this program. If not, see https://www.gnu.org/licenses/.
