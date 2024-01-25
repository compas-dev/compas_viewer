*******************************************************************************
Windows Messages
*******************************************************************************


.. autosummary::
    :toctree:
    :nosignatures:


You can add window pop-up messages to your viewer using the following methods.



"About" Level Message
=====================
To display "about" message from the configuration file:

.. code-block:: python

    viewer.layout.window.about()

.. image:: ../../_images/about.jpg


"Info" Level Message
====================
To display "info" message:

.. code-block:: python

    viewer.layout.window.info("This is an info message.")

.. image:: ../../_images/info.jpg

"Warning" Level Message
=======================
To display "warning" message:

.. code-block:: python

    viewer.layout.window.warning("This is a warning message.")

.. image:: ../../_images/warning.jpg

"Critical" Level Message
========================
To display "critical" message:

.. code-block:: python

    viewer.layout.window.critical("This is an error message.")

.. image:: ../../_images/critical.jpg

"Question" Level Message
========================
To display "question" message:

.. code-block:: python

    viewer.layout.window.question("This is a question message.")

.. image:: ../../_images/question.jpg

"Confirm" Level Message
=======================
To display "confirm" message:

.. code-block:: python

    viewer.layout.window.confirm("This is a confirmation message.")

.. image:: ../../_images/confirm.jpg
