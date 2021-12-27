from PyQt5.QtWidgets import QTableWidgetItem

from typing import Dict, Tuple, List, Optional, Any

from plover import system
from plover.engine import StenoEngine
from plover.formatting import RetroFormatter
from plover.registry import registry
from plover.steno import Stroke
from plover.steno_dictionary import StenoDictionary, StenoDictionaryCollection
from plover.translation import Translation

from plover_word_tray.word_tray_ui import WordTrayUI
from plover_word_tray.sorting import SortingType, get_sorter, sort_suggestions


OUTLINE_TYPE = Tuple[str, ...]


def common_prefix(str_x: str, str_y: str) -> str:
    x_len = len(str_x)
    y_len = len(str_y)
    short_len = min(x_len, y_len)
    for index in range(short_len):
        if str_x[index] != str_y[index]:
            return str_x[:index]

    return str_x[:short_len]


class TranslationNode:
    def __init__(self, translation: str = "", tolerance: int = 1) -> None:
        self.translation = translation
        self.tolerance = tolerance

        # We use a dictionary here to manage translations that are
        # the same except for capitalization.
        self.min_length: Dict[str, int] = {}
        self.outlines: Dict[str, List[OUTLINE_TYPE]] = {}
        self.children: Dict[str, "TranslationNode"] = {}

    def add_outline(self, translation: str, outline: OUTLINE_TYPE) -> None:
        if not outline:
            return
        
        outline_len = len(outline)
        if translation not in self.min_length:
            self.min_length[translation] = outline_len
            self.outlines[translation] = [outline]
            return

        curr_min_len = self.min_length[translation]

        if outline_len <= curr_min_len + self.tolerance:
            self.outlines[translation].append(outline)

        if outline_len < self.min_length[translation]:
            self.min_length[translation] = curr_min_len

            new_max_len = curr_min_len + self.tolerance
            self.outlines[translation] = [
                ol for ol in self.outlines[translation]
                if len(ol) < new_max_len
            ]

    def add_child(self, translation: str, lower_tl: str, outline: OUTLINE_TYPE) -> None:
        if not outline:
            return

        if lower_tl == self.translation:
            self.add_outline(translation, outline)
            return

        if not self.children:
            new_node = TranslationNode(translation, self.tolerance)
            new_node.add_outline(translation, outline)
            self.children[lower_tl] = new_node
            return
        
        tl_len = len(self.translation)
        for key in self.children.keys():
            prefix = common_prefix(key, lower_tl)
            if len(prefix) > tl_len:
                if prefix == key:
                    self.children[key].add_child(translation, lower_tl, outline)
                else:
                    grandchild = self.children.pop(key)
                    new_child = TranslationNode(prefix, self.tolerance)
                    new_child.children[key] = grandchild
                    new_child.add_child(translation, lower_tl, outline)
                    self.children[prefix] = new_child

                return

        new_node = TranslationNode(lower_tl, self.tolerance)
        new_node.add_outline(translation, outline)
        self.children[lower_tl] = new_node

    def match_prefix(self, prefix: str) -> List[Tuple[str, OUTLINE_TYPE]]:
        suggestions_list = []
        
        if self.translation.startswith(prefix):
            suggestions_list = [(tl, ol) for tl, ols in self.outlines.items() for ol in ols]
        
        for key, node in self.children.items():
            if key.startswith(prefix):
                suggestions_list += node.match_prefix(prefix)

        return suggestions_list

    def get_node(self, prefix: str) -> "TranslationNode":
        if self.translation.startswith(prefix):
            return self

        for key, node in self.children.items():
            if prefix.startswith(key):
                return node.get_node(prefix)
        
        return self


