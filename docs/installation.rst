********************************************************************************
Installation
********************************************************************************

Stable
======

Stable releases are available on PyPI and can be installed with pip.

.. code-block:: bash

    pip install compas_viewer


Latest
======

The latest version can be installed from local source.

.. code-block:: bash

    git clone https://github.com/compas-dev/compas_viewer.git
    cd compas_viewer
    pip install -e .


Development
===========

To install `compas_viewer` for development, install from local source with the "dev" requirements.

.. code-block:: bash

    git clone https://github.com/compas-dev/compas_viewer.git
    cd compas_viewer
    pip install -e ".[dev]"


Known issues
============

For ubuntu users, following dependencies might be required depending on the system version:

.. code-block:: bash

    sudo apt-get install libegl1
    sudo apt-get install python3-opengl
