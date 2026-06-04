from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QFrame)
from PyQt6.QtCore import Qt


class ListarView(QWidget):
    def __init__(self, cabeceras: list[str], funcion_db):
        super().__init__()
        self.funcion_db = funcion_db

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        barra = QHBoxLayout()
        self.lbl_contador = QLabel("Cargando…")
        self.lbl_contador.setStyleSheet(
            "font-size: 12px; color: #64748B; background-color: transparent;"
        )
        btn_refresh = QPushButton("↻  Actualizar")
        btn_refresh.setFixedWidth(130)
        btn_refresh.setMinimumHeight(36)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self._refrescar)
        barra.addWidget(self.lbl_contador)
        barra.addStretch()
        barra.addWidget(btn_refresh)
        layout.addLayout(barra)

        self.tabla = QTableWidget(0, len(cabeceras))
        self.tabla.setHorizontalHeaderLabels(cabeceras)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet(
            "QTableWidget { alternate-background-color: #F8FAFC; background-color: #FFFFFF; }"
        )
        self.tabla.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self._refrescar()

    def _refrescar(self) -> None:
        self.tabla.setRowCount(0)
        datos = self.funcion_db()
        for fila in datos:
            pos = self.tabla.rowCount()
            self.tabla.insertRow(pos)
            for col, val in enumerate(fila):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.tabla.setItem(pos, col, item)
        cantidad = self.tabla.rowCount()
        self.lbl_contador.setText(
            f"{cantidad} registro{'s' if cantidad != 1 else ''} encontrado{'s' if cantidad != 1 else ''}"
        )