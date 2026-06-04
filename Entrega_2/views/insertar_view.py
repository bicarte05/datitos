from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QScrollArea, QFrame)
from PyQt6.QtCore import Qt
import sys
sys.path.insert(0, '..')
import validadores


class InsertarView(QWidget):
    def __init__(self, campos_dict: dict, funcion_db, titulo_boton: str = "Guardar"):
        super().__init__()
        self.funcion_db = funcion_db
        self.inputs: dict[str, QLineEdit] = {}

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background-color: transparent;")
        scroll.viewport().setStyleSheet("background-color: transparent;")

        form_widget = QWidget()
        form_widget.setStyleSheet("background-color: transparent;")
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setSpacing(2)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_widget.setLayout(form_layout)

        for i, (nombre_campo, placeholder) in enumerate(campos_dict.items()):
            lbl = QLabel(nombre_campo)
            lbl.setStyleSheet("background-color: transparent;")
            if i > 0:
                lbl.setContentsMargins(0, 8, 0, 0)
            form_layout.addWidget(lbl)

            input_field = QLineEdit(placeholderText=placeholder)
            input_field.setMinimumHeight(36)
            input_field.setMaximumHeight(36)
            self.inputs[nombre_campo] = input_field
            form_layout.addWidget(input_field)

        scroll.setWidget(form_widget)

        # Contenedor para los botones en fila (FUERA del scroll)
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(12)
        botones_layout.setContentsMargins(24, 12, 24, 24)

        btn_guardar = QPushButton(titulo_boton)
        btn_guardar.setMinimumHeight(40)
        btn_guardar.setMaximumHeight(40)
        btn_guardar.setMinimumWidth(100)
        btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guardar.setObjectName("btn_guardar")
        btn_guardar.clicked.connect(self._ejecutar_guardar)
        botones_layout.addWidget(btn_guardar)

        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setMinimumHeight(40)
        btn_limpiar.setMaximumHeight(40)
        btn_limpiar.setMinimumWidth(100)
        btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpiar.setObjectName("btn_limpiar")
        btn_limpiar.clicked.connect(self._limpiar_campos)
        botones_layout.addWidget(btn_limpiar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(40)
        btn_cancelar.setMaximumHeight(40)
        btn_cancelar.setMinimumWidth(100)
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setObjectName("btn_cancelar")
        btn_cancelar.clicked.connect(self._cancelar)
        botones_layout.addWidget(btn_cancelar)

        botones_layout.addStretch()

        # Layout principal: scroll arriba, botones abajo
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)
        outer.addLayout(botones_layout)
        self.setLayout(outer)

        # Estilos CSS para los botones
        self.setStyleSheet(
            "QPushButton#btn_guardar {"
            "  background-color: #0EA5E9;"
            "  border-radius: 7px;"
            "  color: #FFFFFF;"
            "  font-weight: 700;"
            "  font-size: 13px;"
            "}"
            "QPushButton#btn_guardar:hover   { background-color: #0284C7; }"
            "QPushButton#btn_guardar:pressed { background-color: #0369A1; }"
            "QPushButton#btn_limpiar {"
            "  background-color: #94A3B8;"
            "  border-radius: 7px;"
            "  color: #FFFFFF;"
            "  font-weight: 700;"
            "  font-size: 13px;"
            "}"
            "QPushButton#btn_limpiar:hover   { background-color: #64748B; }"
            "QPushButton#btn_limpiar:pressed { background-color: #475569; }"
            "QPushButton#btn_cancelar {"
            "  background-color: #EF4444;"
            "  border-radius: 7px;"
            "  color: #FFFFFF;"
            "  font-weight: 700;"
            "  font-size: 13px;"
            "}"
            "QPushButton#btn_cancelar:hover   { background-color: #DC2626; }"
            "QPushButton#btn_cancelar:pressed { background-color: #B91C1C; }"
        )

    def _ejecutar_guardar(self) -> None:
        valores = [campo.text().strip() for campo in self.inputs.values()]
        campos_nombres = list(self.inputs.keys())
        
        # Validar que no estén vacíos
        if any(not v for v in valores):
            QMessageBox.warning(self, "Campos incompletos",
                                "Por favor, complete todos los campos antes de guardar.")
            return
        
        # Validaciones específicas según el tipo de formulario
        errores = self._validar_campos(campos_nombres, valores)
        if errores:
            QMessageBox.warning(self, "Datos inválidos", "\n".join(errores))
            return
        
        # Crear mensaje de confirmación con los datos ingresados
        datos_resumen = "\n".join(f"{nombre}: {valor}" for nombre, valor in zip(campos_nombres, valores))
        
        respuesta = QMessageBox.question(
            self, "Confirmar ingreso",
            f"¿Está seguro de que desea guardar estos datos?\n\n{datos_resumen}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
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
    
    def _validar_campos(self, campos_nombres: list, valores: list) -> list:
        """
        Valida los campos según su tipo.
        Retorna: lista de mensajes de error (vacía si todo es válido)
        """
        errores = []
        
        for nombre, valor in zip(campos_nombres, valores):
            nombre_lower = nombre.lower()
            
            # Validaciones para Nombre
            if "nombre" in nombre_lower:
                valido, msg = validadores.validar_nombre(valor)
                if not valido:
                    errores.append(f"• {nombre}: {msg}")
            
            # Validaciones para Email
            elif "email" in nombre_lower or "correo" in nombre_lower:
                valido, msg = validadores.validar_email(valor)
                if not valido:
                    errores.append(f"• {nombre}: {msg}")
            
            # Validaciones para Teléfono
            elif "telefono" in nombre_lower or "teléfono" in nombre_lower:
                valido, msg = validadores.validar_telefono(valor)
                if not valido:
                    errores.append(f"• {nombre}: {msg}")
            
            # Validaciones para Dirección
            elif "direccion" in nombre_lower or "dirección" in nombre_lower:
                valido, msg = validadores.validar_direccion(valor)
                if not valido:
                    errores.append(f"• {nombre}: {msg}")
            
            # Validaciones para Rubro
            elif "rubro" in nombre_lower:
                valido, msg = validadores.validar_rubro(valor)
                if not valido:
                    errores.append(f"• {nombre}: {msg}")
            
            # Validaciones para números (total, costo, etc)
            elif any(x in nombre_lower for x in ["total", "costo", "precio"]):
                valido, msg = validadores.validar_numero_positivo(valor, nombre)
                if not valido:
                    errores.append(f"• {msg}")
        
        return errores

    def _limpiar_campos(self) -> None:
        hay_datos = any(campo.text().strip() for campo in self.inputs.values())
        if hay_datos:
            respuesta = QMessageBox.question(
                self, "Confirmar limpieza",
                "¿Está seguro de que desea limpiar todos los campos?\n"
                "Los datos ingresados se perderán.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if respuesta != QMessageBox.StandardButton.Yes:
                return
        for campo in self.inputs.values():
            campo.clear()
        next(iter(self.inputs.values())).setFocus()

    def _cancelar(self) -> None:
        self._limpiar_campos()