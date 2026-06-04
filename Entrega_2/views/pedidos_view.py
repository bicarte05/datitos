from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
import database
from views.pedidos_completo_view import PedidosCompletoView
from views.eliminar_view import EliminarView
from views.listar_view import ListarView


class PedidosView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()

        # 1. Insertar (nueva vista completa)
        tab_insert = PedidosCompletoView()

        # 2. Eliminar (transaccional: borra detalle + pedido)
        tab_delete = EliminarView(
            label_texto="ID del Pedido a anular:",
            placeholder="Ej: 1045",
            funcion_db=database.eliminar_pedido,
        )

        # 3. Listar
        cabeceras = ["ID Pedido", "ID Cliente", "ID Comercio", "Total"]
        tab_list = ListarView(cabeceras=cabeceras, funcion_db=database.obtener_pedidos)

        tabs.addTab(tab_insert, "INSERTAR")
        tabs.addTab(tab_delete, "ELIMINAR")
        tabs.addTab(tab_list, "LISTAR")

        layout.addWidget(tabs)
        self.setLayout(layout)