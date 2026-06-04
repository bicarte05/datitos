from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QScrollArea, QFrame, QComboBox)
from PyQt6.QtCore import Qt
import sys
sys.path.insert(0, '..')
import database
import validadores


class ClientesCompletoView(QWidget):
    """Vista mejorada para registrar clientes con dirección completa."""
    
    def __init__(self):
        super().__init__()
        self.funcion_db = database.registrar_cliente_completo
        self.inputs = {}
        self.combos = {}
        
        # Cargar catálogos
        self.paises = database.obtener_paises()
        self.suscripciones = database.obtener_suscripciones()
        self.ciudades_por_pais = {}
        
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

        # SECCIÓN 1: DATOS PERSONALES
        lbl_seccion1 = QLabel("Datos Personales")
        lbl_seccion1.setStyleSheet("font-weight: bold; font-size: 12px; color: #0EA5E9; background-color: transparent;")
        form_layout.addWidget(lbl_seccion1)

        # Nombre
        lbl = QLabel("Nombre Completo")
        lbl.setStyleSheet("background-color: transparent;")
        form_layout.addWidget(lbl)
        input_nombre = QLineEdit(placeholderText="Ej: Juan Pérez")
        input_nombre.setMinimumHeight(36)
        self.inputs["Nombre"] = input_nombre
        form_layout.addWidget(input_nombre)

        # Email
        lbl = QLabel("Correo Electrónico")
        lbl.setStyleSheet("background-color: transparent;")
        lbl.setContentsMargins(0, 8, 0, 0)
        form_layout.addWidget(lbl)
        input_email = QLineEdit(placeholderText="usuario@ejemplo.com")
        input_email.setMinimumHeight(36)
        self.inputs["Email"] = input_email
        form_layout.addWidget(input_email)

        # Teléfono
        lbl = QLabel("Teléfono")
        lbl.setStyleSheet("background-color: transparent;")
        lbl.setContentsMargins(0, 8, 0, 0)
        form_layout.addWidget(lbl)
        input_telefono = QLineEdit(placeholderText="Ej: +56 9 1234 5678")
        input_telefono.setMinimumHeight(36)
        self.inputs["Telefono"] = input_telefono
        form_layout.addWidget(input_telefono)

        # Suscripción
        lbl = QLabel("Tipo de Suscripción (Opcional)")
        lbl.setStyleSheet("background-color: transparent;")
        lbl.setContentsMargins(0, 8, 0, 0)
        form_layout.addWidget(lbl)
        combo_suscripcion = QComboBox()
        combo_suscripcion.addItem("Sin suscripción", None)
        for id_sus, tipo, costo, desc in self.suscripciones:
            combo_suscripcion.addItem(f"{tipo} (${costo}/mes)", id_sus)
        combo_suscripcion.setMinimumHeight(36)
        self.combos["Suscripcion"] = combo_suscripcion
        form_layout.addWidget(combo_suscripcion)

        # SECCIÓN 2: DIRECCIÓN
        form_layout.addSpacing(12)
        lbl_seccion2 = QLabel("Dirección de Entrega")
        lbl_seccion2.setStyleSheet("font-weight: bold; font-size: 12px; color: #0EA5E9; background-color: transparent;")
        form_layout.addWidget(lbl_seccion2)

        # País
        lbl = QLabel("País")
        lbl.setStyleSheet("background-color: transparent;")
        form_layout.addWidget(lbl)
        combo_pais = QComboBox()
        combo_pais.addItem("Seleccionar país", None)
        for id_pais, nombre_pais in self.paises:
            combo_pais.addItem(nombre_pais, id_pais)
        combo_pais.currentIndexChanged.connect(self._actualizar_ciudades)
        combo_pais.setMinimumHeight(36)
        self.combos["Pais"] = combo_pais
        form_layout.addWidget(combo_pais)

        # Ciudad
        lbl = QLabel("Ciudad")
        lbl.setStyleSheet("background-color: transparent;")
        lbl.setContentsMargins(0, 8, 0, 0)
        form_layout.addWidget(lbl)
        combo_ciudad = QComboBox()
        combo_ciudad.addItem("Seleccionar ciudad", None)
        combo_ciudad.setMinimumHeight(36)
        self.combos["Ciudad"] = combo_ciudad
        form_layout.addWidget(combo_ciudad)

        # Calle
        lbl = QLabel("Calle/Avenida")
        lbl.setStyleSheet("background-color: transparent;")
        lbl.setContentsMargins(0, 8, 0, 0)
        form_layout.addWidget(lbl)
        input_calle = QLineEdit(placeholderText="Ej: Av. Ramón Picarte")
        input_calle.setMinimumHeight(36)
        self.inputs["Calle"] = input_calle
        form_layout.addWidget(input_calle)

        # Número
        lbl = QLabel("Número")
        lbl.setStyleSheet("background-color: transparent;")
        lbl.setContentsMargins(0, 8, 0, 0)
        form_layout.addWidget(lbl)
        input_numero = QLineEdit(placeholderText="Ej: 1234")
        input_numero.setMinimumHeight(36)
        self.inputs["Numero"] = input_numero
        form_layout.addWidget(input_numero)

        scroll.setWidget(form_widget)

        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(12)
        botones_layout.setContentsMargins(24, 12, 24, 24)

        btn_guardar = QPushButton("Guardar Cliente")
        btn_guardar.setMinimumHeight(40)
        btn_guardar.setMaximumHeight(40)
        btn_guardar.setMinimumWidth(120)
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

        botones_layout.addStretch()

        # Layout principal
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)
        outer.addLayout(botones_layout)
        self.setLayout(outer)

        # Estilos
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
        )

    def _actualizar_ciudades(self):
        """Actualiza las ciudades cuando cambia el país seleccionado."""
        id_pais = self.combos["Pais"].currentData()
        combo_ciudad = self.combos["Ciudad"]
        combo_ciudad.clear()
        combo_ciudad.addItem("Seleccionar ciudad", None)
        
        if id_pais:
            ciudades = database.obtener_ciudades(id_pais)
            for id_ciudad, nombre_ciudad in ciudades:
                combo_ciudad.addItem(nombre_ciudad, id_ciudad)

    def _limpiar_campos(self):
        """Limpia todos los campos."""
        for campo in self.inputs.values():
            campo.clear()
        for combo in self.combos.values():
            combo.setCurrentIndex(0)
        if self.inputs:
            next(iter(self.inputs.values())).setFocus()

    def _ejecutar_guardar(self):
        """Valida y guarda el cliente."""
        # Obtener valores de inputs
        nombre = self.inputs["Nombre"].text().strip()
        email = self.inputs["Email"].text().strip()
        telefono = self.inputs["Telefono"].text().strip()
        calle = self.inputs["Calle"].text().strip()
        numero = self.inputs["Numero"].text().strip()
        
        # Obtener valores de combos
        id_suscripcion = self.combos["Suscripcion"].currentData()
        id_ciudad = self.combos["Ciudad"].currentData()
        
        # Validar campos personales
        errores = []
        
        valido, msg = validadores.validar_nombre(nombre)
        if not valido:
            errores.append(f"• Nombre: {msg}")
        
        valido, msg = validadores.validar_email(email)
        if not valido:
            errores.append(f"• Email: {msg}")
        
        valido, msg = validadores.validar_telefono(telefono)
        if not valido:
            errores.append(f"• Teléfono: {msg}")
        
        # Validar dirección si se ingresó
        if calle:
            valido, msg = validadores.validar_direccion(calle)
            if not valido:
                errores.append(f"• Calle: {msg}")
            
            if not id_ciudad:
                errores.append("• Ciudad: Debe seleccionar una ciudad")
        
        if errores:
            QMessageBox.warning(self, "Datos inválidos", "\n".join(errores))
            return
        
        # Confirmar
        suscripcion_texto = self.combos['Suscripcion'].currentText()
        ciudad_texto = self.combos['Ciudad'].currentText()
        
        datos_resumen = f"""
Nombre: {nombre}
Email: {email}
Teléfono: {telefono}
Suscripción: {suscripcion_texto}
"""
        if calle:
            datos_resumen += f"Dirección: {calle} {numero}, {ciudad_texto}"
        
        respuesta = QMessageBox.question(
            self, "Confirmar ingreso",
            f"¿Guardar este cliente?{datos_resumen}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        # Guardar
        if self.funcion_db(nombre, email, telefono, id_suscripcion, calle, numero, id_ciudad):
            QMessageBox.information(self, "Guardado", "Cliente creado correctamente.")
            self._limpiar_campos()
        else:
            QMessageBox.critical(self, "Error",
                                 "No se pudo guardar el cliente.\n"
                                 "Revise los datos e intente nuevamente.")
