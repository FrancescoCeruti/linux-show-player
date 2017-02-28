Cues
====

Cues are the main component of every show/session.
There are multiple types of cues able to perform different tasks, those can be
subdivided in two main categories:

* **Media cues:** used to play multimedia contents, usually related to some media file or stream
* **Action cues:** used to accomplish more complex interaction (e.g. start multiple cues at one),
  fading other cues parameters or interact with external devices or application.

A cue can perform different *actions* depending on its current *state*

**Actions:**
    * ``start:`` Perform the cue task
    * ``stop:`` Stop the running cue
    * ``pause:`` Pause the running cue if possible
    * ``interrupt:`` Stop the running cue, other cues/functions will ignore this event
    * ``fade:`` Decrease/Increase gradually a predefined cue parameter (e.g. volume)

Every action (except for fading) can be performed with or without a fadein/out.


Cue options
-----------

Cue options can edited via a dialog, the way to access this dialog is described
in the layouts pages. Options are organized in tabs depending on their context.

Two tabs are provided for all the cues (excluding plugins):

Appearance
^^^^^^^^^^

Visual options *(some of them can be ignored by the layout)*

* **Cue name:** The name that identify the cue
* **Description/Note:** A text for writing notes about the cue
* **Font size:** The font used to display the name
* **Font color:** The color of the font used to display the name
* **Background color:** The background color of the cue

Cue
^^^

General options for the cue, organized in 3 sub-tabs

Behaviors
"""""""""

Define the default actions used by the cue, this allow to disable fades by default,
or to pause instead of stopping.

* **Start:** Action used to start the cue
* **Stop:** Action used to stop the cue

Pre/Post Wait
"""""""""""""

* **Pre wait:** Add a delay before the cue is started
* **Post wait:** Delay before ``Next action`` is executed
* **Next action:** What to do after ``Post wait`` **(can be ignored by the layout)**
    * *Do Nothing:* You know ...
    * *Auto Next:* Execute the next cue
    * *Auto Follow:* When the cue end, execute the next cue (``Post wait`` value is ignored)

Fade In/Out
"""""""""""

* **Fade In:** Gradually increase a predefined value on faded(in)-actions
    * **Duration:** How long the fade should last before reaching a maximum value
    * **Curve:** How the value should increase in time
* **Fade Out:** Gradually decrease a predefined value on faded(out)-actions
    * **Duration:** How long the fade should last before reaching a minimum value
    * **Curve:** How the value should decrease in time

--------------------------------------------------------------------------------

Media Cues
----------

Audio Cues
^^^^^^^^^^

Audio cues allow you to playback audio files.

A media cue doesn't playback directly the media, but rely on other components,
those can be configured adding and removing effects or controls (e.g. volume, equalizer, speed).

Options
"""""""

* **Media-Cue**
    * **Start time:** Time to skip from the media beginning
    * **Stop time:** Time to skip before the media end
    * **Loop:** Number of repetitions after first play (-1 is infinite)
* **Media Settings:** Media options provided by the backend
    * :doc:`GStreamer backend <gst_media_settings>`

*Video playback support is already planed but not yet implemented*

--------------------------------------------------------------------------------

Action Cues
-----------

Collection Cue
^^^^^^^^^^^^^^

As the name suggest this cue allow to execute multiple cues at once, for each cue
a different action can be specified.

Options (Edit Collection)
"""""""""""""""""""""""""

You can Add/Remove cues to the collection via the provided buttons, ``Double-Click``
values to edit them.

--------------------------------------------------------------------------------

Stop All
^^^^^^^^

This cue simply stop all the running cues, alternately can be configured to
execute different actions.

--------------------------------------------------------------------------------

Seek Action
^^^^^^^^^^^

This cue allow to seek a media cue to a specified point.

Options (Seek Settings)
"""""""""""""""""""""""

* **Cue:** The target media-cue (a button is provided to select the target)
* **Seek:** The time-point to reach

--------------------------------------------------------------------------------

Volume Control
^^^^^^^^^^^^^^

A Volume Control cue allows to trigger a volume change/fade-in/out on a selected media cue.  

Options (Volume Settings)
"""""""""""""""""""""""""

* **Cue:**  The target media-cue (a button is provided to select the target)
* **Volume:** The volume to reach
* **Fade:** Volume fading options
    * **Duration:** The volume fade duration in duration (if 0 the change is instantaneous)
    * **Curve:** The fade curve

--------------------------------------------------------------------------------

MIDI Cue
^^^^^^^^

A MIDI cue allow to send a MIDI message to the MIDI output device used by the application
(can be selected in the application preferences).

Options (MIDI Settings)
"""""""""""""""""""""""

* **MIDI Message:** Set what type of message to send
* **(message attributes):** Depending on the message type different attribute can be edited

Supported MIDI messages
"""""""""""""""""""""""

* ``note*on``
* ``note*off``
* ``control*change``
* ``program*change``
* ``polytouch``
* ``pitchwheel``
* ``song*select``
* ``songpos``
* ``start``
* ``stop``
* ``continue``

--------------------------------------------------------------------------------

Command Cue
^^^^^^^^^^^

This cue allow to execute a shell command, until the command runs the cue is
``running`` and can be stopped, doing so will terminate the command.

To see the command output, LiSP should be launched from a terminal, and
``Discard command output`` must be disabled.

Options (Command Cue)
"""""""""""""""""""""

* **Command:** the command line to be executed (as in a shell)
* **Discard output:** when enabled the command output is discarded
* **Ignore command errors:** when enabled errors are not reported
* **Kill instead of terminate:** when enable, on stop, the command is killed (abruptly interrupted by the OS)

For examples of commands to control external programs, see :doc:`here <command_cue_examples>`.

--------------------------------------------------------------------------------

Index Action
^^^^^^^^^^^^

This cue give the ability to execute a specific action on a cue in a given position
in the layout.

Options (Action Settings)
"""""""""""""""""""""""""

* **Index**
    * **Use a relative index:** When toggled the position is considered relative to the
      current cue position.
    * **Target index:** The position of the target (the UI will enforce a valid index)
* **Action:** The action to execute

--------------------------------------------------------------------------------

Editing multiple cues
---------------------

You can select all cues at once using ``Edit  > Select All`` (``CTRL+A``),
while multiple cues are selected, you can use ``Edit > Edit selected media``
[``CTRL+SHIFT+E``], to edit multiple cues at once.

The available options will depend on the types of the selected cues.
