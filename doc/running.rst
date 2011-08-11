Running your own version of Tickery
===================================

Overview
--------

`Fluidinfo <http://fluidinfo.com>`_ wrote Tickery and we have it deployed
at http://tickery.net, which is currently the best place to match up
Tickery's behavior with what you'll see in the source code.

We've open sourced Tickery so other developers can have a close look at
how a non-trivial Fluidinfo application is put together.

But we also want to make it possible for you to run your own version of
Tickery.

To do so, you'll need to make a few high-level configuration changes to the
source code and also tell Twitter that you have a new application. All of
which is described below. These steps are required because we want to
continue running our own version of Tickery while wanting you to be able to
play with the source code and to deploy your own version of Tickery,
without the possibility that you accidentally disrupt the version we have
at http://tickery.net


Prerequisites
-------------

You'll need to install all of the following to run your own copy of
Tickery.

* Python (we use version 2.5.2 in production).
* `Ply <http://www.dabeaz.com/ply/>`_.
* `Sphinx <http://sphinx.pocoo.org/>`_ (to build this documentation)
* `Virtualenv <http://pypi.python.org/pypi/virtualenv>`_.
* `Fabric <http://fabfile.org>`_.

One-time Fluidinfo setup
------------------------

To run your own version of Tickery (as opposed to just browsing the source
code to see how Tickery does its thing), you'll need to use a Fluidinfo user
other than the one we use (we use ``twitter.com``). If you have a Fluidinfo
account, you can use it, otherwise go to http://fluidinfo.com/accounts/new/
and create a Fluidinfo account.

Put the Fluidinfo username you want to use into the ``TWITTER_USERNAME``
variable in ``tickery/www/defaults`` and the Fluidinfo password into an
environment variable named ``FLUIDINFO_TWITTER_PASSWORD``. You should then be
able to create the necessary Fluidinfo namespaces and tags for your Fluidinfo
user with the ``bin/create-twitter-namespaces-and-tags.py`` script.

This does as it says: creates the namespaces and tags that the user in
Fluidinfo will need to have in order for Tickery to work.

One-time Twitter setup
----------------------

Unfortunately we can't give you the consumer key and secret for *our*
running instance of Tickery (at http://tickery.net), so to run your own
version of Tickery, go to http://dev.twitter.com/start and register an
application, then set the consumer key and consumer secret values that
Twitter assigns you in the following environment variables:

.. code-block:: sh

    $ export TICKERY_CONSUMER_KEY=xxxx
    $ export TICKERY_CONSUMER_SECRET=yyyy

Note that the above assume you're using ``bash`` as a shell.

One-time virtualenv setup
-------------------------

Create a virtualenv to run Tickery in, and install the requirements.

.. code-block:: sh

    $ virtualenv tickery-env
    $ . tickery-env/bin/activate
    $ pip install --upgrade -r requirements.txt

Building Tickery's HTML and Javascript via Pyjamas
--------------------------------------------------

If you've installed things correctly you should be able to type ``make`` at
the top level of your ``tickery`` source tree to have the Javascript
built. If this is successful, you'll see terminal output such as the
following:


.. code-block:: sh

    $ make
    cd tickery/www && ../../pyjamas/bin/pyjsbuild index.py
    /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/tickery/www
    Building : index
    PYJSPATH : [
        /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/tickery/www
        /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/pyjamas/library
        /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/pyjamas/addons
    ]
    Translating : /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/tickery/www/tickerytab.py
    Built to : /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/tickery/www/output
    cd tickery/admin && ../../pyjamas/bin/pyjsbuild index.py
    /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/tickery/admin
    Building : index
    PYJSPATH : [
        /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/tickery/admin
        /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/pyjamas/library
        /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/pyjamas/addons
    ]
    Built to : /home/terry/fluidinfo/src/tickery/fix-fab-deploy-798485/tickery/admin/output

To build a debug version of Tickery, use ``make debug`` instead. Note: The
debug version is about 4 times larger than the non-debug one.

You'll need to rebuild the HTML and Javascript each time you make changes
to the Tickery UI code under ``tickery/www`` or ``tickery/admin``.

Starting Tickery
----------------

Start Tickery using ``twistd``:

.. code-block:: sh

    $ cd tickery
    $ PYTHONPATH=.. twistd -n tickery

Note that you have to be in the ``tickery`` directory when you run the
``twistd`` command. The ``twistd`` server expects to find a ``www/output``
directory to serve files from. The PYTHONPATH=.. is needed so that Twisted
can find its plugins.

There are various options you can use, add ``--help`` to the ``twistd``
command above to list them. An important one is ``--cache-dir`` (which
defaults to ``CACHE``), giving the directory into which cache files should
be persisted.

If you run ``twistd`` without the ``-n`` flag it will daemonize and you'll
find log output appear in ``twistd.log``.

Accessing Tickery
-----------------

Once you've started a local version of Tickery, you can see its main page
by visiting http://localhost:6969 in your browser. If port 6969 doesn't
work for you, you can change it with the ``--port`` option to ``twistd``.

Admin interface
---------------

Tickery also has a rudimentary admin interface, which you can see by
visiting http://localhost:6969/admin in your browser. The admin interface
lets you see users on the queue, change the dispatch queue width (set it to
zero to stop Tickery adding new users - addition requests will be queued
but not dispatched until you widen the queue width), pause and resume
addition of users, etc. You can also change the limits on the number of
friends and results that Tickery will allow, add Twitter user names in
bulk, and add users who would exceed the friend limit when added via
the web interface.

Stopping Tickery
----------------

Kill the currently running Tickery using its process id, as stored by
``twistd`` in a file called ``twistd.pid``:

.. code-block:: sh

    $ kill `cat twistd.pid`

Note that there is an issue with this, which is that it waits for any
outstanding Twisted deferreds to finish, and this occasionally does not
happen (due to hanging calls to the Twitter API, I think).

If the kill works, you'll see the eventual exit of Tickery in the
``tickery.log`` file. The cache files in the ``CACHE`` directory (if any)
will also be updated.

If the kill doesn't work, you'll need to kill Tickery with ``kill -9``.
