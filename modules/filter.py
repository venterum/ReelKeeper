import sqlite3
from PyQt6.QtWidgets import (
    QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QCheckBox, QComboBox, 
    QLabel, QDoubleSpinBox, QSpinBox, QPushButton
)
from PyQt6 import uic

class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("resources/ui/filter.ui", self)
        self.typeCombo.setEnabled(False)
        self.genreCombo.setEnabled(False)
        self.ratingSpin.setEnabled(False)
        self.ratingSpinTo.setEnabled(False)
        self.yearFromSpin.setEnabled(False)
        self.yearUpToSpin.setEnabled(False)
        self.spinProgressFrom.setEnabled(False)
        self.spinProgressUpTo.setEnabled(False)

        self.checkBoxType.stateChanged.connect(self.toggle_type)
        self.checkBoxGenre.stateChanged.connect(self.toggle_genre)
        self.checkBoxRating.stateChanged.connect(self.toggle_rating)
        self.checkBoxYears.stateChanged.connect(self.toggle_years)
        self.checkBoxProgress.stateChanged.connect(self.toggle_progress)

        self.saveButton.clicked.connect(self.apply_filter)
        self.closeButton.clicked.connect(self.reject)

        self.populate_combobox(self.typeCombo, "types", "type_id", "type_name")
        self.populate_combobox(self.genreCombo, "genres", "genre_id", "genre_name")

        self.selected_filters = {}

    def toggle_type(self):
        self.typeCombo.setEnabled(self.checkBoxType.isChecked())

    def toggle_genre(self):
        self.genreCombo.setEnabled(self.checkBoxGenre.isChecked())

    def toggle_rating(self):
        enabled = self.checkBoxRating.isChecked()
        self.ratingSpin.setEnabled(enabled)
        self.ratingSpinTo.setEnabled(enabled)

    def toggle_years(self):
        enabled = self.checkBoxYears.isChecked()
        self.yearFromSpin.setEnabled(enabled)
        self.yearUpToSpin.setEnabled(enabled)

    def toggle_progress(self):
        enabled = self.checkBoxProgress.isChecked()
        self.spinProgressFrom.setEnabled(enabled)
        self.spinProgressUpTo.setEnabled(enabled)

    def populate_combobox(self, combobox, table, id_column, name_column):
        try:
            conn = sqlite3.connect("data/data.sqlite")
            cursor = conn.cursor()

            cursor.execute(f"SELECT {id_column}, {name_column} FROM {table}")
            items = cursor.fetchall()

            combobox.addItem("Любой", -1)
            for item_id, item_name in items:
                combobox.addItem(item_name, item_id)

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные из таблицы {table}: {str(e)}")

    def apply_filter(self):
        if self.checkBoxType.isChecked():
            selected_id = self.typeCombo.currentData()
            if selected_id != -1:
                self.selected_filters["type_id"] = selected_id

        if self.checkBoxGenre.isChecked():
            selected_id = self.genreCombo.currentData()
            if selected_id != -1:
                self.selected_filters["genre_id"] = selected_id

        if self.checkBoxRating.isChecked():
            self.selected_filters["rating"] = (
                self.ratingSpin.value(),
                self.ratingSpinTo.value()
            )

        if self.checkBoxYears.isChecked():
            self.selected_filters["years"] = (
                self.yearFromSpin.value(),
                self.yearUpToSpin.value()
            )

        if self.checkBoxProgress.isChecked():
            self.selected_filters["progress"] = (
                self.spinProgressFrom.value(),
                self.spinProgressUpTo.value()
            )

        if not self.selected_filters:
            QMessageBox.warning(self, "Внимание", "Вы не выбрали ни одного фильтра!")
            return

        self.accept()

    def get_filters(self):
        return self.selected_filters