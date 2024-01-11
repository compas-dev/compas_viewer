********************************************************************************
Installation
********************************************************************************
COMPAS Viewer can be easily installed on multiple platforms, using popular package managers such as conda or pip.

If you don't have COMPAS installed
===================================
Check out the COMPAS installation instructions at https://compas.dev/compas/latest/userguide/installation.html

If you have COMPAS installed
============================
Activate your COMPAS environment and install COMPAS Viewer from `pip`.

.. code-block:: bash

    pip install compas_viewer

Verify the installation
=======================
COMPAS Viewer can be simply lunched by the following command in your terminal:

.. code-block:: bash

    python -m compas_viewer

Update with pip
===============
Update COMPAS Viewer to the latest version with pip.

.. code-block:: bash

    pip install --upgrade compas_viewer

Known issues
============
For ubuntu users, following dependencies might be required depending on the system version:

.. code-block:: bash

    sudo apt-get install libegl1
    sudo apt-get install python3-opengl
