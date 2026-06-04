from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

class VistaBaseConTabs(QWidget):
    """
    Clase base que genera la estructura de pestañas: Insertar, Eliminar, Listar.
    Cualquier módulo (Clientes, Comercios, etc.) hereda de aquí.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        # Instanciamos los contenedores que las clases hijas llenarán
        self.tab_insertar = QWidget()
        self.tab_eliminar = QWidget()
        self.tab_listar = QWidget()
        
        self.tabs.addTab(self.tab_insertar, "INSERTAR")
        self.tabs.addTab(self.tab_eliminar, "ELIMINAR")
        self.tabs.addTab(self.tab_listar, "LISTAR")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)