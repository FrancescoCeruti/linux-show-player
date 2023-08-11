# List Layout

```{image} _static/list_layout_main_view.png
:alt: Linux Show Player - List Layout
:align: center
```

<br>
The List Layout, organize the cues in a (single) list, and provide a sidebar
to monitor and control running cues.

## How to use

### Live and Selection mode

List Layout can operate in two modes, "live" (the default), and "selection".

* In live mode only one cue will be highlighted, this is referred as "current cue". 
The list will scroll to keep the cue visible and centered.<br>
* Enabling selection mode allow to select multiple cues using the standard `[CTRL]` and `[SHIFT]` modifiers, 
the "current cue" will be the last selected.

Selection mode can be toggled via `Layout > Selection` or `[CTRL+SHIFT+E]`.

### Current cue

The current cue is highlighted by the left arrow icon and a different color:

```{image} _static/list_layout_current_cue.png
:alt: Linux Show Player - Current cue
:align: center
```

It can be played by using the `GO` button or `[Space]` (can be changed in the layout options).

To change the current cue, directional keys `⬆️` `⬇️` can be used to go up and down into the list,
alternatively you can click on the cue to make it the current one.

### Cues Editing

The setting dialog for a cue can be opened in two ways: `Right-Click > Edit cue`
or `Double-Click` the cue.

Cues can be selected/deselected with `Right-Click > Select`, `CTRL+Space` or
`CTRL+Click`

### Move and Copy Cues

* **Move:** cues can be moved with a simple `Drag&Drop`
* **Copy:** cues can be copied using `CTRL+Drag&Drop`

## Top Panel

* **Top left:** we can find the `GO` button, this will execute the current cue and move forward;
* **Top center:** name and description of the current cue are displayed here;
* **Top right:** a set of buttons that allow to stop, pause, restart, interrupt and fade all the cues.

## Left Panel

All the cues are shown here in a list-like view, the following column are shown:

* The first column show the current state of the cue<br>
    ![running](_static/icons/led-running.svg){.align-middle} Running<br>
    ![paused](_static/icons/led-pause.svg){.align-middle} Paused<br>
    ![error](_static/icons/led-error.svg){.align-middle} Error<br>
* **#:** The cue index
* **Cue:** The cue name
* **Pre wait:** Pre wait indicator
* **Action:** Cue time indicator
* **Post wait:** Post wait indicator
* The last column show an icon for the "next-action" (what should be done after "post wait")<br>
    ![running](_static/icons/cue-select-next.svg){.align-middle} Select next<br>
    ![paused](_static/icons/cue-trigger-next.svg){.align-middle} Trigger next<br>

### Right Panel

Running cues are shown here:

```{image} _static/list_layout_right_panel.png
:alt: Linux Show Player - Right panel
```

A set of buttons is provided to stop, pause/restart, interrupt and fade each cue,
when the action is supported.<br>
A seek-bar, showing the audio waveform, allow to change the current playing position.

## Layout Options

In the application settings (`File > Preferences`) various options are provided:

### Default behaviours

This can be changed per-show via the `Layout` menu.

* **Show dB-Meters:** show/hide the db-meters for running cues (right panel)
* **Show accurate time:** show/hide tens of seconds for running cues (right panel)
* **Show seek-bars:** show/hide seek bars for running cues (right panel)
* **Auto-select next cue:** if enabled the next cue will be selected automatically
* **Enable selection modo:** if enabled "selection" mode will be active by default

### Behaviours

* **Use waveform seek-bars:** if disabled a "plain" progress bar will be displayed instead of the audio waveform
* **Go key disabled while playing:** if enabled the `GO` keyboard shortcut will be ignored when some cue is playing
* **Go Key:** define up to 4 key-combinations that can be used to execute the current cue,
  to do so, double-click the edit-area, then enter your keys combinations
* **Go Action:** the action `GO` will trigger on the current cue

### Use fade

When disabled, the corresponding buttons on the top right panel will not execute a fades.


```{image}  _static/list_layout_settings.png
:alt: Linux Show Player - List Layout settings
:align: center
```