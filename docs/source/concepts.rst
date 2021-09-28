Concepts
########

This documents goal is to give you a basic overview over how MusicBird operates.
If you prefer to get up-and-running quickly, check out the :doc:`quickstart` instead.

Basic Operation
===============

MusicBird works by reading information from your music library and using that information to create a compact
copy of the library, ready for transfer to mobile devices.

On a very basic level, MusicBird needs to perform two tasks:

#. Scan your music library for files
#. Process those files (e.g. convert, copy, delete them)

The various :code:`musicbird` subcommands all relate to these basic tasks:
Scannig is done with the :code:`scan` subcommand, while processing is handled by :code:`copy, encode, prune`.
:code:`run` simply runs all these commands sequentially so you don't have to memorize them.

Scan
====

The scan is pretty simple. MusicBird registers new files and checks existing ones for changes.
It then marks any files that need to be (re-)processed.
Finally, it marks all files that are no longer in the library for deletion and stores the result in its database.

Processing
==========

During processing, MusicBird reads all files that need processing from the database and applies one of several actions to each.
These actions are:

* **copy**: Copy the file to the mirror library as-is
* **encode**: Convert the file to a lossy format and save the output in the mirror
* **delete**: Delete the file in the mirror

Each of these actions maps to a MusicBird subcommand, and running that command will processes all files
that assigned to that action.

There's a also a special action, **ignore**, which tells MusicBird to not track this file.

Which of these actions MusicBird applies a file depends on its file type, the configuration, whether it was changed, etc.
To summarize:

* If the file is a lossless audio file, it will be **encoded**.
* If the file is a lossy audio file, it will either be **copied**, **encoded** or **ignored**,
  depending on the :code:`lossy_files` configuration parameter.
* If the file is an album art cover (such as :file:`cover.jpg`), it will be **copied** if :code:`copy.albumart` is :code:`True`,
  else it will be  **ignored**.
* If the file is another kind of file (text, movie, etc.), it will be **copied** if :code:`copy.other` is :code:`True`,
  else it will be  **ignored**.
* If the file was deleted in the original library and the :code:`prune` configuration parameter is set, it will be **deleted**.
