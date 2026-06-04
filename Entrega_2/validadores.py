"""
Módulo de validadores para el sistema de delivery.
Contiene funciones para validar entrada de usuario.
"""
import re


def validar_email(email: str) -> tuple[bool, str]:
    """
    Valida formato de email.
    Retorna: (es_válido, mensaje_error)
    """
    email = email.strip()
    if not email:
        return False, "El email no puede estar vacío."
    
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patron, email):
        return False, "Formato de email inválido. Ej: usuario@ejemplo.com"
    
    return True, ""


def validar_telefono(telefono: str) -> tuple[bool, str]:
    """
    Valida formato de teléfono (números, espacios, guiones, paréntesis).
    Retorna: (es_válido, mensaje_error)
    """
    telefono = telefono.strip()
    if not telefono:
        return False, "El teléfono no puede estar vacío."
    
    patron = r'^[\d\s\-\+\(\)]{7,20}$'
    if not re.match(patron, telefono):
        return False, "Teléfono inválido. Use números, guiones o espacios."
    
    return True, ""


def validar_nombre(nombre: str) -> tuple[bool, str]:
    """
    Valida que el nombre tenga al menos 3 caracteres y solo letras/espacios.
    Retorna: (es_válido, mensaje_error)
    """
    nombre = nombre.strip()
    if not nombre:
        return False, "El nombre no puede estar vacío."
    
    if len(nombre) < 3:
        return False, "El nombre debe tener al menos 3 caracteres."
    
    # Permite letras, espacios, acentos y algunos caracteres especiales comunes
    patron = r'^[a-záéíóúñ\s\'-]{3,}$'
    if not re.match(patron, nombre, re.IGNORECASE):
        return False, "El nombre contiene caracteres inválidos."
    
    return True, ""


def validar_direccion(direccion: str) -> tuple[bool, str]:
    """
    Valida que la dirección sea válida.
    Retorna: (es_válido, mensaje_error)
    """
    direccion = direccion.strip()
    if not direccion:
        return False, "La dirección no puede estar vacía."
    
    if len(direccion) < 5:
        return False, "La dirección debe tener al menos 5 caracteres."
    
    if len(direccion) > 200:
        return False, "La dirección no puede exceder 200 caracteres."
    
    return True, ""


def validar_rubro(rubro: str) -> tuple[bool, str]:
    """
    Valida que el rubro sea válido.
    Retorna: (es_válido, mensaje_error)
    """
    rubro = rubro.strip()
    if not rubro:
        return False, "El rubro no puede estar vacío."
    
    if len(rubro) < 3:
        return False, "El rubro debe tener al menos 3 caracteres."
    
    if len(rubro) > 50:
        return False, "El rubro no puede exceder 50 caracteres."
    
    return True, ""


def validar_numero_positivo(valor: str, nombre_campo: str) -> tuple[bool, str]:
    """
    Valida que un valor sea un número positivo.
    Retorna: (es_válido, mensaje_error)
    """
    try:
        num = float(valor.strip())
        if num <= 0:
            return False, f"{nombre_campo} debe ser mayor a 0."
        return True, ""
    except ValueError:
        return False, f"{nombre_campo} debe ser un número válido."


def validar_id(id_str: str, nombre_campo: str) -> tuple[bool, int]:
    """
    Valida que un ID sea un número entero positivo.
    Retorna: (es_válido, id_convertido)
    """
    try:
        id_int = int(id_str.strip())
        if id_int <= 0:
            return False, 0
        return True, id_int
    except ValueError:
        return False, 0
