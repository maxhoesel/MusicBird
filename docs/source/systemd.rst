Automating MusicBird with Systemd
#################################

While you can run MusicBird manually every time you add new files to your library,
it's also possible to automate the entire process. This guide will set up a Systemd
service and timer to periodically run MusicBird in the background, processing new and changed files for you.

Requirements
============

- A Linux distribution running a recent version of Systemd

.. note:: This guide assumes that you have setup MusicBird as described in the :ref:`server_install` guide.

Creating a Service
==================

First, create a new service file for MusicBird in :file:`/etc/systemd/system/`.
Here, we are going to call our service `musicbird-runner`.

:file:`/etc/systemd/system/musicbird-runner.service`:

.. literalinclude:: files/musicbird-runner.service
   :language: ini

Save and close the file, then register your new service with systemd:

.. code::

   sudo systemctl daemon-reload


You can now run MusicBird in the background if you want to. Simply run:

.. code::

   sudo systemctl start --no-block musicbird-runner.service

.. warning::
    Make sure to include the :code:`--no-block` flag in this command! If you don't, the call to systemctl will block
    until MusicBird has finished processing your library, which could take a while.

If you want to see the current status:

.. code::

   # View the current service status
   sudo systemctl status musicbird-runner.service
   # View the service logs
   sudo journalctl -efu musicbird-runner.service

Automating the Service with a Timer
===================================

To automate running our service, we can use a Systemd timer. This timer file must have the same name as the service, so
:code:`musicbird-runner.timer`.

:file:`/etc/systemd/system/musicbird-runner.timer`

.. literalinclude:: files/musicbird-runner.timer
   :language: ini

Now, run the following commands to register the timer with systemd and to enable it:

.. code::

   sudo systemctl daemon-reload
   sudo systemctl enable --now musicbird-runner.timer # Enable the timer at boot and start it right away.

.. warning::
    Please make sure that you are enabling and starting the **timer**, not the **service**. Enabling the service will
    cause it to run on each boot, which is probably not what you want. If you accidentally enabled the service, you can
    undo this by running :code:`sudo systemctl disable musicbird.service`
