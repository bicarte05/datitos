import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QStackedWidget, QListWidget, QLabel,
                             QFrame, QListWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import database
from views.clientes_view import ClientesView
from views.pedidos_view import PedidosView
from views.comercios_view import ComerciosView

# ============================================================
# DESIGN TOKENS
# ============================================================
C_FONDO_APP   = "#F1F5F9"
C_FONDO_MENU  = "#FFFFFF"
C_BORDER      = "#E2E8F0"
C_ACENTO      = "#0EA5E9"
C_ACENTO_FONDO = "#E0F2FE"
C_ACENTO_DARK = "#0284C7"
C_TEXTO       = "#0F172A"
C_TEXTO_MUTED = "#64748B"
C_DANGER      = "#EF4444"
C_SUCCESS     = "#22C55E"
C_WHITE       = "#CF7A7A"

NAV_ITEMS = ["Clientes", "Pedidos", "Comercios"]

# ============================================================
# HOJA DE ESTILOS
#
# REGLA DE ORO para fondos en Qt QSS:
#   - NUNCA usar "QWidget { background-color: X }" de forma global.
#     Qt hereda el fondo del padre a TODOS los hijos, haciendo imposible
#     sobreescribirlo selectivamente en la cascada.
#   - En cambio, pintar solo los contenedores que se conocen por nombre
#     (QMainWindow, QFrame#id) y dejar los QWidget internos con
#     background: transparent para que hereden visualmente del primer
#     ancestro con fondo definido.
# ============================================================
HOJA_DE_ESTILOS = f"""
    /* ── BASE: solo la ventana y el contenedor central reciben el gris ── */
    QMainWindow {{
        background-color: {C_FONDO_APP};
        font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    }}

    /* El widget central y el panel derecho heredan el gris de QMainWindow
       a través de background: transparent (comportamiento por defecto de QWidget).
       NO se les asigna color explícito. */

    /* ── SIDEBAR ─────────────────────────────────────────────────────── */
    QFrame#panel_lateral {{
        background-color: {C_FONDO_MENU};
        border-right: 1px solid {C_BORDER};
    }}
    /* Los QWidget hijos directos del panel lateral también deben ser blancos
       (el contenedor de status, por ejemplo). Se usa el descendant selector. */
    QFrame#panel_lateral QWidget {{
        background-color: {C_FONDO_MENU};
        font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    }}
    QFrame#panel_lateral QLabel {{
        background-color: transparent;
    }}

    QListWidget {{
        background-color: transparent;
        border: none;
        outline: none;
        padding: 4px 8px;
    }}
    QListWidget::item {{
        color: {C_TEXTO_MUTED};
        padding: 9px 12px;
        font-size: 13px;
        font-weight: 600;
        border-radius: 7px;
    }}
    QListWidget::item:hover {{
        background-color: #F8FAFC;
        color: {C_TEXTO};
    }}
    QListWidget::item:selected {{
        background-color: {C_ACENTO_FONDO};
        color: {C_ACENTO};
        border-radius: 7px;
    }}

    /* ── TABS ────────────────────────────────────────────────────────── */
    /*
     * QTabWidget::pane es el contenedor del contenido de las pestañas.
     * Se le da fondo blanco aquí. Los QWidget hijos del pane lo heredan
     * a través de background: transparent.
     */
    QTabWidget::pane {{
        border: 1px solid {C_BORDER};
        background-color: {C_WHITE};
        border-radius: 0px 8px 8px 8px;
        top: -1px;
    }}
    QTabBar {{
        alignment: left;
    }}
    QTabBar::tab {{
        background-color: {C_FONDO_APP};
        color: {C_TEXTO_MUTED};
        border: 1px solid {C_BORDER};
        border-bottom: none;
        padding: 9px 24px;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.5px;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
        margin-right: 3px;
    }}
    QTabBar::tab:hover {{
        background-color: #E2E8F0;
        color: {C_TEXTO};
    }}
    QTabBar::tab:selected {{
        background-color: {C_WHITE};
        color: {C_ACENTO};
        border-color: {C_BORDER};
        border-bottom: 1px solid {C_WHITE};
        margin-bottom: -1px;
        font-weight: 800;
    }}

    /* ── LABELS ──────────────────────────────────────────────────────── */
    QLabel {{
        background-color: transparent;
        color: {C_TEXTO};
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
        font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    }}

    /* ── INPUTS ──────────────────────────────────────────────────────── */
    QLineEdit {{
        background-color: {C_WHITE};
        border: 1.5px solid {C_BORDER};
        border-radius: 7px;
        padding: 10px 12px;
        font-size: 13px;
        color: {C_TEXTO};
        selection-background-color: {C_ACENTO_FONDO};
    }}
    QLineEdit:focus {{
        border-color: {C_ACENTO};
        background-color: #F0F9FF;
    }}
    QLineEdit:hover {{
        border-color: #94A3B8;
    }}

    /* ── BUTTONS ─────────────────────────────────────────────────────── */
    QPushButton {{
        background-color: {C_ACENTO};
        color: {C_WHITE};
        border: none;
        border-radius: 7px;
        padding: 11px 20px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 0.3px;
    }}
    QPushButton:hover   {{ background-color: {C_ACENTO_DARK}; }}
    QPushButton:pressed {{ background-color: #0369A1; }}

    /* Botón Limpiar */
    QPushButton#btn_limpiar {{
        background-color: #F59E0B;
        color: {C_WHITE};
    }}
    QPushButton#btn_limpiar:hover   {{ background-color: #D97706; }}
    QPushButton#btn_limpiar:pressed {{ background-color: #B45309; }}

    /* Botón Cancelar */
    QPushButton#btn_cancelar {{
        background-color: #6B7280;
        color: {C_WHITE};
    }}
    QPushButton#btn_cancelar:hover   {{ background-color: #4B5563; }}
    QPushButton#btn_cancelar:pressed {{ background-color: #374151; }}

    /* ── TABLE ───────────────────────────────────────────────────────── */
    QTableWidget {{
        border: 1px solid {C_BORDER};
        border-radius: 7px;
        background-color: {C_WHITE};
        gridline-color: {C_BORDER};
        font-size: 13px;
    }}
    QTableWidget::item {{
        padding: 8px 12px;
        color: {C_TEXTO};
        background-color: transparent;
    }}
    QTableWidget::item:selected {{
        background-color: {C_ACENTO_FONDO};
        color: {C_ACENTO_DARK};
    }}
    QHeaderView::section {{
        background-color: #F8FAFC;
        color: {C_TEXTO_MUTED};
        font-weight: 700;
        font-size: 11px;
        letter-spacing: 0.5px;
        padding: 8px 12px;
        border: none;
        border-bottom: 1px solid {C_BORDER};
        border-right: 1px solid {C_BORDER};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: #CBD5E1;
        border-radius: 3px;
        min-height: 30px;
    }}
"""


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Los Datitos Delivery")
        self.resize(1100, 700)
        self.setMinimumSize(800, 500)
        try:
            self.setWindowIcon(QIcon("logo.ico"))
        except Exception:
            pass

        widget_central = QWidget()
        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

        # ── SIDEBAR ──────────────────────────────────────────
        self.panel_lateral = QFrame()
        self.panel_lateral.setObjectName("panel_lateral")
        self.panel_lateral.setFixedWidth(220)

        layout_lateral = QVBoxLayout()
        layout_lateral.setContentsMargins(0, 24, 0, 24)
        layout_lateral.setSpacing(0)
        self.panel_lateral.setLayout(layout_lateral)

        # Fila del título: "LOS DATITOS DELIVERY" + punto de conexión alineados
        header_row = QWidget()
        header_row.setStyleSheet("background-color: transparent;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(16, 0, 16, 0)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_row.setLayout(header_layout)

        titulo = QLabel("LOS DATITOS DELIVERY")
        titulo.setStyleSheet(
            f"font-size: 14px; font-weight: 800; color: {C_TEXTO};"
            f"letter-spacing: 0.5px; background-color: transparent;"
        )

        self.punto_conexion = QFrame()
        self.punto_conexion.setFixedSize(7, 7)

        if database.verificar_conexion():
            self.punto_conexion.setStyleSheet(
                f"background-color: {C_SUCCESS}; border-radius: 3px;"
            )
        else:
            self.punto_conexion.setStyleSheet(
                f"background-color: {C_DANGER}; border-radius: 3px;"
            )

        header_layout.addWidget(titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.punto_conexion)

        layout_lateral.addWidget(header_row)
        layout_lateral.addSpacing(16)

        self.menu_lista = QListWidget()
        self.menu_lista.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_lista.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for nombre in NAV_ITEMS:
            self.menu_lista.addItem(QListWidgetItem(nombre))

        layout_lateral.addWidget(self.menu_lista)
        layout_principal.addWidget(self.panel_lateral)

        # ── PANEL DERECHO ─────────────────────────────────────
        # QWidget sin color explícito → hereda transparente → muestra el gris de QMainWindow
        contenedor_derecho = QWidget()
        layout_derecho = QVBoxLayout()
        layout_derecho.setContentsMargins(32, 32, 32, 32)
        contenedor_derecho.setLayout(layout_derecho)

        self.titulo_vista = QLabel("Clientes")
        self.titulo_vista.setStyleSheet(
            f"font-size: 22px; font-weight: 800; color: {C_TEXTO};"
            f"margin-bottom: 4px; background-color: transparent;"
        )
        self.descripcion_vista = QLabel("Gestiona el registro de clientes del sistema")
        self.descripcion_vista.setStyleSheet(
            f"font-size: 13px; color: {C_TEXTO_MUTED}; margin-bottom: 20px;"
            f"background-color: transparent;"
        )
        layout_derecho.addWidget(self.titulo_vista)
        layout_derecho.addWidget(self.descripcion_vista)

        self.stack_vistas = QStackedWidget()
        self.stack_vistas.addWidget(ClientesView())
        self.stack_vistas.addWidget(PedidosView())
        self.stack_vistas.addWidget(ComerciosView())

        layout_derecho.addWidget(self.stack_vistas)
        layout_principal.addWidget(contenedor_derecho)

        self._view_meta = [
            ("Clientes",  "Gestiona el registro de clientes del sistema"),
            ("Pedidos",   "Administra y consulta las transacciones de pedidos"),
            ("Comercios", "Gestiona los comercios adheridos al sistema"),
        ]

        self.menu_lista.currentRowChanged.connect(self._cambiar_vista)
        self.menu_lista.setCurrentRow(0)

    def _cambiar_vista(self, index: int) -> None:
        self.stack_vistas.setCurrentIndex(index)
        if 0 <= index < len(self._view_meta):
            titulo, desc = self._view_meta[index]
            self.titulo_vista.setText(titulo)
            self.descripcion_vista.setText(desc)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(HOJA_DE_ESTILOS)
    
    # Sincronizar las secuencias de la BD antes de mostrar la ventana
    database.sincronizar_secuencias()
    
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())