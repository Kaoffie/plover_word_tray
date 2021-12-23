from PyQt5.QtWidgets import (
    QDialog, QWidget, QLabel, QSpinBox, QCheckBox,
    QComboBox, QDialogButtonBox, QGridLayout
)

from plover_word_tray.word_tray_config import WordTrayConfig
from plover_word_tray.sorting import SortingType, sorting_descriptions


class ConfigUI(QDialog):

    def __init__(self, temp_config: WordTrayConfig, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.temp_config = temp_config
        self.setup_window()

    def setup_window(self) -> None:
        self.resize(350, 200)

        self.to_pseudo_label = QLabel(self)
        self.to_pseudo_label.setText("Display Pseudosteno")

        self.to_pseudo_box = QCheckBox(self)
        self.to_pseudo_box.setChecked(self.temp_config.to_pseudo)

        self.tolerance_label = QLabel(self)
        self.tolerance_label.setText("Outline Length Tolerance")

        self.tolerance_box = QSpinBox(self)
        self.tolerance_box.setValue(self.temp_config.tolerance)
        self.tolerance_box.setRange(0, 5)

        self.row_height_label = QLabel(self)
        self.row_height_label.setText("Row Height")

        self.row_height_box = QSpinBox(self)
        self.row_height_box.setValue(self.temp_config.row_height)
        self.row_height_box.setRange(10, 100)

        self.page_len_label = QLabel(self)
        self.page_len_label.setText("List Length")
        
        self.page_len_box = QSpinBox(self)
        self.page_len_box.setValue(self.temp_config.page_len)
        self.page_len_box.setRange(1, 30)

        self.sorting_type_label = QLabel(self)
        self.sorting_type_label.setText("Display Order")

        self.sorting_type_box = QComboBox(self)
        self.sorting_type_box.addItems(sorting_descriptions)
        self.sorting_type_box.setCurrentIndex(self.temp_config.sorting_type.value)

        self.button_box = QDialogButtonBox(
            (
                QDialogButtonBox.Cancel | 
                QDialogButtonBox.Ok
            ),
            parent=self
        )
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.save_settings)

        self.layout = QGridLayout()
        self.layout.addWidget(self.to_pseudo_label, 0, 0)
        self.layout.addWidget(self.to_pseudo_box, 0, 1)
        self.layout.addWidget(self.tolerance_label, 1, 0)
        self.layout.addWidget(self.tolerance_box, 1, 1)
        self.layout.addWidget(self.row_height_label, 2, 0)
        self.layout.addWidget(self.row_height_box, 2, 1)
        self.layout.addWidget(self.page_len_label, 3, 0)
        self.layout.addWidget(self.page_len_box, 3, 1)
        self.layout.addWidget(self.sorting_type_label, 4, 0)
        self.layout.addWidget(self.sorting_type_box, 4, 1)
        self.layout.addWidget(self.button_box, 5, 0, 2, 1)
        self.setLayout(self.layout)

    def save_settings(self) -> None:
        self.temp_config.to_pseudo = self.to_pseudo_box.isChecked()
        self.temp_config.tolerance = self.tolerance_box.value()
        self.temp_config.row_height = self.row_height_box.value()
        self.temp_config.page_len = self.page_len_box.value()
        self.temp_config.sorting_type = SortingType(
            self.sorting_type_box.currentIndex()
        )
        
        self.accept()
