from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
import database
from views.insertar_view import InsertarView
from views.eliminar_view import EliminarView
from views.listar_view import ListarView


class ComerciosView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()

        # 1. Insertar
        campos_insertar = {
            "ID del Comercio": "Ej: 15",
            "Nombre del Local": "Ej: Pizza Los Datitos",
            "Dirección Física": "Ej: Av. Ramón Picarte 1234",
        }
        tab_insert = InsertarView(
            campos_dict=campos_insertar,
            funcion_db=database.registrar_comercio,
            titulo_boton="Registrar Comercio",
        )

        # 2. Eliminar 
        tab_delete = EliminarView(
            label_texto="ID del Comercio a eliminar:",
            placeholder="Ej: 15",
            funcion_db=database.eliminar_comercio,
        )

        # 3. Listar
        cabeceras = ["ID Comercio", "Nombre", "Dirección"]
        tab_list = ListarView(
            cabeceras=cabeceras, 
            funcion_db=database.obtener_comercios,
            placeholder_buscador="🔍 Buscar por ID, Nombre o Dirección...",
            usar_filtro_combo=False
        )

        tabs.addTab(tab_insert, "INSERTAR")
        tabs.addTab(tab_delete, "ELIMINAR")
        tabs.addTab(tab_list, "LISTAR")

        layout.addWidget(tabs)
        self.setLayout(layout)