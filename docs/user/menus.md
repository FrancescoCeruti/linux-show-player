# Menu and Shortcuts

Here you can find a comprehensive list of the standard main menu entries.\
Keyboard shortcut are indicated as ``[key-combination]``.

```{note}
Some of the shortcuts may be different, depending on the used language and desktop environment.
```

## File menu

Settings and operations related to the current session

* **New session:** ``[CTRL+N]`` Open a new (empty) session, if the current session is not saved a confirmation dialog is shown.
* **Open:** ``[CTRL+O]`` Open a saved session, if the current session is not saved a confirmation dialog is shown.
* **Save session:** ``[CTRL+S]`` Save the current session.
* **Save as:** ``[CTRL+SHIFT+S]`` Save the current session in a new files.
* **Preferences:** Open the application settings dialog.
* **Toggle fullscreen:** Enable/Disable fullscreen mode.
* **Exit:** Close "Linux Show Player", if the current session is not saved a confirmation dialog is shown.

## Edit menu

Add/Edit cues (accessible right-clicking on empty areas of the layout)

* **Integration cues:** Add cus that comunicate with different protocols (MIDI, OSC).
* **Media cues:** Add media-cues.
* **Action cues:** Add different types of action-cues.
* **Misc cues:** Add misc cues.
* **Undo:** ``[CTRL+Z]`` Undo the last action (the last action is shown in the bottom of the window).
* **Redo:** ``[CTRL+Y]`` Redo the last undone action.
* **Select all:** ``[CTRL+A]`` Select all the cues.
* **Select all media cues:** Select all and only the media-cues
* **Deselect all:** ``[CTRL+SHIFT+A]`` Deselect all the cues
* **Invert selection:** ``[CTRL+I]`` Invert the selection of all the cues.
* **Edit selected cues:** ``[CTRL+SHIFT+E]`` Open a multi-edit dialog for the selected cues.

## Layout menu

This menu give access to layout functionality and display options for the current view.

### Cart Layout

* **Add page/Add pages:** Allows to add one or multiple pages on the current layout. Pages can be switched using the tab bar on top of the layout or directional keys.
* **Remove current page:** Remove the current page and all its cues.
* **Countdown mode:** Cues will display the remaining time instead of the elapsed time.
* **Show seek-bars:** Media cues will display a seek bar, allowing to directly seek to a specific time of the cue.
* **Show dB-meters:** Media cues will display a dB meter on their right side.
* **Show volume:** Media cues will display a volume control on their right side. Setting the volume to the middle point (50%) of the slider sets the volume to +0dB.
* **Show accurate time:** When checked, cues will display play time with a precision of 0.1s. When unchecked the time is only precise down to 1s.

### List Layout

* **Show dB-meters:** Show / hide the db-meters for running media-cues.
* **Show seek-bars:** Show / hide seek bars for running media-cues.
* **Show accurate time:** Show / hide tens of seconds for running media-cues.
* **Show index column:** Show / hide the cue numbers.
* **Auto-select next cue:** If enabled the next cue is selected automatically.
* **Selection mode:** ``[CTRL+SHIFT+E]`` Enable multi-selection (for editing).
* **Disable GO Key while playing:** Disable the "GO" keyboard shortcut while there are playing cues.
* **Show resize handles:** Enable handles that allow to customize the size of various panels.
* **Restore default size:** Reset the size of panels to their defaults.

## Tools

* **ReplayGain/Normalization:** Volume normalization [[see more]](plugins/replaygain.md).
* **Synchronization:** Keep multiple "live" sessions in sync [[see more]](plugins/synchronization.md).
* **Rename Cues:** Rename multiple cues at once [[see more]](plugins/cue_rename.md).
* **Presets:** Manage cues presets [[see more]](plugins/presets.md).

## About

Info about "Linux Show Player" and some used technologies.

## Cues Menu

Right-clicking a cue will open a menu to access cue-specific options and actions,
like editing and copy/paste.