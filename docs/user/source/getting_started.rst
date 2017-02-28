.. toctree::
   :hidden:
   :maxdepth: 1


Getting Started
===============

Before diving into the different aspects of LiSP you need to understand the main
concepts that set the basis on how the application works.

Cues
----

First, and probably the most important components you will find in LiSP, are the **cues**,
a cue is used to execute a specific action in a repeatable manner, every cue
allow customization of its behaviours independently.

Cues are at the heart of every show, allowing to play sounds, send MIDI messages,
controls other cues and so on.

Layouts
-------

When creating a new show in LiSP you have the ability to chose a *layout*, this
will affect how cues will be displayed and eventually provides different sets of features.

Currently two layouts are provided:

* **List Layout:** arrange the cues in a list and provided a mouse/keyboard oriented UI
* **Cart Layout:** arrange the cues as buttons in one or more grids and provide a more touch-oriented UI.

Menus
-----

Most of the functionality are accessible via the top-bar menu, here a small
explanation on what you will find:

* **File:** Operation related to the current session or the global application
* **Edit:** Functions mainly related to adding/editing cues (accessible right-clicking on empty areas of the layout)
* **Layout:** Functions provided by the current layout
* **Tools:** Utility to make life easier

Cues provides a contextual (right-click) menu to access cue-specific options.

Plugins
-------

Linux Show Player is heavily based on plugins, while this is almost always
hidden from the user, most of the functionality are provided via plugins.
From time to time the documentation may refer to those as plugins or modules.
