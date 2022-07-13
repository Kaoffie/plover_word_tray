from enum import Enum
from typing import Tuple, Union, Callable, Any, List, Optional

from plover import system

from plover_word_tray.pseudo import format_pseudo


OUTLINE_TYPE = Tuple[str, ...]


class SortingType(Enum):
    LENGTH = 0
    FREQUENCY = 1
    STROKE_COUNT = 2
    ALPHABETICAL = 3
    SYSTEM_DEFINED = 4


sorting_descriptions = [
    "Length",
    "Frequency",
    "Stroke Count",
    "Alphabetical",
    "System Defined"
]


def to_int(string: str, default: int) -> int:
    try:
        return int(string)
    except ValueError:
        return default


def get_sorter(
    sorting_type: SortingType, 
    last_outline: Tuple[str, ...]
) -> Callable[[Tuple[str, OUTLINE_TYPE]], Any]:
    if sorting_type == SortingType.FREQUENCY:
        if system.ORTHOGRAPHY_WORDS is not None:
            return lambda s: (
                system.ORTHOGRAPHY_WORDS.get(s[0], 999999), 
                s[1] != last_outline, 
                len(s[1])
            )
        else:
            return lambda s: (
                len(s[0]), 
                s[1] != last_outline,
                s[0], 
                len(s[1]), 
                s[1]
            )

    elif sorting_type == SortingType.STROKE_COUNT:
        return lambda s: (
            len(s[1]), 
            s[1] != last_outline,
            s[1], 
            len(s[0]), 
            s[0]
        )

    elif sorting_type == SortingType.ALPHABETICAL:
        return lambda s: (
            s[0].lower(), 
            s[1] != last_outline,
            len(s[1]), 
            s[1]
        )

    return lambda s: (
        len(s[0]), 
        s[1] != last_outline,
        s[0], 
        len(s[1]), 
        s[1]
    )


def sort_suggestions(
    suggestions: List[Tuple[str, OUTLINE_TYPE]], 
    sorting_type: SortingType,
    to_pseudo: bool,
    last_outline: Tuple[str, ...],
    stroke_formatter: Optional[Callable[[str], str]] = None,
    translation_formatter: Optional[Callable[[str], str]] = None,
    system_sorter: Optional[Callable[[Tuple[str, Tuple[str, ...]]], Any]] = None,
) -> List[Tuple[str, OUTLINE_TYPE]]:
    formatted_sgns = []
    for translation, raw_outline in suggestions:
        if stroke_formatter is not None:
            raw_outline = tuple(stroke_formatter(s) for s in raw_outline)
        if translation_formatter is not None:
            translation = translation_formatter(translation)
        
        formatted_sgns.append((translation, raw_outline))
    
    sorted_sgns = []
    if sorting_type == SortingType.SYSTEM_DEFINED:
        if system_sorter is not None:
            sorted_sgns = sorted(formatted_sgns, key=system_sorter)
        
        sorting_type = SortingType.LENGTH
    
    if formatted_sgns and not sorted_sgns:
        sorted_sgns = sorted(formatted_sgns, key=get_sorter(sorting_type, last_outline))

    with_pseudo = []
    for translation, raw_outline in sorted_sgns:
        if to_pseudo:
            pseudo_outline = format_pseudo(raw_outline, translation)
        else:
            pseudo_outline = ""
        
        with_pseudo.append((translation, raw_outline, pseudo_outline))
    
    return with_pseudo
