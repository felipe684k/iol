# IOL Portfolio Tracker

Herramienta en Python que se conecta a la API de [InvertirOnline (IOL)](https://api.invertironline.com) para monitorear la composición de un portfolio de inversión y calcular su desviación respecto a una asignación objetivo.

## Qué hace

1. Se autentica contra la API de IOL vía OAuth2 (`grant_type=password`).
2. Obtiene la composición actual del portfolio (`/api/portafolio`).
3. Filtra los activos relevantes y calcula el porcentaje que representa cada uno sobre el total invertido.
4. Compara ese porcentaje contra una asignación objetivo predefinida y muestra el desvío.
5. Guarda un snapshot histórico de la valorización en una base de datos MySQL, para poder trackear la evolución en el tiempo.

## Ejemplo de salida

```
Composición actual del portafolio:

SPY: 1 250 000 ARS — 63.5% (objetivo 65.0%, desvío -1.5%)
VEA: 490 000 ARS — 24.9% (objetivo 25.0%, desvío -0.1%)
IEMG: 229 000 ARS — 11.6% (objetivo 10.0%, desvío +1.6%)

Total invertido en estos 3 ETFs: 1 969 000 ARS
```

## Stack

- **Python** — lógica principal
- **requests** — consumo de la API de IOL
- **MySQL** (`mysql-connector-python`) — persistencia del historial
- **python-dotenv** — manejo de credenciales fuera del código

## Estructura

```
inv.py           # Script principal
TICKERHISTORY.sql        # Creación de la base de datos + queries de ejemplo
                   # (la tabla se crea automáticamente desde inv.py)
.env.example       # Variables de entorno necesarias (sin valores reales)
```

## Setup

1. Clonar el repo e instalar dependencias:
   ```bash
   pip install requests mysql-connector-python python-dotenv
   ```
2. Crear un archivo `.env` en la raíz (ver `.env.example`) con:
   ```
   IOL_USERNAME=tu_usuario
   IOL_PASSWORD=tu_contraseña
   DB_HOST=localhost
   DB_USER=tu_usuario_mysql
   DB_PASS=tu_contraseña_mysql
   DB_NAME=iol_portfolio
   ```
3. Correr el schema en tu instancia de MySQL:
   ```bash
   mysql -u tu_usuario -p < TICKERHISTORY.sql
   ```
4. Ejecutar:
   ```bash
   python inv.py
   ```

## Notas

- La asignación objetivo (`TARGET_ALLOCATION`) está hardcodeada en el script según mi estrategia personal de DCA (65% SPY / 25% VEA / 10% IEMG) — se puede ajustar fácilmente para otra composición.
- Repo privado porque el script se conecta a mi cuenta personal de inversión.
