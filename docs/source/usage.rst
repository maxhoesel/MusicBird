Usage
#####

MusicBird comes with a set of subcommands, each of which perform a specific action.
This page contains an overview for each of them.

Base Command
============

There are a few parameters that can be set regardless of the subcommand you want to run:

.. code::

   musicbird [-c CONFIG] [--loglevel {DEBUG,INFO,WARNING,ERROR,FATAL}] [--version] <subcommand>

* :code:`-c`: Set the path to a custom configuration file. Default: :file:`~/.config/musicbird/config.yml` (see :doc:`config` for details)
* :code:`--loglevel`: Set the verbosity of the application. Default: :code:`INFO`
* :code:`--version`: Print MusicBirds current version and exit

:code:`config`
==============

The :code:`config` subcommad is used to manage the MusicBird configuration file. Currently, there are two subcommands:

:code:`config generate`
-----------------------

Run this command to generate a new config file. You can optionally set the path with the :code:`-o` flag.

Example:

.. code::

   musicbird config generate -o /path/to/musicbird/config.yml

:code:`config print`
--------------------

This command prints out the current (complete) configuration file to STDOUT. Useful for debugging purposes.

Example:

.. code::

   musicbird config print

:code:`scan`
============

Scans the music library for changes and updates MusicBirds database.

Parameters:

* :code:`--rescan`: Delete the current database and re-scan the entire library.

.. warning::

   Using :code:`--rescan` will cause **ALL** files in the library to be re-processed, meaning that lossless files will be re-encoded and so on.
   Avoid using this flag unless your database has become corrupted or you want to re-create your entire library mirror from scratch.

* :code:`--pretend`: Scan the library and show the results, but don't store them in MusicBirds database.
  Helpful if you just want to see what running :code:`scan` would do right now.

Example:

.. code::

   musicbird scan


:code:`run, copy, encode, prune`
================================

These commands process files and update the mirror library. They share a few common parameters

* :code:`--pretend`: Show what changes would be made to the mirror library, but don't actually execute anything.

You can use the :code:`--help` flag to see command-specific extra parameters.

Example:

.. code::

   musicbird run/copy/encode/prune
