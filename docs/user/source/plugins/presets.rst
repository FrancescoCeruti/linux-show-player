Presets
=======

Allow to create, edit, import and export presets for cues.

How to use
----------

The main interface is accessible via ``Tools > Presets``

.. image:: ../media/presets.png
    :alt: Linux Show Player - Presets
    :align: center

|

On the left the list of the available presets (sorted by name), double-click to
edit a preset. Multiple preset can be selected using the ``CTRL`` and ``SHIFT``.

On the right a series of buttons gives access to the following:

* **Add:** allow to manually create a preset
* **Rename:** rename the selected preset
* **Edit:** edit the selected preset
* **Remove:** remove the selected preset
* **Create Cue:** create a cue from the selected presets
* **Load on selected Cues:** load a preset on selected cues

On the bottom:

* **Export selected:** export the selected presets to a custom archive
* **Import:** import from an exported preset

.. Note::
    The archive use a custom extension to easily filer others files, but it's a
    standard zip file.

The following options are provided in the cue context menu (right-click):

* **Load preset:** load a preset on the cue
* **Save as preset:** save the cue settings as a preset

.. Note::
    Preset are saved under ``$HOME/.linux-show-player/presets/``
