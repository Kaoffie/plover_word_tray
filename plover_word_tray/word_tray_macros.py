from plover.translation import Translator
from plover.steno import Stroke


def prev_page(translator: Translator, stroke: Stroke, argument: str):
    translator.word_tray_state = "prev_page"


def next_page(translator: Translator, stroke: Stroke, argument: str):
    translator.word_tray_state = "next_page"


def word_tray_reload(translator: Translator, stroke: Stroke, argument: str):
    translator.word_tray_state = "word_tray_reload"
