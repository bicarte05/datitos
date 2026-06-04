from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt


class EliminarView(QWidget):
    def __init__(self, label_texto: str, placeholder: str, funcion_db):
        super().__init__()
        self.funcion_db = funcion_db

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(4)

        lbl = QLabel(label_texto)
        self.input_id = QLineEdit(placeholderText=placeholder)
        self.input_id.setMinimumHeight(40)

        layout.addWidget(lbl)
        layout.addWidget(self.input_id)
        layout.addSpacing(8)

        btn = QPushButton("Eliminar Registro")
        btn.setMinimumHeight(44)
        btn.setObjectName("btn_eliminar")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._ejecutar_eliminar)
        layout.addWidget(btn)

        advertencia = QLabel("⚠  Esta acción no se puede deshacer.")
        # background-color: transparent es clave — sin esto hereda el fondo
        # del QWidget padre que puede ser blanco o gris según el contexto.
        advertencia.setStyleSheet(
            "color: #EF4444; font-size: 11px; margin-top: 6px;"
            "background-color: transparent;"
        )
        layout.addWidget(advertencia)

        self.setLayout(layout)

        # Pseudo-estados (:hover, :pressed) solo funcionan en el stylesheet
        # del widget PADRE, no en el del propio botón.
        self.setStyleSheet(
            "QPushButton#btn_eliminar {"
            "  background-color: #EF4444;"
            "  border-radius: 7px;"
            "  color: #FFFFFF;"
            "  font-weight: 700;"
            "  font-size: 13px;"
            "}"
            "QPushButton#btn_eliminar:hover   { background-color: #DC2626; }"
            "QPushButton#btn_eliminar:pressed { background-color: #B91C1C; }"
        )

    def _ejecutar_eliminar(self) -> None:
        valor_id = self.input_id.text().strip()
        if not valor_id:
            QMessageBox.warning(self, "Campo vacío",
                                "Ingrese el identificador del registro a eliminar.")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar el registro «{valor_id}»?\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if self.funcion_db(valor_id):
            QMessageBox.information(self, "Eliminado",
                                    "El registro fue eliminado correctamente.")
            self.input_id.clear()
        else:
            QMessageBox.critical(self, "Error al eliminar",
                                 "No se pudo eliminar el registro.\n"
                                 "Verifique que exista y no tenga dependencias activas.")