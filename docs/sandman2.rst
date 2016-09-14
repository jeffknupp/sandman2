API
===

*sandman2* provides a minimal API to control the behavior and inclusion of
resources from the database.

.. automodule:: sandman2
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: sandman2.model.Model
    :special-members: __version__, __url__, __methods__
    :members:
    :undoc-members:

.. autoclass:: sandman2.service.Service
    :members:
    :undoc-members:

The `sandman2.exception` module contains an Exception, expressible in
JSON, for each HTTP status code. In general, code should raise these exceptions
directly rather than making a call to Flask's ``abort()`` method.

.. automodule:: sandman2.exception
    :members:
    :undoc-members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
