*************************
Mopidy-WebLibrary
*************************

.. image:: https://travis-ci.org/fbarresi/Mopidy-WebLibrary.svg?branch=develop
    :alt: Travis CI build status

Features
========

//TODO

Dependencies
============

- ``Mopidy`` >= 1.1.0. An extensible music server that plays music from local disk, Spotify, SoundCloud, Google
  Play Music, and more.

Installation
============

Install by running::

    pip install mopidy-weblibrary


Alternatively, clone the repository and run ``sudo python setup.py install`` from within the project directory. e.g. ::

    $ git clone https://github.com/fbarresi/mopidy-weblibrary
    $ cd mopidy-weblibrary
    $ sudo python setup.py install


Configuration
=============

WebLibrary is shipped with default settings that should work straight out of the box for most users::

    [weblibrary]
    enabled = true

The following configuration values are available should you wish to customize your installation further:

- ``weblibrary/enabled``: If the WebLibrary extension should be enabled or not. Defaults to ``true``.


Usage
=====

Enter the address of the Mopidy server that you are connecting to in your browser (e.g. http://localhost:6680/weblibrary)


Project resources
=================

- `Source code <https://github.com/fbarresi/Mopidy-WebLibrary>`_
- `Issue tracker <https://github.com/fbarresi/Mopidy-WebLibrary/issues>`_
- `Download development snapshot <httub.com/fbarresi/Mopidy-WebLibrary/archive/develop.tar.gz#egg=Mopidy-WebLibrary-dev>`_


Changelog
=========

v1.0.0 (UNRELEASED)
-------------------
