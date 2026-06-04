from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QScrollArea, QFrame, QComboBox, 
                             QTableWidget, QTableWidgetItem, QSpinBox)
from PyQt6.QtCore import Qt
import sys
sys.path.insert(0, '..')
import database
import validadores


class PedidosCompletoView(QWidget):
    """Vista mejorada para registrar pedidos con cliente, comercio y productos."""
    
    def __init__(self):
        super().__init__()
        self.clientes = database.obtener_clientes()
        self.comercios = database.obtener_comercios()
        self.productos_actuales = []
        self.detalles_pedido = []  # Lista de (id_producto, cantidad, precio_unitario, nombre)
        
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

        # SECCIÓN 1: CLIENTE Y COMERCIO
        lbl_seccion1 = QLabel("Seleccionar Cliente y Comercio")
        lbl_seccion1.setStyleSheet("font-weight: bold; font-size: 12px; color: #0EA5E9; background-color: transparent;")
        form_layout.addWidget(lbl_seccion1)

        # Cliente
        lbl = QLabel("Cliente")
        lbl.setStyleSheet("background-color: transparent;")
        form_layout.addWidget(lbl)
        combo_cliente = QComboBox()
        combo_cliente.addItem("Seleccionar cliente", None)
        for id_cli, nombre, email, telefono in self.clientes:
            combo_cliente.addItem(f"{nombre} ({email})", id_cli)
        combo_cliente.currentIndexChanged.connect(self._on_cliente_changed)
        combo_cliente.setMinimumHeight(36)
        self.combo_cliente = combo_cliente
        form_layout.addWidget(combo_cliente)

        # Comercio
        lbl = QLabel("Comercio")
        lbl.setStyleSheet("background-color: transparent;")
        lbl.setContentsMargins(0, 8, 0, 0)
        form_layout.addWidget(lbl)
        combo_comercio = QComboBox()
        combo_comercio.addItem("Seleccionar comercio", None)
        # Cargar todos los comercios desde la BD
        for id_com, nombre, direccion, rubro, id_ciudad in self.comercios:
            combo_comercio.addItem(f"{nombre} ({rubro})", id_com)
        combo_comercio.setEnabled(False)
        combo_comercio.currentIndexChanged.connect(self._on_comercio_changed)
        combo_comercio.setMinimumHeight(36)
        self.combo_comercio = combo_comercio
        form_layout.addWidget(combo_comercio)

        # SECCIÓN 2: PRODUCTOS
        form_layout.addSpacing(12)
        lbl_seccion2 = QLabel("Productos del Comercio")
        lbl_seccion2.setStyleSheet("font-weight: bold; font-size: 12px; color: #0EA5E9; background-color: transparent;")
        form_layout.addWidget(lbl_seccion2)

        # Tabla de productos disponibles
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(["Producto", "Precio", "Cantidad", "Subtotal", "Agregar"])
        self.tabla_productos.setMinimumHeight(200)
        self.tabla_productos.setEnabled(False)
        form_layout.addWidget(self.tabla_productos)

        # SECCIÓN 3: CARRITO/DETALLES DEL PEDIDO
        form_layout.addSpacing(12)
        lbl_seccion3 = QLabel("Items del Pedido")
        lbl_seccion3.setStyleSheet("font-weight: bold; font-size: 12px; color: #0EA5E9; background-color: transparent;")
        form_layout.addWidget(lbl_seccion3)

        # Tabla de items añadidos
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(["Producto", "Precio Unit.", "Cantidad", "Subtotal", "Quitar"])
        self.tabla_carrito.setMinimumHeight(150)
        form_layout.addWidget(self.tabla_carrito)

        # Total
        layout_total = QHBoxLayout()
        layout_total.addStretch()
        lbl_total = QLabel("Total Pedido:")
        lbl_total.setStyleSheet("font-weight: bold; background-color: transparent;")
        self.lbl_total_valor = QLineEdit("$0.00")
        self.lbl_total_valor.setReadOnly(True)
        self.lbl_total_valor.setMaximumWidth(150)
        layout_total.addWidget(lbl_total)
        layout_total.addWidget(self.lbl_total_valor)
        form_layout.addLayout(layout_total)

        scroll.setWidget(form_widget)

        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(12)
        botones_layout.setContentsMargins(24, 12, 24, 24)

        btn_guardar = QPushButton("Crear Pedido")
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
        btn_limpiar.clicked.connect(self._limpiar)
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

    def _on_cliente_changed(self):
        """Cuando cambia el cliente, habilita comercios pero limpia los productos."""
        id_cliente = self.combo_cliente.currentData()
        self.combo_comercio.setEnabled(id_cliente is not None)
        self.combo_comercio.setCurrentIndex(0)
        self.tabla_productos.setRowCount(0)
        self.tabla_carrito.setRowCount(0)
        self.detalles_pedido = []
        self._actualizar_total()

    def _on_comercio_changed(self):
        """Cuando cambia el comercio, carga los productos."""
        id_comercio = self.combo_comercio.currentData()
        self.tabla_productos.setRowCount(0)
        self.tabla_carrito.setRowCount(0)
        self.detalles_pedido = []
        self._actualizar_total()
        
        if id_comercio:
            self.productos_actuales = database.obtener_productos_por_comercio(id_comercio)
            self._cargar_tabla_productos()
            self.tabla_productos.setEnabled(True)
        else:
            self.tabla_productos.setEnabled(False)
            self.productos_actuales = []

    def _cargar_tabla_productos(self):
        """Carga los productos en la tabla."""
        self.tabla_productos.setRowCount(len(self.productos_actuales))
        
        for row, (id_prod, nombre, desc, precio) in enumerate(self.productos_actuales):
            # Producto
            item_nombre = QTableWidgetItem(f"{nombre}")
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_productos.setItem(row, 0, item_nombre)
            
            # Precio
            item_precio = QTableWidgetItem(f"${precio:.2f}")
            item_precio.setFlags(item_precio.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_productos.setItem(row, 1, item_precio)
            
            # Cantidad (SpinBox)
            spin = QSpinBox()
            spin.setMinimum(0)
            spin.setMaximum(100)
            spin.setValue(0)
            self.tabla_productos.setCellWidget(row, 2, spin)
            
            # Subtotal
            item_subtotal = QTableWidgetItem("$0.00")
            item_subtotal.setFlags(item_subtotal.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_productos.setItem(row, 3, item_subtotal)
            
            # Botón Agregar
            btn_agregar = QPushButton("Agregar")
            btn_agregar.clicked.connect(lambda checked, r=row: self._agregar_producto(r))
            self.tabla_productos.setCellWidget(row, 4, btn_agregar)

    def _agregar_producto(self, row: int):
        """Agrega un producto al carrito desde la tabla de productos."""
        spin = self.tabla_productos.cellWidget(row, 2)
        cantidad = spin.value()
        
        if cantidad <= 0:
            QMessageBox.warning(self, "Cantidad inválida", "Ingrese una cantidad mayor a 0.")
            return
        
        id_prod, nombre, desc, precio = self.productos_actuales[row]
        
        # Buscar si ya existe en el carrito
        encontrado = False
        for i, (prod_id, cant, p_unit, prod_nombre) in enumerate(self.detalles_pedido):
            if prod_id == id_prod:
                # Actualizar cantidad
                self.detalles_pedido[i] = (prod_id, cant + cantidad, p_unit, prod_nombre)
                encontrado = True
                break
        
        if not encontrado:
            self.detalles_pedido.append((id_prod, cantidad, precio, nombre))
        
        spin.setValue(0)
        self._cargar_tabla_carrito()
        self._actualizar_total()

    def _cargar_tabla_carrito(self):
        """Carga los items del carrito."""
        self.tabla_carrito.setRowCount(len(self.detalles_pedido))
        
        for row, (id_prod, cantidad, precio_unit, nombre) in enumerate(self.detalles_pedido):
            subtotal = cantidad * precio_unit
            
            # Producto
            item_nombre = QTableWidgetItem(nombre)
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_carrito.setItem(row, 0, item_nombre)
            
            # Precio unitario
            item_precio = QTableWidgetItem(f"${precio_unit:.2f}")
            item_precio.setFlags(item_precio.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_carrito.setItem(row, 1, item_precio)
            
            # Cantidad (SpinBox editable)
            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(100)
            spin.setValue(cantidad)
            spin.valueChanged.connect(lambda val, r=row: self._actualizar_cantidad(r, val))
            self.tabla_carrito.setCellWidget(row, 2, spin)
            
            # Subtotal
            item_subtotal = QTableWidgetItem(f"${subtotal:.2f}")
            item_subtotal.setFlags(item_subtotal.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_carrito.setItem(row, 3, item_subtotal)
            
            # Botón Quitar
            btn_quitar = QPushButton("Quitar")
            btn_quitar.clicked.connect(lambda checked, r=row: self._quitar_producto(r))
            self.tabla_carrito.setCellWidget(row, 4, btn_quitar)

    def _actualizar_cantidad(self, row: int, nueva_cantidad: int):
        """Actualiza la cantidad de un producto en el carrito."""
        if row < len(self.detalles_pedido):
            id_prod, cant, precio_unit, nombre = self.detalles_pedido[row]
            self.detalles_pedido[row] = (id_prod, nueva_cantidad, precio_unit, nombre)
            self._cargar_tabla_carrito()
            self._actualizar_total()

    def _quitar_producto(self, row: int):
        """Quita un producto del carrito."""
        if 0 <= row < len(self.detalles_pedido):
            self.detalles_pedido.pop(row)
            self._cargar_tabla_carrito()
            self._actualizar_total()

    def _actualizar_total(self):
        """Actualiza el total del pedido."""
        total = sum(cantidad * precio_unit for _, cantidad, precio_unit, _ in self.detalles_pedido)
        self.lbl_total_valor.setText(f"${total:.2f}")

    def _limpiar(self):
        """Limpia todo el formulario."""
        self.combo_cliente.setCurrentIndex(0)
        self.combo_comercio.setCurrentIndex(0)
        self.tabla_productos.setRowCount(0)
        self.tabla_carrito.setRowCount(0)
        self.detalles_pedido = []
        self._actualizar_total()

    def _ejecutar_guardar(self):
        """Valida y guarda el pedido."""
        id_cliente = self.combo_cliente.currentData()
        id_comercio = self.combo_comercio.currentData()
        
        if not id_cliente:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un cliente.")
            return
        
        if not id_comercio:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un comercio.")
            return
        
        if not self.detalles_pedido:
            QMessageBox.warning(self, "Validación", "Debe agregar al menos un producto.")
            return
        
        total = sum(cantidad * precio_unit for _, cantidad, precio_unit, _ in self.detalles_pedido)
        
        # Confirmar
        cliente_texto = self.combo_cliente.currentText()
        comercio_texto = self.combo_comercio.currentText()
        
        detalle_items = "\n".join(f"  • {nombre} x{cantidad} = ${cantidad * precio_unit:.2f}" 
                                   for _, cantidad, precio_unit, nombre in self.detalles_pedido)
        
        respuesta = QMessageBox.question(
            self, "Confirmar pedido",
            f"""Cliente: {cliente_texto}
Comercio: {comercio_texto}

Items:
{detalle_items}

Total: ${total:.2f}

¿Crear este pedido?""",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        # Preparar detalles para la BD (sin el nombre, solo id_prod, cantidad, precio)
        detalles_bd = [(id_prod, cantidad, precio_unit) for id_prod, cantidad, precio_unit, _ in self.detalles_pedido]
        
        # Guardar
        if database.registrar_pedido_con_detalles(id_cliente, id_comercio, detalles_bd, total, 0.0):
            QMessageBox.information(self, "Guardado", "Pedido creado correctamente.")
            self._limpiar()
        else:
            QMessageBox.critical(self, "Error",
                                 "No se pudo guardar el pedido.\n"
                                 "Revise los datos e intente nuevamente.")
