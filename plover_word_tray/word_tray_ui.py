from PyQt5.QtWidgets import (
    QTableWidget, QGridLayout, 
    QHeaderView, QLabel, QPlainTextEdit, QAction, 
    QAbstractItemView
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QKeySequence

from plover.engine import StenoEngine
from plover.gui_qt.tool import Tool
from plover.gui_qt.utils import ToolBar

from plover_word_tray.resources_rc import *
from plover_word_tray.word_tray_config import WordTrayConfig
from plover_word_tray.config_ui import ConfigUI
from plover_word_tray.sorting import SortingType


class WordTrayUI(Tool):
    TITLE = "Word Tray"
    ICON = ":/word_tray/add_database.svg"
    ROLE = "word_tray"

    def __init__(self, engine: StenoEngine) -> None:
        super().__init__(engine)
        self.engine: StenoEngine = engine
        self.config = WordTrayConfig()
        self.restore_state()
        self.show_window()
        self.finished.connect(self.save_state)

    def _restore_state(self, settings: QSettings) -> None:
        if settings.contains("to_pseudo"):
            self.config.to_pseudo = settings.value("to_pseudo", type=bool)

        if settings.contains("show_both"):
            self.config.show_both = settings.value("show_both", type=bool)

        if settings.contains("tolerance"):
            self.config.tolerance = settings.value("tolerance", type=int)

        if settings.contains("row_height"):
            self.config.row_height = settings.value("row_height", type=int)
        
        self.prev_pin = False
        if settings.contains("pinned") and settings.value("pinned", type=bool):
            self.prev_pin = True
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        if settings.contains("page_len"):
            self.config.page_len = settings.value("page_len", type=int)
        
        if settings.contains("sorting_type"):
            self.config.sorting_type = SortingType(settings.value("sorting_type", type=int))
        
        if not settings.contains("geometry"):
            self.resize(260, 400)
        
    def _save_state(self, settings: QSettings) -> None:
        settings.setValue("to_pseudo", self.config.to_pseudo)
        settings.setValue("show_both", self.config.show_both)
        settings.setValue("tolerance", self.config.tolerance)
        settings.setValue("row_height", self.config.row_height)
        settings.setValue("pinned", self.pin_action.isChecked())
        settings.setValue("page_len", self.config.page_len)
        settings.setValue("sorting_type", self.config.sorting_type.value)

    def show_window(self) -> None:
        self.current_label = QLabel(self)
        self.current_label.setText("Current Word")

        self.current_translation = QPlainTextEdit(self)
        self.current_translation.setFixedHeight(30)
        self.current_translation.setLineWrapMode(True)
        self.current_translation.setReadOnly(True)
        self.current_translation.setPlainText("Awaiting Input")

        self.suggestions_label = QLabel(self)
        self.suggestions_label.setText("Suggestions")

        self.suggestions_table = QTableWidget(self)
        self.suggestions_table.setRowCount(self.config.page_len)
        self.suggestions_table.setColumnCount(2)
        self.suggestions_table.verticalHeader().setDefaultSectionSize(self.config.row_height)
        self.suggestions_table.setMinimumHeight(self.config.row_height * self.config.page_len + self.config.row_height)
        self.suggestions_table.setAlternatingRowColors(True)
        self.suggestions_table.horizontalHeader().hide()
        self.suggestions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.suggestions_table.verticalHeader().hide()
        self.suggestions_table.setShowGrid(False)
        self.suggestions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.pin_action = QAction(self)
        self.pin_action.setCheckable(True)
        self.pin_action.setChecked(self.prev_pin)
        self.pin_action.setText("Pin window")
        self.pin_action.setToolTip("Keep Word Tray on top.")
        self.pin_action.setIcon(QIcon(":/word_tray/pin.svg"))
        self.pin_action.triggered.connect(self.on_toggle_pin)
        self.pin_action.setShortcut(QKeySequence("Ctrl+P"))

        self.settings_action = QAction(self)
        self.settings_action.setText("Word Tray settings")
        self.settings_action.setText("Configure Word Tray.")
        self.settings_action.setIcon(QIcon(":/word_tray/settings.svg"))
        self.settings_action.triggered.connect(self.on_settings)
        self.settings_action.setShortcut(QKeySequence("Ctrl+S"))

        self.page_label = QLabel(self)
        self.page_label.setText("Page 0 of 0")
        self.page_label.setAlignment(Qt.AlignHCenter)

        self.layout = QGridLayout()
        self.layout.addWidget(self.current_label, 0, 0, 1, 2)
        self.layout.addWidget(self.current_translation, 1, 0, 1, 2)
        self.layout.addWidget(self.suggestions_label, 2, 0, 1, 2)
        self.layout.addWidget(self.suggestions_table, 3, 0, 1, 2)
        self.layout.addWidget(ToolBar(
            self.pin_action,
            self.settings_action
        ), 4, 0)
        self.layout.addWidget(self.page_label, 4, 1)
        self.setLayout(self.layout)

        self.show()
    
    def on_toggle_pin(self, _: bool = False) -> None:
        flags = self.windowFlags()

        if self.pin_action.isChecked():
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.show()

    def on_settings(self, *args) -> None:
        config_dialog = ConfigUI(self.config.copy(), self)
        if config_dialog.exec():
            self.config = config_dialog.temp_config
            self.suggestions_table.setRowCount(self.config.page_len)
            self.suggestions_table.setColumnCount(2 + (self.config.to_pseudo and self.config.show_both) * 1)
            self.suggestions_table.verticalHeader().setDefaultSectionSize(self.config.row_height)
            self.suggestions_table.setMinimumHeight(self.config.row_height * self.config.page_len + self.config.row_height)

    def get_word_tray_config(self) -> WordTrayConfig:
        return self.config
