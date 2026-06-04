from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QScrollArea, QFrame)
from PyQt6.QtCore import Qt


class InsertarView(QWidget):
    def __init__(self, campos_dict: dict, funcion_db, titulo_boton: str = "Guardar"):
        super().__init__()
        self.funcion_db = funcion_db
        self.inputs: dict[str, QLineEdit] = {}

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # ASIGNAMOS NOMBRES (ID) PARA QUE LA TRANSPARENCIA NO AFECTE AL BOTÓN
        scroll.setObjectName("area_scroll")
        scroll.setStyleSheet("QScrollArea#area_scroll { background-color: transparent; }")
        
        viewport = scroll.viewport()
        viewport.setObjectName("viewport_scroll")
        viewport.setStyleSheet("QWidget#viewport_scroll { background-color: transparent; }")

        form_widget = QWidget()
        form_widget.setObjectName("contenedor_form")
        form_widget.setStyleSheet("QWidget#contenedor_form { background-color: transparent; }")
        
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setSpacing(4)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_widget.setLayout(form_layout)

        for i, (nombre_campo, placeholder) in enumerate(campos_dict.items()):
            lbl = QLabel(nombre_campo)
            lbl.setStyleSheet("background-color: transparent;")
            if i > 0:
                lbl.setContentsMargins(0, 12, 0, 0)
            form_layout.addWidget(lbl)

            input_field = QLineEdit(placeholderText=placeholder)
            input_field.setMinimumHeight(40)
            self.inputs[nombre_campo] = input_field
            form_layout.addWidget(input_field)

        btn = QPushButton(titulo_boton)
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._ejecutar_guardar)
        form_layout.addSpacing(8)
        form_layout.addWidget(btn)

        scroll.setWidget(form_widget)

        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        self.setLayout(outer)

    def _ejecutar_guardar(self) -> None:
        valores = [campo.text().strip() for campo in self.inputs.values()]
        if any(not v for v in valores):
            QMessageBox.warning(self, "Campos incompletos",
                                "Por favor, complete todos los campos antes de guardar.")
            return
        if self.funcion_db(*valores):
            QMessageBox.information(self, "Guardado", "Registro creado correctamente.")
            for campo in self.inputs.values():
                campo.clear()
            next(iter(self.inputs.values())).setFocus()
        else:
            QMessageBox.critical(self, "Error",
                                 "No se pudo guardar el registro.\n"
                                 "Revise los datos e intente nuevamente.")