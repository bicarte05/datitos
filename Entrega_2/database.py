import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

# Carga las credenciales desde el archivo .env de forma segura
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(ENV_PATH)

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

def _limpiar_id(valor_str):
    """
    Toma un RUT de la interfaz (Ej: '11111111-1') y lo convierte
    a un entero válido para los campos id_cliente / id_comercio.
    """
    try:
        # Si tiene guion, toma solo la primera parte. Luego quita puntos si los hay.
        limpio = str(valor_str).split('-')[0].replace('.', '')
        return int(limpio)
    except ValueError:
        return 0 # Retorna 0 si escribieron texto inválido

# ==========================================
# CRUD - CLIENTES
# ==========================================
def registrar_cliente(rut, nombre, email):
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        id_cli = _limpiar_id(rut)
        # Adaptado a las columnas reales: id_cliente, nombre, email
        cur.execute("INSERT INTO public.cliente (id_cliente, nombre, email) VALUES (%s, %s, %s)", 
                    (id_cli, nombre, email))
        conn.commit()
        return True
    except Error as e:
        print(f"Error registrando cliente: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def obtener_clientes():
    conn = conectar()
    if not conn: return []
    try:
        cur = conn.cursor()
        # AQUÍ ESTÁ EL CAMBIO: agregamos "telefono" al final del SELECT
        cur.execute("SELECT id_cliente, nombre, email, telefono FROM public.cliente ORDER BY nombre")
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo clientes: {e}")
        return []
    finally:
        if conn: conn.close()

def eliminar_cliente(id_cliente):
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        id_cli = _limpiar_id(id_cliente)
        
        # 1. Eliminar dependencias directas (hijos débiles)
        cur.execute("DELETE FROM public.direccion WHERE id_cliente = %s", (id_cli,))
        cur.execute("DELETE FROM public.carrito WHERE id_cliente = %s", (id_cli,))
        
        # 2. Eliminar el registro padre
        cur.execute("DELETE FROM public.cliente WHERE id_cliente = %s", (id_cli,))
        
        # 3. Confirmar la transacción
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"Error eliminando cliente: {e}")
        # Si falla (ej: el cliente tiene un PEDIDO activo, la BD bloqueará el DELETE)
        # Hacemos rollback para revertir el borrado de la dirección.
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

# ==========================================
# CRUD - COMERCIOS
# ==========================================
def registrar_comercio(rut_comercio, nombre, direccion):
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        id_com = _limpiar_id(rut_comercio)
        # Adaptado a las columnas reales: id_comercio, nombre, direccion
        cur.execute("INSERT INTO public.comercio (id_comercio, nombre, direccion) VALUES (%s, %s, %s)", 
                    (id_com, nombre, direccion))
        conn.commit()
        return True
    except Error as e:
        print(f"Error registrando comercio: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def obtener_comercios():
    conn = conectar()
    if not conn: return []
    try:
        cur = conn.cursor()
        # SE AGREGÓ: rubro, id_ciudad
        cur.execute("SELECT id_comercio, nombre, direccion, rubro, id_ciudad FROM public.comercio ORDER BY nombre")
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo comercios: {e}")
        return []
    finally:
        if conn: conn.close()

def eliminar_comercio(id_comercio):
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        id_com = _limpiar_id(id_comercio)
        
        # 1. Eliminar dependencias (productos del comercio)
        cur.execute("DELETE FROM public.producto WHERE id_comercio = %s", (id_com,))
        
        # 2. Eliminar el registro principal
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
        # SE AGREGÓ: total_productos, id_repartidor
        cur.execute("""
            SELECT id_pedido, id_cliente, id_comercio, total_productos, id_repartidor
            FROM public.pedido
            ORDER BY id_pedido DESC
        """)
        return cur.fetchall()
    except Error as e:
        print(f"Error obteniendo pedidos: {e}")
        return []
    finally:
        if conn: conn.close()

def eliminar_pedido(id_pedido):
    """
    Eliminación transaccional compleja: Borra todos los registros vinculados
    al ciclo de vida del pedido antes de borrar el pedido en sí.
    """
    conn = conectar()
    if not conn: return False
    try:
        cur = conn.cursor()
        
        # 1. Eliminar todas las entidades hijas que referencian al id_pedido
        cur.execute("DELETE FROM public.detalle_pedido WHERE id_pedido = %s", (id_pedido,))
        cur.execute("DELETE FROM public.pago WHERE id_pedido = %s", (id_pedido,))
        cur.execute("DELETE FROM public.reclamo WHERE id_pedido = %s", (id_pedido,))
        cur.execute("DELETE FROM public.valoracion_pedido WHERE id_pedido = %s", (id_pedido,))
        
        # 2. Eliminar el pedido principal
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