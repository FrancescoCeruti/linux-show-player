# Cue Search

This plugin provides an advanced dialog to search and trigger cues by name or description.

## How to use

You can open the dialog via `Tools > Find cues`, or by pressing `Ctrl+F`.

```{image} ../_static/cue_search_dialog.png
:alt: Cue Search dialog
:align: center
```

Type in the search field to filter cues by their **name** or **description**;
matching text is highlighted in the results. When the field is empty, the
currently running cues are listed instead.

The results list shows, for each cue, its icon, index, name and description.
Cues that are fading out are shown with a pulsing icon.

Press `Enter` or `Left-Click` on a result to run an action on the cue.

### Actions

The "Action" selector at the bottom determines what action to perform

* **Focus cue:** reveal the cue in the layout
* **Trigger cue:** start the cue
* **Trigger and focus cue:** start the cue and reveal it in the layout
* **Trigger cue and keep panel open:** start the cue without closing the dialog

The chosen action is remembered between sessions.

### Volume modifiers

While triggering a cue, you can hold a modifier key to adjust its volume:

* `Ctrl`: to play louder
* `Shift`: to play quieter

The volume multipliers can be configured in the plugin settings
(`File > Preferences > Plugins > Cue Search`).
