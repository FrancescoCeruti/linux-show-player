# Presets

This plugin allows to create, edit, import and export presets for cues.

Presets have multiple purposes:
  * Easy replicate cues
  * Apply certain settings to one or multiple cues
  * Exchange cue configurations between users 

**Presets are global.** All shows/sessions in the same user account have access to same presets.

## How to use

The interface, where you can manage your presets, is accessible via `Tools > Presets`

```{image} ../_static/presets_main_dialog.png
:alt: Presets
:align: center
```

On the left, the list of the available presets (sorted by name), you can `Double-Click` to
edit a preset, you can select multiple entries by using the stander `CTRL` and `SHIFT` modifiers.

On the right a series of buttons gives access to the following:

* **Add:** create a new preset
* **Rename:** rename the selected preset
* **Edit:** edit the selected preset
* **Remove:** remove the selected preset
* **Create Cue:** create a new cue from the selected presets
* **Load on selected Cues:** load a preset on selected cues

On the bottom:

* **Export selected:** export the selected presets
* **Import:** import presets form an existing export

```{note}
The exported file use the `.presets` extension to easily filter others files, but it's a standard zip file.
```

### Contex menu

The following options are provided in each cue context menu (right-click):

* **Load preset:** load a preset on the cue
* **Save as preset:** save the cue settings as a preset

```{warning}
While it's possible to undo/redo actions on cues, like loading a preset on a cue, changes to the presets are not undoable. 
```