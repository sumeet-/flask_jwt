Setup
=====

.. code-block:: text

    $ mkdir flask-jwt
    $ cd flask-jwt
    $ virtualenv -p python3 venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

Run
===

.. code-block:: text

    $ FLASK_APP=run.py FLASK_DEBUG=1 flask run


Test
====

.. code-block:: text

    $ pytest test_microservice.py
