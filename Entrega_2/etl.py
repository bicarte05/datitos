import os
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import Error
from dotenv import load_dotenv

# Cargar credenciales del archivo .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(ENV_PATH)

def conectar_oltp():
    """Conexión a la base de datos Transaccional (Los Datitos Delivery)"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT")
    )

def conectar_olap():
    """Conexión a la base de datos Analítica (Modelo Estrella)"""
    return psycopg2.connect(
        host=os.getenv("OLAP_HOST"),
        database=os.getenv("OLAP_NAME"),
        user=os.getenv("OLAP_USER"),
        password=os.getenv("OLAP_PASS"),
        port=os.getenv("OLAP_PORT")
    )

def ejecutar_etl():
    print("Iniciando proceso ETL (Extracción, Transformación y Carga)...")
    
    conn_oltp = None
    conn_olap = None
    
    try:
        # Abrimos ambas conexiones
        conn_oltp = conectar_oltp()
        conn_olap = conectar_olap()
        
        cur_oltp = conn_oltp.cursor()
        cur_olap = conn_olap.cursor()

        # ==========================================
        # 1. DIMENSIÓN USUARIOS
        # ==========================================
        print("-> Procesando dim_usuario...")
        # EXTRACT & TRANSFORM (Separar nombre y apellido)
        cur_oltp.execute("""
            SELECT 
                id_cliente,
                split_part(nombre, ' ', 1),
                COALESCE(NULLIF(SUBSTRING(nombre FROM POSITION(' ' IN nombre) + 1), nombre), 'Sin Apellido'),
                email
            FROM public.cliente;
        """)
        usuarios = cur_oltp.fetchall()
        
        # LOAD
        query_usuarios = """
            INSERT INTO public.dim_usuario (id_usuario_origen, nombre, apellido, email)
            VALUES %s
            ON CONFLICT (id_usuario_origen) DO UPDATE 
            SET nombre = EXCLUDED.nombre, apellido = EXCLUDED.apellido, email = EXCLUDED.email;
        """
        execute_values(cur_olap, query_usuarios, usuarios)

        # ==========================================
        # 2. DIMENSIÓN COMERCIOS
        # ==========================================
        print("-> Procesando dim_comercio...")
        # EXTRACT & TRANSFORM (Prevenir rubros nulos)
        cur_oltp.execute("""
            SELECT id_comercio, nombre, COALESCE(rubro, 'General') 
            FROM public.comercio;
        """)
        comercios = cur_oltp.fetchall()
        
        # LOAD
        query_comercios = """
            INSERT INTO public.dim_comercio (id_comercio_origen, nombre, rubro)
            VALUES %s
            ON CONFLICT (id_comercio_origen) DO UPDATE 
            SET nombre = EXCLUDED.nombre, rubro = EXCLUDED.rubro;
        """
        execute_values(cur_olap, query_comercios, comercios)

        # ==========================================
        # 3. DIMENSIÓN FECHA
        # ==========================================
        print("-> Procesando dim_fecha...")
        cur_oltp.execute("""
            SELECT DISTINCT 
                TO_CHAR(fecha, 'YYYYMMDD')::INT, DATE(fecha), EXTRACT(YEAR FROM fecha),
                EXTRACT(MONTH FROM fecha), EXTRACT(DAY FROM fecha), EXTRACT(QUARTER FROM fecha),
                TO_CHAR(fecha, 'TMMonth'), TO_CHAR(fecha, 'TMDay')
            FROM public.pedido;
        """)
        fechas = cur_oltp.fetchall()
        
        query_fechas = """
            INSERT INTO public.dim_fecha (date_key, fecha, anio, mes, dia, trimestre, nombre_mes, nombre_dia)
            VALUES %s
            ON CONFLICT (date_key) DO NOTHING;
        """
        execute_values(cur_olap, query_fechas, fechas)

        # ==========================================
        # 4. DIMENSIÓN HORA
        # ==========================================
        print("-> Procesando dim_hora...")
        cur_oltp.execute("""
            SELECT DISTINCT 
                TO_CHAR(fecha, 'HH24MI')::INT, EXTRACT(HOUR FROM fecha), EXTRACT(MINUTE FROM fecha),
                CASE 
                    WHEN EXTRACT(HOUR FROM fecha) BETWEEN 6 AND 11 THEN 'Mañana'
                    WHEN EXTRACT(HOUR FROM fecha) BETWEEN 12 AND 18 THEN 'Tarde'
                    ELSE 'Noche'
                END
            FROM public.pedido;
        """)
        horas = cur_oltp.fetchall()
        
        query_horas = """
            INSERT INTO public.dim_hora (time_key, hora, minuto, periodo_dia)
            VALUES %s
            ON CONFLICT (time_key) DO NOTHING;
        """
        execute_values(cur_olap, query_horas, horas)

        # ==========================================
        # 5. TABLA DE HECHOS (hechos_pedidos)
        # ==========================================
        print("-> Procesando hechos_pedidos...")
        cur_oltp.execute("""
            SELECT 
                p.id_pedido, p.id_cliente, p.id_comercio,
                TO_CHAR(p.fecha, 'YYYYMMDD')::INT, TO_CHAR(p.fecha, 'HH24MI')::INT,
                COALESCE(pg.monto_final, p.total_productos + p.costo_envio),
                p.costo_envio, COALESCE(p.distancia_km, 0), 1
            FROM public.pedido p
            LEFT JOIN public.pago pg ON p.id_pedido = pg.id_pedido;
        """)
        hechos = cur_oltp.fetchall()
        
        query_hechos = """
            INSERT INTO public.hechos_pedidos (
                id_pedido_origen, id_usuario_fk, id_comercio_fk, id_fecha_fk, 
                id_hora_fk, monto_total, costo_envio, distancia_km, cantidad_pedidos
            )
            VALUES %s
            ON CONFLICT (id_pedido_origen) DO NOTHING;
        """
        execute_values(cur_olap, query_hechos, hechos)

        # Guardamos los cambios en la BD Analítica
        conn_olap.commit()
        print("Proceso ETL finalizado con exito. Datos transferidos a la BD Analitica.")

    except Error as e:
        print(f"Error durante la ejecución del ETL: {e}")
        if conn_olap:
            conn_olap.rollback()
    finally:
        # Cerramos las conexiones de forma segura
        if conn_oltp:
            cur_oltp.close()
            conn_oltp.close()
        if conn_olap:
            cur_olap.close()
            conn_olap.close()

if __name__ == "__main__":
    ejecutar_etl()