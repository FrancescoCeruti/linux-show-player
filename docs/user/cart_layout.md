# Cart Layout

```{image} _static/cart_layout_main_view.png
:alt: Linux Show Player - Cart Layout
:align: center
```

<br>
The Cart Layout organize all the cues in grid-like pages, cues are shown as
buttons, if the cue provides a duration, the current cue time is shown at the bottom.

## How to use

### Adding Pages

To add a new page you can use `Layout > Add page`, or `Layout > Add pages`,
to add multiple pages at once.

Pages will also be added automatically when needed.

### Removing Pages

To remove a page, select the page to be removed, then use `Layout > Remove current page`,
a confirmation dialog will be shown.

```{warning}
All cues in the page will be deleted.
```

### Moving between pages

Pages can be switched using the tab bar on top of the layout or directional keys.

### Renaming pages

It's possible to rename pages via `Double click` on the tab name.

### Cues Execution

A cue can be start/stopped by clicking on it.

Via `Right-Click` on the cue is also possible play, stop, or pause the cues explicitly.

### Cues Editing

The setting dialog for a cue can be opened in two ways: `Right-Click > Edit cue` or `SHIFT+Right-Click`.

Cues can be selected/deselected for multi-editing with `Right-Click > Select` or `CTRL+Left-Click`.

### Move and Copy Cues

Cues can be copied or moved (into free spaces) inside a page or between different pages:

* **Move:** cues can be moved with `SHIFT+Drag&Drop`
* **Copy:** cues can be copied with `CTRL+Drag&Drop`

to move/copy between pages, while dragging the cue, over the destination page.

## Options

In the application settings (`File > Preferences`) various options are provided:

* **Countdown mode:** when enabled the current cue time is displayed as a countdown
* **Show seek-bars:** when enabled a slider able to change the current playing position
  of media cues (for media cues)
* **Show dB-meters:** when enabled, a dB level indicator is shown (for supported cues)
* **Show accurate time:** when enabled the cue time is displayed including tens of seconds
* **Show volume:** when enabled a volume slider is shown (for supported cues)
* **Grid size:** define the number of rows & columns per page. (require to reload
  the session)

```{warning}
When the grid size is changed, cues will be visually shifted to keep their
logical positioning.
```

```{image} _static/cart_layout_settings.png
:alt: Linux Show Player - Cart Layout settings
:align: center
```

## Limitations

Given its non-sequential nature, Cart Layout does not support cues "next-action".
