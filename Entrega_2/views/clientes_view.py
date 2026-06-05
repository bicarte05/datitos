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
        tab_delete = EliminarView(
            label_texto="ID del Cliente a eliminar:",
            placeholder="Ej: 145",
            funcion_db=database.eliminar_cliente,
        )

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