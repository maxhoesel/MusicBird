Quick-Start Guide
#################

This guide will give you a quick introduction to MusicBird and how to get it running.

Installation
============

Install MusicBird from PyPI:

.. code::

   pip install --user musicbird

.. note::
   This performs a user installation to :file:`~/.local/bin` to prevent cluttering up the global Python install.
   If you are getting a :code:`Command not found` error when running :code:`musicbird`, make sure that
   :file:`~/.local/bin` is in your :code:`$PATH`

Create Configuration
====================

To generate a new configuration:

.. code::

   musicbird config generate

Then, open the configuration at :file:`~/.config/musicbird/config.yml` and make the following adjustments:

- Uncomment the :code:`source` entry and set it to the directory containing your music library
- Uncomment hte :code:`destination` entry and set it to the directory in which you want to store the converted library

Your config file should look like this:

.. code:: yaml

   source: "/home/max/Music/" # Your music library
   destination: "/mnt/max/mobile/Music" # Your lossy library mirror

   # other configuration options
   # ...

You are now ready to run MusicBird!

Run
===

To scan and process your entire library, run:

.. code::

   musicbird run

MusicBird is now scanning your entire library. Once it has done so, it will copy/convert all your files to the destination directory
and then exit. Feel free to get yourself a coffee, as this process might take a while - up to a few hours for a large library.

Next Steps
==========

To learn more about the MusicBird commands, see :doc:`usage`

To learn about all the configuration options, see :doc:`config`
