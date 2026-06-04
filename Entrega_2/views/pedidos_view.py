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

        # 2. Eliminar
        esquema_eliminar = [
            ("ID Pedido", "input", "Buscar por ID de Pedido..."),
            ("ID Cliente solicitante", "info", ""),
            ("ID Comercio preparador", "info", ""),
            ("Total de Productos", "info", ""),     # <--- NUEVO
            ("ID Repartidor", "info", "")           # <--- NUEVO
        ]
        tab_delete = EliminarView(
            esquema_campos=esquema_eliminar,
            funcion_db=database.eliminar_pedido,
            funcion_obtener_datos=database.obtener_pedidos
        )

        # 3. Listar (Actualizado para que coincida con las 5 columnas)
        cabeceras = ["ID Pedido", "ID Cliente", "ID Comercio", "Total Productos", "ID Repartidor"]
        tab_list = ListarView(cabeceras=cabeceras, funcion_db=database.obtener_pedidos)

        # 3. Listar
        cabeceras = ["ID Pedido", "ID Cliente", "ID Comercio", "Total"]
        tab_list = ListarView(cabeceras=cabeceras, funcion_db=database.obtener_pedidos)

        tabs.addTab(tab_insert, "INSERTAR")
        tabs.addTab(tab_delete, "ELIMINAR")
        tabs.addTab(tab_list, "LISTAR")

        layout.addWidget(tabs)
        self.setLayout(layout)