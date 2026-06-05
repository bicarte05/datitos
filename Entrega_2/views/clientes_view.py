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
        # Añadimos las dos nuevas columnas: Teléfono y Suscripción
        cabeceras = ["ID Cliente", "Nombre", "Email", "Teléfono", "Suscripción"]
        cabeceras_detalle = ["ID Pedido", "ID Comercio", "Total"] 
        
        tab_list = ListarView(
            cabeceras=cabeceras, 
            funcion_db=database.obtener_clientes,
            cabeceras_detalle=cabeceras_detalle,
            funcion_detalle_db=database.obtener_pedidos_por_cliente,
            placeholder_buscador="🔍 Buscar por ID, Nombre, Correo o Teléfono...",
            usar_filtro_combo=True,
            titulo_combo="suscripciones",
            columna_combo=4
        )
        tabs.addTab(tab_insert, "INSERTAR")
        tabs.addTab(tab_delete, "ELIMINAR")
        tabs.addTab(tab_list, "LISTAR")

        layout.addWidget(tabs)
        self.setLayout(layout)