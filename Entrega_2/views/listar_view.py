from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, 
                             QLineEdit, QComboBox) # <--- Importamos QLineEdit y QComboBox
from PyQt6.QtCore import Qt

class ListarView(QWidget):
    def __init__(self, cabeceras: list[str], funcion_db, cabeceras_detalle=None, funcion_detalle_db=None,
                 placeholder_buscador="🔍 Buscar...", usar_filtro_combo=True, titulo_combo="Filtro", columna_combo=None):
        super().__init__()
        self.funcion_db = funcion_db
        self.funcion_detalle_db = funcion_detalle_db
        self.usar_filtro_combo = usar_filtro_combo
        self.titulo_combo = titulo_combo
        self.columna_combo = columna_combo if columna_combo is not None else 4  # Por defecto columna 4

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- ZONA DE FILTROS (NUEVO) ---
        filtros_layout = QHBoxLayout()
        
        # 1. Buscador Universal
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText(placeholder_buscador)
        self.buscador.setMinimumHeight(36)
        self.buscador.textChanged.connect(self._aplicar_filtros) # Filtra mientras escribes
        
        # 2. Filtro Dinámico (Combo)
        self.combo_filtro = QComboBox()
        self.combo_filtro.setMinimumHeight(36)
        self.combo_filtro.setMinimumWidth(180)
        self.combo_filtro.currentTextChanged.connect(self._aplicar_filtros)
        self.combo_filtro.setVisible(usar_filtro_combo)  # Se muestra solo si se especifica
        
        filtros_layout.addWidget(self.buscador)
        if usar_filtro_combo:
            filtros_layout.addWidget(self.combo_filtro)
        layout.addLayout(filtros_layout)

        # --- BARRA SUPERIOR (Contador y Botón) ---
        barra = QHBoxLayout()
        self.lbl_contador = QLabel("Cargando…")
        self.lbl_contador.setStyleSheet("font-size: 12px; color: #64748B;")
        
        btn_refresh = QPushButton("↻  Actualizar")
        btn_refresh.setFixedWidth(130)
        btn_refresh.setMinimumHeight(36)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self._refrescar)
        
        barra.addWidget(self.lbl_contador)
        barra.addStretch()
        barra.addWidget(btn_refresh)
        layout.addLayout(barra)

        # --- TABLA PRINCIPAL ---
        self.tabla = QTableWidget(0, len(cabeceras))
        self.tabla.setHorizontalHeaderLabels(cabeceras)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("QTableWidget { alternate-background-color: #F8FAFC; background-color: #FFFFFF; }")
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.cellClicked.connect(self._al_seleccionar_fila)
        layout.addWidget(self.tabla)

        # --- TABLA DETALLES ---
        if self.funcion_detalle_db and cabeceras_detalle:
            self.lbl_titulo_detalle = QLabel("Haz clic en un registro para ver sus pedidos")
            self.lbl_titulo_detalle.setStyleSheet("font-weight: bold; margin-top: 10px; color: #334155;")
            layout.addWidget(self.lbl_titulo_detalle)

            self.tabla_detalle = QTableWidget(0, len(cabeceras_detalle))
            self.tabla_detalle.setHorizontalHeaderLabels(cabeceras_detalle)
            self.tabla_detalle.horizontalHeader().setStretchLastSection(True)
            self.tabla_detalle.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.tabla_detalle.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.tabla_detalle.setAlternatingRowColors(True)
            self.tabla_detalle.setStyleSheet("QTableWidget { alternate-background-color: #F1F5F9; background-color: #FFFFFF; }")
            self.tabla_detalle.verticalHeader().setVisible(False)
            self.tabla_detalle.setMaximumHeight(200) 
            layout.addWidget(self.tabla_detalle)
        else:
            self.tabla_detalle = None

        self.setLayout(layout)
        self._refrescar()

    def _refrescar(self) -> None:
        """Obtiene los datos de la BD y llena la tabla principal y los filtros."""
        self.tabla.setRowCount(0)
        datos = self.funcion_db()
        
        valores_filtro_unicos = set() # Para guardar los valores únicos del filtro
        
        for fila in datos:
            pos = self.tabla.rowCount()
            self.tabla.insertRow(pos)
            for col, val in enumerate(fila):
                texto = str(val)
                item = QTableWidgetItem(texto)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.tabla.setItem(pos, col, item)
                
                # Si estamos en la columna de filtro, guardamos el valor
                if self.usar_filtro_combo and col == self.columna_combo:
                    valores_filtro_unicos.add(texto)

        # Llenamos el menú desplegable con los valores encontrados
        if self.usar_filtro_combo:
            self.combo_filtro.blockSignals(True) # Bloqueamos para que no filtre accidentalmente mientras se llena
            self.combo_filtro.clear()
            self.combo_filtro.addItem(f"Todos los {self.titulo_combo}")
            for valor in sorted(valores_filtro_unicos):
                self.combo_filtro.addItem(valor)
            self.combo_filtro.blockSignals(False)

        # Reseteamos los campos visuales
        self.buscador.clear()
        if self.usar_filtro_combo:
            self.combo_filtro.setCurrentIndex(0)
        self._aplicar_filtros() # Actualiza el contador

        if self.tabla_detalle:
            self.tabla_detalle.setRowCount(0)
            self.lbl_titulo_detalle.setText("Haz clic en un registro para ver sus pedidos")

    def _aplicar_filtros(self, *args):
        """Oculta o muestra filas. Ignora argumentos de signals de Qt."""
        texto_busqueda = self.buscador.text().lower()
        filtro_combo = self.combo_filtro.currentText() if self.usar_filtro_combo else None
        
        # Siempre buscamos en todas las columnas
        columnas_busqueda = range(self.tabla.columnCount())
        
        visibles = 0
        for row in range(self.tabla.rowCount()):
            mostrar = True
            
            # 1. Filtro de Búsqueda
            if texto_busqueda:
                coincide_texto = False
                for col in columnas_busqueda:
                    item = self.tabla.item(row, col)
                    if item and texto_busqueda in item.text().lower():
                        coincide_texto = True
                        break
                if not coincide_texto:
                    mostrar = False
                    
            # 2. Filtro Dinámico (solo si está habilitado y existe la columna)
            if mostrar and self.usar_filtro_combo and filtro_combo and not filtro_combo.startswith("Todos los"):
                if self.columna_combo < self.tabla.columnCount():
                    item_filtro = self.tabla.item(row, self.columna_combo)
                    if not item_filtro or item_filtro.text() != filtro_combo:
                        mostrar = False
            
            self.tabla.setRowHidden(row, not mostrar)
            if mostrar:
                visibles += 1
                
        self.lbl_contador.setText(f"{visibles} registro{'s' if visibles != 1 else ''} visible{'s' if visibles != 1 else ''}")

    def _al_seleccionar_fila(self, row, col):
        if not self.tabla_detalle or not self.funcion_detalle_db: return
        item_id = self.tabla.item(row, 0)
        item_nombre = self.tabla.item(row, 1)
        if item_id:
            id_seleccionado = item_id.text()
            nombre = item_nombre.text() if item_nombre else f"ID: {id_seleccionado}"
            self.lbl_titulo_detalle.setText(f"Pedidos de: {nombre}")
            self.tabla_detalle.setRowCount(0)
            datos_detalle = self.funcion_detalle_db(id_seleccionado)
            for fila in datos_detalle:
                pos = self.tabla_detalle.rowCount()
                self.tabla_detalle.insertRow(pos)
                for c, val in enumerate(fila):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                    self.tabla_detalle.setItem(pos, c, item)