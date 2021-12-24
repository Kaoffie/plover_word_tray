# Word Tray for Plover
[![PyPI](https://img.shields.io/pypi/v/plover-word-tray)](https://pypi.org/project/plover-word-tray/)
![GitHub](https://img.shields.io/github/license/Kaoffie/plover_word_tray)

**Word Tray** is a GUI plugin that automatically looks up efficient outlines for words that start with the current input, much like autocomplete suggestions. It is heavily inspired by [**StenoTray**](https://github.com/brentn/StenoTray), which was a widget made before Plover's plugin system was implemented.

![](https://user-images.githubusercontent.com/30435273/147299721-5c1727ce-4536-4636-9f2a-4c668d9296fe.png)

## Installation

This plugin isn't on the Plover Plugin Registry yet; install it with the following command:

```
plover -s plover_plugins install plover_word_tray
```

Alternatively, if you are on Windows, locate the directory where Plover.exe is located in and install using the following command:

```
.\plover_console.exe -s plover_plugins install plover_word_tray
```

## Usage Notes

### Pseudosteno & Tolerance

In the settings page, you may turn on **Display Pseudosteno** to show hidden sounds in the list of outlines, such as `PLOFR` instead of `PHROFR`.

**Tolerance** determines the maximum outline length above the minimum length the widget will list. For instance, if the minimum number of strokes required to stroke the word "sample" is 2, setting `Tolerance = 3` will display all outlines with 2 to 5 strokes.

### Macro Strokes & Shortcuts

To scroll between pages in the widget, you may use the following dictionary definitions. Note that these don't come with the plugin itself and you'll have to add them manually! Feel free to use the recommended strokes, or don't.

| Action             | Dictionary Definition | Recommended Stroke |
|--------------------|-----------------------|--------------------|
| Next Page          | `=wt_next_page`       | `#-GS`             |
| Previous Page      | `=wt_prev_page`       | `#-RB`             |
| Reload Suggestions | `=wt_reload`          | `#-RBGS`           |

The plugin keeps an internal copy of your dictionaries to load suggestions faster. If you edit the dictionaries, this plugin might not respond immediately; you may force it to reload using the Reload Suggestions stroke.

### Display Order Types

| Display Order | Explanation |
|---|---|
| Length | Order by shortest word first |
| Frequency | Order by most frequent word first, if the current system provides a frequency table. |
| Stroke Count | Order by lowest stroke count first. |
| Alphabetical | Order by translation alphabetically. |
| System Defined | Order defined by the system. The default English stenotype system doesn't have a defined display order. Defaults to Length. |

### System-defined functions

If you're designing a language system for Plover and you'd like to customize the display order and format, you may do so by including these functions in your system file:

```py
def WT_STROKE_FORMATTER(stroke: str) -> str:
    """Formats single strokes, such as STROEBG"""
    return ...

def WT_TRANSLATION_FORMATTER(translation: str) -> str:
    """Formats the translated string, such as 'stroke'"""
    return ...

def WT_SORTER(entry: Tuple[str, Tuple[str, ...]]) -> int:
    """
    Scores translation-outline pairs, such as ("translate", ("TRAPBS", "HRAEUT"))
    Note that the order of the tuples here are reversed from plover-next-stroke.

    Pairs are ordered from smallest to biggest;
    it need not be an int - anything that can be compared
    works, including strings or tuples of ints.
    """
    outline, translation = entry
    return ...
```

All suggestions will be run through the two formatters (if available) before being sorted. If the user chooses to turn on pseudosteno formatting, the pseudo conversion will happen first before that is passed to the sorter. The sorter will only be used if the user changes their display order to "System Defined".

## License & Credits

This plugin is licensed under the MIT license.

The icons used in this plugin are taken from [Icons8 Flat Color Icons](https://github.com/icons8/flat-color-icons).

Much of the UI in this plugin is taken from the [Plover Next Stroke](https://github.com/Kaoffie/plover_next_stroke) plugin.

Of course, it goes without saying that this plugin owes its existence to the original [StenoTray](https://github.com/brentn/StenoTray), made by [@brentn](https://github.com/brentn), with contributions from [@Mqrius](https://github.com/Mqrius), [@morinted](https://github.com/morinted), [@seebs](https://github.com/seebs), and [@David-Allison](https://github.com/David-Allison).