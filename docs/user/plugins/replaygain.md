# ReplayGain & Normalization

This plugin provide a simple utility to calculate the
<a href="https://en.wikipedia.org/wiki/Audio_normalization" target="_blank">normalized</a> or 
<a href="https://en.wikipedia.org/wiki/ReplayGain" target="_blank">ReplayGain</a> volume for media cues.

The values are used as *Normalized Volume* for the [`Volume`](../cues/media_cues.md#volume) element.

```{note}
If a ReplayGain value is already stored in the file metadata (e.g. ID3 tags), it will be used.

The original files are left untouched.
```

## How to use

Via `Tools > ReplayGain / Normalization` menu the following options are provided:

* **Calculate**: Open a dialog to start the calculation
* **Reset all**: Reset to 0dB the normalized volumes of all cues
* **Reset selected**: Reset to 0dB the normalized volumes, only for the selected cues

### Calculate

```{image} ../_static/replaygain_dialog.png
:alt: ReplayGain
```

* **ReplayGain to:** Apply ReplayGain normalization, using the reference value in dB SPL (89 is the standard default)
* **Normalize to:** Use a simple normalization to the reference value in dB (0 is the maximum value)
* **Apply only to selected media:** apply only to the currently selected cues
* **Threads number:** Number of concurrent/parallel calculations (defaults to the available cores)

```{note}
The the process may require some time, depending on your CPU, number and size of the files involved.
```
