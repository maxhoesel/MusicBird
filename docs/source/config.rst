Configuration Reference
#######################

MusicBird uses a configuration file to store its settings and preferences.
By default, it is stored at :file:`$XDG_CONFIG_HOME/musicbird/config.yml` (which in turn is usually at :file:`~/.config/musicbird/config.yml))`
To generate a configuration file in this location, run: :code:`musicbird config generate`

The generated configuration file has comments describing every option and what it does.
Feel free to adjust them as needed.

Template Configuration File
===========================

Below is the full configuration file, as output by :code:`musicbird config generate`:

.. literalinclude:: ../../src/musicbird/data/default_config.yml
   :language: yaml
