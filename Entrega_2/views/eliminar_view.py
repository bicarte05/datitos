from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox,
                             QPushButton, QMessageBox, QCompleter, QFrame)
from PyQt6.QtCore import Qt

class EliminarView(QWidget):
    # esquema_campos recibe lista de tuplas: (Nombre_columna, "input" o "info", placeholder)
    def __init__(self, esquema_campos: list, funcion_db, funcion_obtener_datos):
        super().__init__()
        self.funcion_db = funcion_db
        self.funcion_obtener_datos = funcion_obtener_datos

        self.inputs = []       # Guardará tuplas: (indice_columna, QComboBox)
        self.info_labels = []  # Guardará tuplas: (indice_columna, QLabel, nombre_campo)
        self.datos = []  
        self.id_seleccionado = None
        self._updating = False 

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        titulo = QLabel("Busque y seleccione el registro a eliminar:")
        titulo.setStyleSheet("font-size: 14px; font-weight: 800; color: #0F172A;")
        layout.addWidget(titulo)

        # 1. ZONA DE INPUTS (Buscadores)
        self.campos_layout = QVBoxLayout()
        self.campos_layout.setSpacing(4)

        # 2. ZONA DE INFORMACIÓN (Cuadro Gris)
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_layout.setSpacing(8)
        
        info_title = QLabel("Información del registro:")
        info_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #64748B; margin-bottom: 4px;")
        info_layout.addWidget(info_title)

        tiene_info = False

        # Construcción dinámica basada en el esquema
        for col_idx, (nombre_campo, tipo, placeholder) in enumerate(esquema_campos):
            if tipo == "input":
                lbl = QLabel(nombre_campo + ":")
                combo = QComboBox()
                combo.setEditable(True)
                combo.lineEdit().setPlaceholderText(placeholder)
                combo.setMinimumHeight(40)
                
                completer = combo.completer()
                if completer:
                    completer.setFilterMode(Qt.MatchFlag.MatchContains)
                    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
                    completer.popup().setStyleSheet("""
                        QListView {
                            background-color: #F8FAFC; 
                            color: #0F172A; 
                            border: 2px solid #0EA5E9; 
                            border-radius: 6px;
                            outline: none;
                        }
                        QListView::item { padding: 8px; }
                        QListView::item:selected { 
                            background-color: #E0F2FE; 
                            color: #0284C7; 
                            font-weight: bold;
                        }
                    """)
                
                combo.activated.connect(lambda idx, c=col_idx: self._on_combo_seleccionado(idx, c))
                combo.lineEdit().textEdited.connect(self._on_texto_editado)

                self.campos_layout.addWidget(lbl)
                self.campos_layout.addWidget(combo)
                self.inputs.append((col_idx, combo))
            
            elif tipo == "info":
                tiene_info = True
                # Usamos HTML básico <b> para poner el título en negrita
                lbl_info = QLabel(f"<b>{nombre_campo}:</b> -")
                lbl_info.setStyleSheet("font-size: 13px; color: #334155;")
                info_layout.addWidget(lbl_info)
                self.info_labels.append((col_idx, lbl_info, nombre_campo))

        layout.addLayout(self.campos_layout)
        layout.addSpacing(12)
        
        # Solo agregamos el cuadro gris si la entidad tiene campos "info"
        if tiene_info:
            self.info_frame.setLayout(info_layout)
            layout.addWidget(self.info_frame)
            layout.addSpacing(12)

        btn = QPushButton("Eliminar Registro")
        btn.setMinimumHeight(44)
        btn.setObjectName("btn_eliminar")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._ejecutar_eliminar)
        layout.addWidget(btn)

        advertencia = QLabel("⚠  Esta acción destruirá permanentemente los datos y sus dependencias.")
        advertencia.setStyleSheet(
            "color: #EF4444; font-size: 11px; margin-top: 6px;"
            "background-color: transparent;"
        )
        layout.addWidget(advertencia)

        self.setLayout(layout)

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
            "QComboBox { border: 1.5px solid #E2E8F0; border-radius: 7px; padding: 5px; background-color: #FFFFFF; color: #0F172A; font-size: 13px; }"
            "QComboBox:focus { border-color: #0EA5E9; }"
            "QComboBox::drop-down { border: none; width: 30px; }"
        )

        self.cargar_datos()

    def _reset_info_labels(self):
        """Devuelve el cuadro de información a su estado vacío con guiones"""
        for col_idx, lbl, nombre_campo in self.info_labels:
            lbl.setText(f"<b>{nombre_campo}:</b> -")

    def cargar_datos(self):
        if not self.funcion_obtener_datos: return
        
        self._updating = True
        self.datos = self.funcion_obtener_datos()
        self.id_seleccionado = None
        
        for col_idx, combo in self.inputs:
            combo.clear()
            
        for fila in self.datos:
            id_real = fila[0]
            for col_idx, combo in self.inputs:
                combo.addItem(str(fila[col_idx]), userData=id_real)
        
        for col_idx, combo in self.inputs:
            combo.setCurrentIndex(-1)
            
        self._reset_info_labels()
        self._updating = False

    def showEvent(self, event):
        self.cargar_datos()
        super().showEvent(event)

    def _on_texto_editado(self):
        if not self._updating:
            self.id_seleccionado = None
            self._reset_info_labels()

    def _on_combo_seleccionado(self, index_in_combo, col_idx):
        if self._updating or index_in_combo == -1: return
        
        self._updating = True
        
        # Encontramos el combo específico que el usuario tocó
        combo_modificado = next(combo for idx, combo in self.inputs if idx == col_idx)
        self.id_seleccionado = combo_modificado.itemData(index_in_combo)
        
        fila_encontrada = next((f for f in self.datos if f[0] == self.id_seleccionado), None)
        
        if fila_encontrada:
            # 1. Actualizamos los otros combos (inputs)
            for idx, combo in self.inputs:
                if idx != col_idx:
                    idx_a_seleccionar = combo.findData(self.id_seleccionado)
                    if idx_a_seleccionar != -1:
                        combo.setCurrentIndex(idx_a_seleccionar)
            
            # 2. Rellenamos el cuadro gris de información
            for idx, lbl, nombre_campo in self.info_labels:
                valor = fila_encontrada[idx]
                lbl.setText(f"<b>{nombre_campo}:</b> {valor}")
                        
        self._updating = False

    def _ejecutar_eliminar(self) -> None:
        if not self.id_seleccionado:
            if self.inputs:
                # Si escribió a mano en la primera caja
                primer_combo = self.inputs[0][1]
                texto_id = primer_combo.currentText().strip()
                if texto_id:
                    self.id_seleccionado = texto_id
                else:
                    QMessageBox.warning(self, "Campo vacío", "Seleccione o busque un registro válido para eliminar.")
                    return
            else:
                return

        respuesta = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar permanentemente este registro?\n\n",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if self.funcion_db(self.id_seleccionado):
            QMessageBox.information(self, "Eliminado", "El registro fue eliminado correctamente.")
            self.cargar_datos() 
        else:
            QMessageBox.critical(self, "Error crítico",
                                 "No se pudo eliminar el registro.\n"
                                 "La base de datos bloqueó la acción debido a dependencias activas.")