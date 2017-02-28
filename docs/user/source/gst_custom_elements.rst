GStreamer Backend - Custom Elements
===================================

One of the most used functionality of GStreamer is the ability to create pipelines
from a text description, usually this is done from a CLI interface (e.g. on a terminal)
using the ``gst-launch`` program, in LiSP it's possible to create a custom media-element
using this functionality.

Element Syntax
--------------

From this point ``element(s)`` refer to a GStreamer component and not to LiSP.

Properties
^^^^^^^^^^

*PROPERTY=VALUE*

Sets the property to the specified value. You can use ``gst-inspect`` to find out
about properties and allowed values of different elements.

Elements
^^^^^^^^

*ELEMENT-TYPE [PROPERTY_1 ...]*

Creates an element of type *ELEMENT-TYPE* and sets its *PROPERTIES*.

Links
^^^^^

*ELEMENT_1 ! ELEMENT_2 ! ELEMENT_3*

The simplest link (exclamation mark) connects two adjacent elements. The elements
are connect starting from the left.

Examples
^^^^^^^^

The examples below assume that you have the correct plug-ins available.
Keep in mind that different elements might accept different formats, so you might
need to add converter elements like ``audioconvert`` and ``audioresample`` (for audio)
in front of the element to make things work.

**Add an echo effect to the audio:**

``audioecho delay=500000000 intensity=0.2 feedback=0.3``

**Add a reverb effect to the audio:**

``audioecho delay=20000000 intensity=0.4 feedback=0.45``

**Removes voice from sound (or at least try to do so):**

``audiokaraoke filter-band=200 filter-width=120``

**Remove voice from sound and (then) apply a reverb effect:**

``audiokaraoke filter-band=200 filter-width=120 ! audioecho delay=20000000 intensity=0.4 feedback=0.45``

--------------------------------------------------------------------------------

Extracted from the `GStreamer SDK docs <http://docs.gstreamer.com/display/GstSDK/gst-launch>`_
