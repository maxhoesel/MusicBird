MusicBird Documentation
#######################

Welcome to the documentation for MusicBird, an advanced Python package for creating mobile-friendly copies of your music library.

.. _purpose:

Purpose of the Project
======================

With the advent of lossless music file formats such as FLAC, music libraries can now often range in the dozens of gigabytes.
Fitting all of that onto a mobile device can be tricky, if not impossible.

This is where MusicBird comes in.

MusicBirds main goal is to make carrying around your music library with you easy and painless, even on devices with limited storage.
To achieve this, MusicBird creates a copy of your music library, with all lossless files converted into a more space-saving, lossy format,
leaving your regular and lossy music files untouched. Note that MusicBird does **not** modify your original library -
it only creates a copy that you can then push to your phone or media player.
It also keeps track of changes during runs, so it only processes those files that have changed since the last run

It was created because I (the author) wasn't satisfied with the existing options for automatically compressing a music library.
Most of them were either hard to automate or didn't account for things such as modified/deleted files.

Features
========

Here's some of the most important features of MusicBird, in no particular order:

* It's *fast*! Not only does it use all your cores when encoding files, it also remembers the state of your library from when you last ran it.
  This means that MusicBird will only process those files that have actually changed since then.
* It works with any music library! You don't need to adjust your library structure at all for MusicBird to do its magic - in fact, you could make it read-only
  and everything would still work just fine!
* It tracks modified and deleted files! Did you change the tags of a file and want them on your phone as well?
  Do you no longer like that artist and deleted all their music from your library? Don't worry!
  MusicBird will pick up those changes and adjust the mirror copy accordingly
* It's flexible! MusicBird uses the excellent `ffmpeg libraries <https://ffmpeg.org/>`_ under the hood,
  meaning that most common input and output formats are supported.

Contents
========

If you want to get started right away, check out the :doc:`quickstart`.

If not, see below for the table of contents and more detailed instructions.

.. toctree::
   :maxdepth: 1
   :caption: User Documentation

   install
   concepts
   usage
   config


.. toctree::
   :maxdepth: 1
   :caption: Guides

   quickstart
   systemd

.. toctree::
   :maxdepth: 2
   :caption: Development and Contributing

   contributing
   modules
