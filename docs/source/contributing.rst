Contributing to MusicBird
#########################

This document should contain all the information you need to contribute to MusicBird.

.. note:: By contributing to this project, you show that you have read and agree with with the `Code of Conduct. <https://github.com/maxhoesel/MusicBird/blob/main/CODE_OF_CONDUCT.md>`_

Initial Setup
=============

Make sure that you have the regular MusicBird dependencies installed (such as ffmpeg).

This project uses `poetry <https://python-poetry.org>`_ for dependency management and `tox <https://tox.wiki/en/latest>`_ for running tests/integrations.

Automatic installation
----------------------

To install the dev dependencies and setup the environment, simply run :code:`scripts/setup.sh` from your user shell.
Alternatively, you can follow the manual steps below.

Manual installation
-----------------------

1. Install the following python packages (preferably via pip): :code:`tox poetry`
2. Create a virtual environment for the project (via poetry) and activate it in your IDE and shell
3. (Optional: Install the pre-commit hook to automatically lint your commit messages :code:`poetry run pre-commit install --hook-type commit-msg`)

Conventions and Best Practices
==============================

Commit Messages
---------------

Follow the guidelines below when committing your changes

* All commits **must** follow the `conventional-commits standard <https://www.conventionalcommits.org/en/v1.0.0/>`_:
  :code:`<type>(optional scope): <description>`
  * Valid scopes are all components of this project, such as modules or commands
* Structure your changes so that they are separated into logical and independent commits whenever possible.
* The commit message should clearly state **what** your change does. The "why" and "how" belong into the commit body.
* Note that if you install the pre-commit hook, your commit messages will be checked automatically upon committing,
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

   Tox tries to test against all python versions that MusicBird supports. This means that some pyxx tests might fail
   on your machine, because you probably don't have all of them installed. You can use a tool like PyEnv to manage
   Python installations if you want to. Alternatively, the CI will run against all python versions when you create a pull request.

Writing new Tests
-----------------

Any significant code in the MusicBird source should have tests associated with it. If you are adding a new feature or similar,
you will therefore also have to write some tets. You can take a look at the existing tests for guidance.

Note that there are several fixtures available that you can use in your tests - see the :file:`tests/conftest.py` file
for more details on their usage.

When running test with Tox, it will automatically generate a coverage report for you. You can view the results by opening
:file:`htmlcov/index.html` in your browser.

Documentation
=============

Documentation is generated from the source files in :file:`docs/source/` and module docstrings.

If you are adding a new package/module, make sure to add it to :file:`modules.rst` or :file:`musicbird.rst` respectively.

To regenerate the documentation, run :code:`tox -e docs`.
