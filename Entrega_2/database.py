import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import re

# Carga las credenciales desde el archivo .env de forma segura
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(ENV_PATH)

# ==========================================
# VALIDACIONES
# ==========================================
def validar_email(email: str) -> bool:
    """Valida formato de email."""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_telefono(telefono: str) -> bool:
    """Valida formato de teléfono (números, espacios, guiones, paréntesis)."""
    patron = r'^[\d\s\-\+\(\)]{7,20}$'
    return re.match(patron, telefono) is not None

def validar_nombre(nombre: str) -> bool:
    """Valida que el nombre tenga al menos 3 caracteres."""
    return len(nombre.strip()) >= 3

def validar_id_existe(tabla: str, id_nombre: str, id_valor: int) -> bool:
    """Verifica si un ID existe en la tabla especificada."""
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM {tabla} WHERE {id_nombre} = %s", (id_valor,))
        existe = cur.fetchone() is not None
        return existe
    except Error:
        return False
    finally:
        if conn: conn.close()

def conectar():
    """Establece la conexión usando variables de entorno."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Error as e:
        print(f"Error de base de datos: {e}")
        return None

def verificar_conexion():
    """Retorna True si la conexión a PostgreSQL es exitosa."""
    conn = conectar()
    if conn:
        conn.close()
        return True
    return False

def sincronizar_secuencias():
    """Sincroniza todas las secuencias SERIAL con el máximo ID de cada tabla.
    Esto previene errores de llave duplicada cuando hay datos previos.
    Se ejecuta automáticamente al inicializar."""
    conn = conectar()
    if not conn: return
    
    try:
        cur = conn.cursor()
        tablas = [
            ('cliente', 'id_cliente'),
            ('comercio', 'id_comercio'),
            ('pedido', 'id_pedido'),
            ('producto', 'id_producto'),
            ('ciudad', 'id_ciudad'),
            ('pais', 'id_pais'),
            ('suscripcion', 'id_suscripcion'),
        ]
        
        for tabla, id_col in tablas:
            try:
                # Obtener el máximo ID actual
                cur.execute(f"SELECT MAX({id_col}) FROM public.{tabla}")
                max_id = cur.fetchone()[0]
                if max_id is None:
                    max_id = 0
                
                # Obtener el nombre de la secuencia (PostgreSQL la nombra así por defecto)
                secuencia = f"{tabla}_{id_col}_seq"
                
                # Resetear la secuencia al siguiente valor
                cur.execute(f"SELECT setval('public.{secuencia}', %s, true)", (max_id + 1,))
            except Error as e:
                # Si la tabla no existe o no tiene secuencia, ignorar
                pass
        
        conn.commit()
    except Error as e:
        print(f"Error sincronizando secuencias: {e}")
    finally:
        if conn: conn.close()

def _limpiar_id(valor_str):
    """
    Convierte un string a un entero válido para búsquedas de ID.
    Si tiene guion, toma solo la primera parte. Luego quita puntos si los hay.
    """
    try:
        limpio = str(valor_str).split('-')[0].replace('.', '')
        return int(limpio)
    except ValueError:
        return 0

# ==========================================
# CATÁLOGOS - PAÍSES, CIUDADES, SUSCRIPCIONES
# ==========================================
def obtener_paises():
    """Obtiene lista de países disponibles."""
    conn = conectar()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_pais, nombre FROM public.pais ORDER BY nombre")
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo países: {e}")
        return []
    finally:
        if conn: conn.close()

def obtener_ciudades(id_pais: int = None):
    """Obtiene ciudades. Si id_pais es None, obtiene todas."""
    conn = conectar()
    if not conn: return []
    try:
        cur = conn.cursor()
        if id_pais:
            cur.execute("SELECT id_ciudad, nombre FROM public.ciudad WHERE id_pais = %s ORDER BY nombre", (id_pais,))
        else:
            cur.execute("SELECT id_ciudad, nombre FROM public.ciudad ORDER BY nombre")
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo ciudades: {e}")
        return []
    finally:
        if conn: conn.close()

def obtener_suscripciones():
    """Obtiene lista de tipos de suscripción disponibles."""
    conn = conectar()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_suscripcion, tipo, costo_mensual, descuento_envio FROM public.suscripcion ORDER BY tipo")
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo suscripciones: {e}")
        return []
    finally:
        if conn: conn.close()

# ==========================================
# CRUD - CLIENTES
# ==========================================
def registrar_cliente_completo(nombre, email, telefono, id_suscripcion, calle, numero, id_ciudad):
    """
    Registra un nuevo cliente con su dirección en una transacción.
    Inserta en cliente y dirección.
    """
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        
        # Convertir id_suscripcion a None si está vacío
        id_suscripcion = int(id_suscripcion) if id_suscripcion else None
        id_ciudad = int(id_ciudad) if id_ciudad else None
        
        # 1. Insertar cliente
        cur.execute(
            "INSERT INTO public.cliente (nombre, email, telefono, id_suscripcion) VALUES (%s, %s, %s, %s) RETURNING id_cliente", 
            (nombre, email, telefono, id_suscripcion)
        )
        id_cliente = cur.fetchone()[0]
        
        # 2. Insertar dirección si se proporcionó calle
        if calle and calle.strip():
            cur.execute(
                "INSERT INTO public.direccion (id_cliente, calle, numero, id_ciudad) VALUES (%s, %s, %s, %s)", 
                (id_cliente, calle, numero, id_ciudad)
            )
        
        conn.commit()
        return True
    except Error as e:
        print(f"Error registrando cliente: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def registrar_cliente(nombre, email, telefono):
    """Registra un cliente simple sin dirección."""
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO public.cliente (nombre, email, telefono) VALUES (%s, %s, %s)", 
            (nombre, email, telefono)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error registrando cliente: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def obtener_clientes():
    """Obtiene lista de clientes."""
    conn = conectar()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_cliente, nombre, email, telefono FROM public.cliente ORDER BY nombre LIMIT 50")
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo clientes: {e}")
        return []
    finally:
        if conn: conn.close()

def eliminar_cliente(id_cliente_str):
    """Elimina un cliente por ID."""
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        id_cli = _limpiar_id(id_cliente_str)
        cur.execute("DELETE FROM public.cliente WHERE id_cliente = %s", (id_cli,))
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"Error eliminando cliente: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

# ==========================================
# CRUD - COMERCIOS
# ==========================================
def registrar_comercio(nombre, rubro, direccion):
    """Registra un nuevo comercio. El ID se genera automáticamente."""
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        # El id_comercio es SERIAL, se genera automáticamente
        cur.execute(
            "INSERT INTO public.comercio (nombre, rubro, direccion) VALUES (%s, %s, %s)", 
            (nombre, rubro, direccion)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error registrando comercio: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def obtener_comercios():
    """Obtiene lista de comercios."""
    conn = conectar()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_comercio, nombre, rubro, direccion FROM public.comercio ORDER BY nombre LIMIT 50")
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo comercios: {e}")
        return []
    finally:
        if conn: conn.close()

def eliminar_comercio(id_comercio_str):
    """Elimina un comercio por ID."""
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        id_com = _limpiar_id(id_comercio_str)
        cur.execute("DELETE FROM public.comercio WHERE id_comercio = %s", (id_com,))
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"Error eliminando comercio: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

# ==========================================
# CRUD - PEDIDOS (TRANSACCIONAL)
# ==========================================
def crear_pedido_transaccional(rut_cliente, rut_comercio, total):
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        
        id_cli = _limpiar_id(rut_cliente)
        id_com = _limpiar_id(rut_comercio)
        monto = float(total)
        
        # 1. Adaptado al esquema: id_cliente, id_comercio, total_productos (la fecha se inserta automática con NOW())
        cur.execute("""
            INSERT INTO public.pedido (id_cliente, id_comercio, total_productos, fecha)
            VALUES (%s, %s, %s, NOW()) RETURNING id_pedido
        """, (id_cli, id_com, monto))
        
        id_pedido = cur.fetchone()[0]
        
        # 2. Adaptado al esquema de detalle_pedido: id_pedido, id_producto, cantidad, precio_unitario
        # Como en la UI no pedimos producto, simulamos con id_producto=1 y cantidad=1 para que pase el INSERT
        cur.execute("""
            INSERT INTO public.detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario)
            VALUES (%s, 1, 1, %s)
        """, (id_pedido, monto))
        
        conn.commit()
        return True
    except Error as e:
        print(f"Error en transacción de pedido: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def obtener_pedidos():
    conn = conectar()
    if not conn: return []
    try:
        cur = conn.cursor()
        # Adaptado a las columnas reales del esquema
        cur.execute("""
            SELECT id_pedido, id_cliente, id_comercio, total_productos
            FROM public.pedido
            ORDER BY id_pedido DESC LIMIT 50
        """)
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo pedidos: {e}")
        return []
    finally:
        if conn: conn.close()

def eliminar_pedido(id_pedido):
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        # El esquema de DB está correcto para estas eliminaciones en cascada
        cur.execute("DELETE FROM public.detalle_pedido WHERE id_pedido = %s", (id_pedido,))
        cur.execute("DELETE FROM public.pedido WHERE id_pedido = %s", (id_pedido,))
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"Error eliminando pedido: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

# ==========================================
# FUNCIONES PARA PEDIDOS MEJORADOS
# ==========================================
def obtener_productos_por_comercio(id_comercio: int):
    """Obtiene todos los productos de un comercio."""
    conn = conectar()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id_producto, nombre, descripcion, precio 
            FROM public.producto 
            WHERE id_comercio = %s 
            ORDER BY nombre
        """, (id_comercio,))
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo productos: {e}")
        return []
    finally:
        if conn: conn.close()