class WordTraySuggestions(WordTrayUI):
    def __init__(self, engine: StenoEngine) -> None:
        super().__init__(engine)

        self._translate_tree = None
        self._suggestions: List[Tuple[str, OUTLINE_TYPE]] = []
        self._prev_node: Optional[TranslationNode] = None
        self._page = 0

        self._stroke_formatter: Optional[Callable[[STROKE_TYPE], STROKE_TYPE]] = None
        self._translation_formatter: Optional[Callable[[str], str]] = None
        self._system_sorter: Optional[Callable[[Tuple[OUTLINE_TYPE, str]], Any]] = None

        engine.signal_connect("stroked", self.on_stroke)
        engine.signal_connect("dictionaries_loaded", self.on_dict_update)
        engine.signal_connect("config_changed", self.on_config_changed)
        self.index_dictionaries()
        self.on_config_changed()

    def update_table(self) -> None:
        top_index = self._page * self.config.page_len

        page_count = (len(self._suggestions) - 1) // self.config.page_len + 1
        displayed = self._suggestions[top_index:top_index + self.config.page_len]
        display_len = len(displayed)

        for index, (translation, outline) in enumerate(displayed):
            self.suggestions_table.setItem(index, 0, QTableWidgetItem(translation))
            self.suggestions_table.setItem(index, 1, QTableWidgetItem("/".join(outline)))

        if display_len < self.config.page_len:
            for index in range(display_len, self.config.page_len):
                self.suggestions_table.setItem(index, 0, QTableWidgetItem(""))
                self.suggestions_table.setItem(index, 1, QTableWidgetItem(""))
        
        self.page_label.setText(f"Page {self._page + 1} of {page_count}")

    def on_stroke(self, _: tuple) -> None:
        update_suggestions = True

        if hasattr(self.engine._translator, "word_tray_state"):
            word_tray_state = self.engine._translator.word_tray_state
            max_pages = (len(self._suggestions) - 1) // self.config.page_len + 1

            if word_tray_state == "prev_page":
                self._page = (self._page - 1) % max_pages
                update_suggestions = False
            
            elif word_tray_state == "next_page":
                self._page = (self._page + 1) % max_pages
                update_suggestions = False
            
            elif word_tray_state == "word_tray_reload":
                self.index_dictionaries()
            
            self.engine._translator.word_tray_state = ""

        prev_translations: List[Translation] = self.engine.translator_state.prev()

        if not prev_translations:
            return

        retro_formatter: RetroFormatter = RetroFormatter(prev_translations)
        last_fragment: List[str] = retro_formatter.last_fragments()

        if not last_fragment:
            return

        curr_word: str = last_fragment[-1].strip()

        if prev_translations:
            last_translation = prev_translations[-1].english
            if last_translation is not None:
                if (
                    last_translation.replace(" ", "").isalnum()
                    and len(last_translation) > len(curr_word)
                ):
                    curr_word = last_translation.strip()

        if curr_word and update_suggestions:
            self.current_translation.setPlainText(curr_word)
            prefix = curr_word.lower()

            if (
                self._prev_node is not None 
                and prefix.startswith(self._prev_node.translation)
            ):
                tree_node = self._prev_node.get_node(prefix)
                raw_suggestions = tree_node.match_prefix(prefix)
            else:    
                tree_node = self._translate_tree.get_node(prefix)
                raw_suggestions = tree_node.match_prefix(prefix)

            queued_suggestions = sort_suggestions(
                suggestions=raw_suggestions,
                sorting_type=self.config.sorting_type,
                to_pseudo=self.config.to_pseudo,
                stroke_formatter=self._stroke_formatter,
                translation_formatter=self._translation_formatter,
                system_sorter=self._system_sorter
            )

            self._prev_node = tree_node
            self._suggestions = queued_suggestions
            self._page = 0
        
        self.update_table()
    
    def index_dictionaries(self) -> None:
        self._translate_tree = TranslationNode(tolerance=self.config.tolerance)
        dictionaries: StenoDictionaryCollection = self.engine.dictionaries

        dictionary: StenoDictionary
        for dictionary in dictionaries.dicts:
            if dictionary.enabled:
                for outline, translation in dictionary.items():
                    self._translate_tree.add_child(translation, translation.lower(), outline)

    def on_dict_update(self) -> None: 
        self.index_dictionaries()
    
    def on_config_changed(self) -> None:
        system_name = system.NAME
        system_mod = registry.get_plugin("system", system_name).obj

        self._stroke_formatter = getattr(system_mod, "WT_STROKE_FORMATTER", None)
        self._translation_formatter = getattr(system_mod, "WT_TRANSLATION_FORMATTER", None)
        self._system_sorter = getattr(system_mod, "WT_SORTER", None)
