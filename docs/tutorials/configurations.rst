********************************************************************************
File Structure
********************************************************************************

.. ::`compas_viewer` reads its customized ::`.viewer` file. The file architecture is designed for better data exchange, collaboration, and communication.

.. Concept
.. ===========

.. 1. **Folder-based** :  ::`.viewer` file is a `.zip` folder (archive) that contains files in various formats.

.. 2. **Extendability** :  ::`.viewer` file could contain any type of files. The core functions of viewer are `.json` based and the invoking functions are dictionary-find based, meaning that only missing parameters will cause the loading failure while redundant parameters will only be ignored.

.. Quick Look
.. ==========
