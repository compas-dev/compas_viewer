********************************************************************************
Actions
********************************************************************************

:mod:`compas_viewer` provides rich interactivity by allowing the user to define their preferred key shortcuts
as well as the expected action behaviours. The :class:`compas_viewer.actions.action.Action` class is the base class
for all actions.

Buildin Actions
================
Some buildin actions are provided which can be checked out by the following code:

>>> from compas_viewer.actions import ITEM_ACTIONS
>>> print(ITEM_ACTIONS)

The key names in the controller configuration file should match the action names to call the action correctly.

We encourage you contribute and share the created actions by submitting a pull request to the :mod:`compas_viewer` repository.


Custom Actions
================
You can create your own actions by inheriting from the :class:`compas_viewer.actions.action.Action` class:

# TODO
