ReplayGain & Normalization
==========================

This module provide a simple utility to calculate a `Normalized`_ / `ReplayGain`_
volume for media cues. The values are used as *Normalized Volume* for the ``Volume``
media-element, if a ReplayGain value is already stored in the media-file metadata
(e.g ID3 tags) it will be used.

.. Note::
    The original files are left untouched.

How to use
----------

Via ``Tools > ReplayGain / Normalization`` menu the following options are provided:

* **Calculate**: Open a dialog to set some option and start the calculation
* **Reset all**: Reset to 0dB the normalized volumes of all cues
* **Reset selected**: Reset to 0dB the normalized volumes, only for the selected cues

.. image:: ../media/replaygain_dialog.png
    :alt: Linux Show Player - ReplayGain dialog
    :align: center

|

* **ReplayGain**: Use ReplayGain normalization using the reference value in dB SPL (89 is the standard default)
* **Normalize**: Use a simple normalization to the reference value in dB (0 is the maximum value)
* **Only selected cues**: apply only to the currently selected cues
* **Thread number**: Number of concurrent/parallel calculations (default to the cup cores)

.. Note::
    that the process may require some time, depending on the CPU, the number
    and size of the files involved.

.. _Normalized: https://en.wikipedia.org/wiki/Audio_normalization
.. _ReplayGain: https://en.wikipedia.org/wiki/ReplayGain