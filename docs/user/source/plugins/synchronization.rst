Synchronization
===============

The goal of this plugin is to allow two or more LiSP sessions running on different
PCs to be synchronized during a performance (no edit synchronization).
The two session are supposed to be identical, so, only user interaction with the
cues are replicated on other sessions.

How to use
----------

The plugin usage is quite simple, the only thing to do, is to add the remote session
you want to "control" to the peer-list, this can be done via
``Tools > Synchronization > Mange connected peers``

.. image:: ../media/synchronization_peers.png
    :alt: Linux Show Player - Manage synchronization peers
    :align: center

|

On the left you can find the peers list, on the right the following buttons:

* **Discover peers:** Allow to search for other sessions in the network;
* **Manually add peer:** Allow to manually add a peer, using it's IP address;
* **Remove selected peer:** Remove the selected peer;
* **Remove all peers:** Remove all the peers.

To easily retrieve the (local) IP address ``Tools > Synchronization > Show your IP``
will display the current IP address of the PC.

How it works
------------

Once a session is connected, user actions are replicated on the connected one.
This is achieved by sending some info over the network, by default the ``8070``
and ``50000`` (for the discovery) ports are used, those values can be changed
in the configuration file ``$HOME/.linux-show-player/config.cfg``.

Two or more sessions can be mutually connected, this way all the sessions share the same "state".
