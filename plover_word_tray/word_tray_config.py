from plover_word_tray.sorting import SortingType


CONFIG_ITEMS = {
    "to_pseudo": False,
    "tolerance": 1,
    "row_height": 30,
    "page_len": 10,
    "sorting_type": SortingType.LENGTH
}


class WordTrayConfig:
    def __init__(self, values: dict = None):
        if values is None:
            values = dict()

        for key, default in CONFIG_ITEMS.items():
            if key in values:
                setattr(self, key, values[key])
            else:
                setattr(self, key, default)

    def copy(self) -> "WordTrayConfig":
        value_dict = {k: getattr(self, k) for k in CONFIG_ITEMS.keys()}
        return WordTrayConfig(value_dict)
