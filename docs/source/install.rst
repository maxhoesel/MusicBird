Installation
############

.. note::

   This guide assumes that you are running a recent version of Ubuntu/Debian.
   The overall steps should be the same on other distributions, but the commands may differ.
   Please see your distributions documentation for details.

Requirements
============

To run MusicBird you need:

* A machine running a recent distribution of Linux with enough CPU power to convert music files
* Python 3.6 or later
* :code:`pip`
* :code:`ffmpeg` installed and ready to go

.. note:: Windows and MacOS are not supported at this time

To install the requirements under Debian/Ubuntu:

.. code::

   sudo apt update && sudo apt install -y ffmpeg python3-pip

Install
=======

Since MusicBird is just a Python package, there a tons of ways you can install it.
This guide will cover two common use cases - a desktop/user installation for personal use, and an installation on an encoding server.

User Install
------------

First, make sure that pip is up-to-date:

.. code::

   python3 -m pip install --upgrade pip


Now, install MusicBird from PyPI like so:

.. code::

   python3 -m pip install --user musicbird

This performs a "user" installation, meaning that the :code:`musicbird` package will be installed into your local user Python environment,
usually located under :file:`~/.local/bin`.
By doing a user install, you are not cluttering up the system install and don't need root permissions.

That's it! MusicBird is now installed. You can check that everything worked with the command below

.. code::

   musicbird --version

.. note::
   If you are getting a :code:`command not found` error when running :code:`musicbird`,
   try logging back out and in. If that doesn't work, you might have to add :file:`~/.local/bin` to your :code:`$PATH`

Virtualenv (Server) Install
---------------------------

If you are planning on running MusicBird on a headless server, it's a good idea to use a virtualenv for isolation.
We are also going to create a separate user for MusicBird to run as, to increase security.

.. seealso::
   To learn more about virtualenvs, see `this guide <https://realpython.com/python-virtual-environments-a-primer/>`_.

First, create a new user for musicbird and switch to it:

.. code::

   sudo adduser --system musicbird --home /opt/musicbird --disabled-password --shell /bin/bash
   sudo -iu musicbird

.. note::

   This command creates a system user without the ability to login. This means that you don't need to set a password for it.

Now, create and activate a virtualenv for MusicBird to run from

.. code::

   cd /opt/musicbird
   python3 -m venv venv
   source venv/bin/activate

Finally, let's upgrade pip and install musicbird

.. code::

   python3 -m pip install --upgrade pip
   python3 -m pip install musicbird

That's it! MusicBird is now installed. You can check that everything worked with the command below

.. code::

   musicbird --version