def registrar_pedido_con_detalles(id_cliente: int, id_comercio: int, detalles_productos: list, 
                                   total_productos: float, costo_envio: float = 0.0):
    """
    Registra un pedido completo con sus detalles en una transacción.
    
    detalles_productos: Lista de tuplas (id_producto, cantidad, precio_unitario)
    """
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        
        # 1. Insertar pedido
        cur.execute("""
            INSERT INTO public.pedido (id_cliente, id_comercio, total_productos, costo_envio)
            VALUES (%s, %s, %s, %s)
            RETURNING id_pedido
        """, (id_cliente, id_comercio, total_productos, costo_envio))
        id_pedido = cur.fetchone()[0]
        
        # 2. Insertar detalles del pedido
        for id_producto, cantidad, precio_unitario in detalles_productos:
            cur.execute("""
                INSERT INTO public.detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """, (id_pedido, id_producto, cantidad, precio_unitario))
        
        conn.commit()
        return True
    except Error as e:
        print(f"Error registrando pedido: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()


# ==========================================
# INSPECCION DEL ESQUEMA
# ==========================================
if __name__ == "__main__":
    print("Conectando a la base de datos...")
    conn = conectar()
    if not conn:
        print("No se pudo conectar. Revisa tu .env")
    else:
        print("Conexión exitosa. Leyendo esquema...\n")
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
        filas = cur.fetchall()
        if not filas:
            print("No se encontraron tablas en el schema 'public'.")
        else:
            tabla_actual = None
            for table, column, dtype in filas:
                if table != tabla_actual:
                    print(f"\n── {table} ──")
                    tabla_actual = table
                print(f"   {column:<30} {dtype}")
        conn.close()