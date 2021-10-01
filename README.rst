MusicBird - Convert your Music library on-the-fly 🐦
####################################################

.. image:: https://img.shields.io/github/workflow/status/maxhoesel/MusicBird/CI.svg
   :target: https://img.shields.io/github/workflow/status/maxhoesel/MusicBird/CI.svg
.. image:: https://img.shields.io/pypi/pyversions/musicbird.svg
   :target: https://img.shields.io/pypi/pyversions/musicbird.svg
.. image:: https://img.shields.io/pypi/l/musicbird.svg
   :target: https://img.shields.io/pypi/l/musicbird.svg
.. image:: https://img.shields.io/codecov/c/github/maxhoesel/MusicBird.svg
   :target: https://img.shields.io/codecov/c/github/maxhoesel/MusicBird.svg

----

MusicBird is a python package that creates a mobile-friendly copy of your music library. Its major features include:

* It's *fast*! Not only does it use all your cores when encoding files, it also remembers the state of your library from when you last ran it.
  This means that MusicBird will only process those files that have actually changed since then.
* It works with any music library! You don't need to adjust your library structure at all for MusicBird to do its magic - in fact, you could make it read-only
  and everything would still work just fine!
* It tracks modified and deleted files! Did you change the tags of a file and want them on your phone as well?
  Do you no longer like that artist and deleted all their music from your library? Don't worry!
  MusicBird will pick up those changes and adjust the mirror copy accordingly
* It's flexible! MusicBird uses the excellent `ffmpeg libraries <https://ffmpeg.org/>`_ under the hood,
  meaning that most common input and output formats are supported.

Documentation
=============

See the `official docs <https://musicbird.readthedocs.io/en/latest/>`_ for installation and usage instructions

Author & License
================

Written and maintained by Max Hösel (@maxhoesel)

Licensed under the GNU GPLv3 or later
