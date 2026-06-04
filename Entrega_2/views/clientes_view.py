from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
import database
from views.insertar_view import InsertarView
from views.eliminar_view import EliminarView
from views.listar_view import ListarView


class ClientesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()

        # 1. Insertar
        campos_insertar = {
            "ID del Cliente": "Ej: 145",
            "Nombre Completo": "Ej: Juan Pérez",
            "Correo Electrónico": "ejemplo@uach.cl",
        }
        tab_insert = InsertarView(
            campos_dict=campos_insertar,
            funcion_db=database.registrar_cliente,
            titulo_boton="Guardar Cliente",
        )

        # 2. Eliminar
        # (Nombre del campo, "input" o "info", Placeholder)
        esquema_eliminar = [
            ("ID Cliente", "input", "Buscar por ID..."),
            ("Nombre Completo", "input", "Buscar por nombre..."),
            ("Correo Electrónico", "info", ""),
            ("Teléfono", "info", "")
        ]
        tab_delete = EliminarView(
            esquema_campos=esquema_eliminar,
            funcion_db=database.eliminar_cliente,
            funcion_obtener_datos=database.obtener_clientes
        )

        cabeceras = ["ID Cliente", "Nombre", "Email", "Teléfono"]
        tab_list = ListarView(cabeceras=cabeceras, funcion_db=database.obtener_clientes)
        
        # 3. Listar
        cabeceras = ["ID Cliente", "Nombre", "Email"]
        tab_list = ListarView(cabeceras=cabeceras, funcion_db=database.obtener_clientes)

        tabs.addTab(tab_insert, "INSERTAR")
        tabs.addTab(tab_delete, "ELIMINAR")
        tabs.addTab(tab_list, "LISTAR")

        layout.addWidget(tabs)
        self.setLayout(layout)