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
            "Nombre del Local": "Ej: Pizza Los Datitos",
            "Rubro": "Ej: Pizzería",
            "Dirección Física": "Ej: Av. Ramón Picarte 1234",
        }
        tab_insert = InsertarView(
            campos_dict=campos_insertar,
            funcion_db=database.registrar_comercio,
            titulo_boton="Registrar Comercio",
        )

        # 2. Eliminar
        esquema_eliminar = [
            ("ID Comercio", "input", "Buscar por ID..."),
            ("Nombre del Local", "input", "Buscar por nombre..."),
            ("Dirección Física", "info", "")
        ]
        tab_delete = EliminarView(
            esquema_campos=esquema_eliminar,
            funcion_db=database.eliminar_comercio,
            funcion_obtener_datos=database.obtener_comercios
        )

        # 3. Listar
        cabeceras = ["ID Comercio", "Nombre", "Rubro", "Dirección"]
        tab_list = ListarView(cabeceras=cabeceras, funcion_db=database.obtener_comercios)

        tabs.addTab(tab_insert, "INSERTAR")
        tabs.addTab(tab_delete, "ELIMINAR")
        tabs.addTab(tab_list, "LISTAR")

        layout.addWidget(tabs)
        self.setLayout(layout)