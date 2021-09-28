Contributing to MusicBird
#########################

This document should contain all the information you need to contribute to MusicBird.

.. note:: By contributing to this project, you show that you have read and agree with with the `Code of Conduct. <https://github.com/maxhoesel/>`_

Initial Setup
=============

This project uses `Tox <https://tox.readthedocs.io/en/latest/>`_ for testing and other development workflows.
Tox allows us to quickly setup up reproducible build and test environments, so it is used in all CI tasks and integrations.

To setup Tox:

1. Install tox from your distributions package repositories (probably :code:`tox` or :code:`python3-tox`.
2. For this repository and clone it: :code:`git clone git@github.com:yourUsername/MusicBird`
3. Enter the repository and run :code:`tox -l`: :code:`cd MusicBird && tox -l`. Tox will now initialize itself
   and then display all available environments. You can run :code:`tox` to run all tests/integration steps at once.

Now,change to a feature branch and start making your changes. Whenever you are ready to test, you can just run :code:`tox -e <environment>`
to run the individual test steps.

.. note:: As a general rule of thumb, always run :code:`tox` fully before committing any changes.

.. _editable_dev_setup:

Editable Setup
--------------

Sometimes, debugging issues from within tox runs can be hard and tedious. In those situations, a local editable environment can help.
This allows you to make changes to the code and directly run tests/CLI commands without having to repackage anything, nor run tox.

This project provides a script for exactly this purpose. Simply run :file:`./scripts/setup.sh` to initialize a local
development environment. This script create a new venv at :file`.venv`, then installs MusicBird, plus some other utilities.

To activate this environment, run: :code:`. .venv/bin/activate`

From now on, you can make changes to MusicBirds source code and immediately test them on the CLI/in Pytest,
without having to rebuild the package with tox.

Conventions and Best Practices
==============================

Commit Messages
---------------

Follow the guidelines below when committing your changes

* All commits **must** follow the <conventional-commits standard https://www.conventionalcommits.org/en/v1.0.0/>_:
  :code:`<type>(optional scope): <description>`
  * Valid scopes are all components of this project, such as modules or commands
* Structure your changes so that they are separated into logical and independent commits whenever possible.
* The commit message should clearly state **what** your change does. The "why" and "how" belong into the commit body.
* Note that if you use the :ref:`editable_dev_setup`, your commit messages will be checked automatically upon committing,
  allowing you to make modifications before adding them to your branch.

Some good examples:
* :code:`fix(prune): also delete files with unicode chars`
* :code:`feat: Add "config edit" command`

Don't be afraid to rename/amend/rewrite your branch history to achieve these goals!
Take a look at the :code:`git rebase -i` and :code:`git commit --amend` commands if you are not sure how to do so.

Code Format
-----------

Please make sure to format your code with autopep8. Your IDE/Editor should support this.

Docstrings for methods, modules, etc. use the `Google docstring format <https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings>`_.

Running and writing Tests
=========================

MusicBirds test suite is split into two parts: unit (quick, basic, isolated) and integration (more complete, slower).
You can one (or both) using :code:`tox` (:code:`tox -- tests/unit`, :code:`tox -- tests/integration`.

.. note::

   Tox tries to test against all python versions that MusicBird supports (3.8 and up as of October 2021).
   Unless you happen to have


Writing new Tests
-----------------

Any significant in the MusicBird source should have tests associated with it. If you are adding a new feature or similar,
you will therefore also have to write some tets. You can take a look at the existing tests for guidance.

Note that there are several fixtures available that you can use in your tests - see the :file:`tests/conftest.py` file
for more details on their usage.

When running test with Tox, it will automatically generate a coverage report for you. You can view the results by opening
:file:`htmlcov/intex.html` in your browser.

Documentation
=============

Documentation is generated from the source files in :file:`docs/source/` and module docstrings.

If you are adding a new package/module, make sure to add it to :file:`modules.rst` or :file:`musicbird.rst` respectively.

To regenerate the documentation, run :code:`tox -e docs`.
