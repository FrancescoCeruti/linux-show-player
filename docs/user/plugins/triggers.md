# Triggers

Triggers allows to "trigger" actions on _target_ cues when the state of a _source_ cue changes.

For example, when a certain cue ends, you can automatically start another.

## Cue options (Triggers)

Triggers can be managed from the cue of which the state change will trigger an action (source):

```{image} ../_static/triggers_cue_options.png
:alt: Triggers cue options
:align: center
```

* **Trigger:** the state change of the _source_ cue that will trigger the action
  * **Started:** The cue is started (after pre-wait)
  * **Stopped:** The cue is stopped
  * **Paused:** The cue is paused
  * **Ended:** The cue is ended
* **Cue:** the _target_ cue
* **Action:** the action to execute on the _target_ cue

Triggers can be added and removed with the bottom right buttons,
and edited by `Duble-Click` on the value you want to change.