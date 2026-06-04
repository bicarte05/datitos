from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
import database
from views.clientes_completo_view import ClientesCompletoView
from views.eliminar_view import EliminarView
from views.listar_view import ListarView


class ClientesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()

        # 1. Insertar (nueva vista completa)
        tab_insert = ClientesCompletoView()

        # 2. Eliminar
        tab_delete = EliminarView(
            label_texto="ID del Cliente a eliminar:",
            placeholder="Ej: 145",
            funcion_db=database.eliminar_cliente,
        )

        # 3. Listar
        cabeceras = ["ID Cliente", "Nombre", "Email", "Teléfono"]
        tab_list = ListarView(cabeceras=cabeceras, funcion_db=database.obtener_clientes)

        tabs.addTab(tab_insert, "INSERTAR")
        tabs.addTab(tab_delete, "ELIMINAR")
        tabs.addTab(tab_list, "LISTAR")

        layout.addWidget(tabs)
        self.setLayout(layout)