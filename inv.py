import json
import mysql.connector
from datetime import datetime
import os
import sys
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()  # lee IOL_USERNAME / IOL_PASSWORD / DB_* de un archivo .env local

BASE_URL = "https://api.invertironline.com"

# Allocation objetivo de tu estrategia DCA
TARGET_ALLOCATION = {"SPY": 65.0, "VEA": 25.0, "IEMG": 10.0}


def get_token():
    """POST /token con grant_type=password. Devuelve el access_token."""
    username = os.environ["IOL_USERNAME"]
    password = os.environ["IOL_PASSWORD"]

    resp = requests.post(
        f"{BASE_URL}/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": username,
            "password": password,
            "grant_type": "password",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"]


def get_portafolio(access_token):
    """GET /api/portafolio. Devuelve el JSON crudo con la lista 'activos'."""
    resp = requests.get(
        f"{BASE_URL}/api/portafolio",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    resp.raise_for_status()
    return resp.json()


def calcpercentage(investment, total):
    acum = (investment / total) * 100
    return round(acum, 2)


def guardar_historial_db(activos_a_guardar):
    """
    Recibe una lista de tuplas con 3 elementos: [("SPY", 10, 20360.0), ("VEA", 5, 11530.0), ...]
    Abre conexión, asegura la tabla, inserta todos los registros y cierra limpiamente.
    """
    if not activos_a_guardar:
        return

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"],
            database=os.environ["DB_NAME"]
        )
        cursor = conn.cursor()

        # 1. Crear tabla si no existe (Actualizada con la columna cantidad)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticker_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fecha DATETIME,
                simbolo VARCHAR(10),
                cantidad DECIMAL(10, 2),
                valor_actual DECIMAL(15, 2)
            )
        """)

        # 2. Preparamos los datos
        fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ahora el INSERT tiene 4 columnas y pide 4 valores (%s, %s, %s, %s)
        sql = "INSERT INTO ticker_history (fecha, simbolo, cantidad, valor_actual) VALUES (%s, %s, %s, %s)"
        
        # Desempaquetamos los 3 elementos de la mochila y armamos el paquete de 4
        filas = [(fecha_ahora, simbolo, cantidad, valor) for simbolo, cantidad, valor in activos_a_guardar]

        # 3. Guardamos todos los registros
        cursor.executemany(sql, filas)
        conn.commit()

        for simbolo, cantidad, valor in activos_a_guardar:
            print(f"[DB] ✔️ Guardado en MySQL: {simbolo} | Cantidad: {cantidad} | Precio: {valor} ARS")

    except mysql.connector.Error as err:
        print(f"[DB] ❌ Error conectando/guardando en MySQL: {err}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("[DB] Conexión cerrada correctamente.")


def main():
    access_token = get_token()
    portafolio = get_portafolio(access_token)

    valores = {}
    activos_para_db = []  

    for activo in portafolio.get("activos", []):
        simbolo = activo["titulo"]["simbolo"]
        
        if simbolo in TARGET_ALLOCATION:
            valores[simbolo] = activo["valorizado"]
            valor_actual_ticket = activo["ultimoPrecio"]
            
            # NUEVO: Extraemos la cantidad desde el JSON de IOL
            cantidad = activo["cantidad"]
            
            # NUEVO: Ahora nuestra mochila guarda tuplas de 3 elementos
            activos_para_db.append((simbolo, cantidad, valor_actual_ticket))

    # Mandamos la nueva lista a la base de datos
    guardar_historial_db(activos_para_db)

    # Cálculos e impresiones por pantalla
    total = sum(valores.values())

    print("\nComposición actual del portafolio:\n")

    for simbolo, target in TARGET_ALLOCATION.items():
        valor = valores.get(simbolo, 0)
        actual = calcpercentage(valor, total)
        desvio = round(actual - target, 2)

        valor_formatted = f"{valor:,.0f}".replace(",", " ")

        print(
            f"{simbolo}: {valor_formatted} ARS — "
            f"{actual}% (objetivo {target}%, desvío {desvio:+}%)"
        )

    total_formatted = f"{total:,.0f}".replace(",", " ")
    print(f"\nTotal invertido en estos 3 ETFs: {total_formatted} ARS")


if __name__ == "__main__":
    main()