from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
import database
from views.insertar_view import InsertarView
from views.eliminar_view import EliminarView
from views.listar_view import ListarView


class PedidosView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()

        # 1. Insertar (transaccional)
        campos_insertar = {
            "ID Cliente": "Ej: 414",
            "ID Comercio": "Ej: 15",
            "Monto Total": "Ej: 15000",
        }
        tab_insert = InsertarView(
            campos_dict=campos_insertar,
            funcion_db=database.crear_pedido_transaccional,
            titulo_boton="Crear Pedido",
        )

        # 2. Eliminar (transaccional: borra detalle + pedido)
        tab_delete = EliminarView(
            label_texto="ID del Pedido a anular:",
            placeholder="Ej: 1045",
            funcion_db=database.eliminar_pedido,
        )

        # 3. Listar
        cabeceras = ["ID Pedido", "ID Cliente", "ID Comercio", "Total"]
        tab_list = ListarView(
            cabeceras=cabeceras, 
            funcion_db=database.obtener_pedidos,
            placeholder_buscador="🔍 Buscar por ID Pedido, Cliente o Comercio...",
            usar_filtro_combo=True,
            titulo_combo="comercios",
            columna_combo=2
        )

        tabs.addTab(tab_insert, "INSERTAR")
        tabs.addTab(tab_delete, "ELIMINAR")
        tabs.addTab(tab_list, "LISTAR")

        layout.addWidget(tabs)
        self.setLayout(layout)