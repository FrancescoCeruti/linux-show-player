# Action cues

Actions cues allows to control other cues status or parameters.

## Collection Cue

This cue allow to tigger multiple cues at once, for each cue a different action can be specified.<br>
The execution is instantaneous, it doesn't keep track of the status of triggered cues.

### Options (Edit Collection)

```{image} ../_static/collection_cue_options.png
:alt: Collection cue options
:align: center
```

You can Add cues to the collection via the `Add` button, and remove the selected one with the `Remove` button.
To edit a value (Cue, Action) `Double-Click` on it.

## Stop All

This cue simply stop all the running cues,
the "stop" action can be configured via the **Stop Settings** tab in the cue edit dialog.

## Seek Action

This cue allow to seek a media-cue to a specific point in time.

### Options (Seek Settings)

* **Cue:** The target media-cue (can be changed via the button labelled `Click to select`)
* **Seek:** The point in time to reach

## Volume Control

This cue allows to trigger a volume change or fade-in/out on a selected media-cue.  

### Options (Volume Settings)

```{image} ../_static/volume_control_cue_options.png
:alt: Volume Control cue options
:align: center
```

* **Cue:** The target media-cue (can be changed via the button labelled `Click to select`)
* **Volume:** The volume to reach (in % or dB)
* **Fade:** Fading options
    * **Duration:** Fade duration in seconds (0 to disable fade)
    * **Curve:** The fade curve

## Index Action

This cue triggers another cue in a specific position (index) in the layout.

### Options (Action Settings)

```{image} ../_static/index_action_cue_options.png
:alt: Index Action cue options
:align: center
```

* **Index**
    * **Use a relative index:** When toggled the position is considered relative to the
      current cue position
    * **Target index:** The position of the target (the UI will enforce a valid index)
* **Action:** The action to execute
* **Suggested cue name:** you can copy this value and use it as the cue name