# AI Agent - Content Curation System

Agente IA para curación automática de contenidos desde Telegram.

## Instalación

### 1. Crear entorno virtual

```bash
cd agent
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Instalar navegadores de Playwright

```bash
playwright install chromium
```

### 4. Configurar variables de entorno

Copia `.env.example` a `.env` y rellena los valores:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```bash
# OpenAI API Key (obligatorio)
OPENAI_API_KEY=sk-tu-api-key-aqui

# Telegram API (obligatorio)
# Obtener en: https://my.telegram.org/apps
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=tu_hash_aqui
TELEGRAM_PHONE=+34123456789

# ID del grupo/canal de Telegram
TELEGRAM_CHAT_ID=-1001234567890
```

## Obtener Credenciales

### OpenAI API Key

1. Ve a https://platform.openai.com/api-keys
2. Crea una nueva API key
3. Cópiala en `.env`

### Telegram API

1. Ve a https://my.telegram.org/apps
2. Inicia sesión con tu número de teléfono
3. Crea una nueva aplicación
4. Copia `api_id` y `api_hash` a `.env`

### Telegram Chat ID

**Método 1 - Usando @RawDataBot (Recomendado):**

1. Añade `@RawDataBot` a tu grupo de Telegram
2. Envía cualquier mensaje en el grupo (ej. "hola")
3. El bot responderá con datos JSON
4. Busca `"chat": {"id": -1001234567890}`
5. Copia ese número (incluye el signo negativo) a `.env`

**Método 2 - Script Python:**

Si ya configuraste las credenciales de Telegram, ejecuta:

```bash
python get_chat_id.py
```

Este script listará TODOS tus grupos y canales con sus IDs. Elige el que quieres monitorizar.

**Formato del Chat ID:**
- Siempre es un número negativo
- Ejemplo: `TELEGRAM_CHAT_ID=-1001234567890`

## Uso

### Modo Batch (ejecución única)

```bash
python main.py
```

El agente procesa el historial de mensajes:
1. Se conecta a Telegram
2. Extrae URLs de los últimos N mensajes
3. Navega cada URL con Playwright
4. Extrae contenido y genera resumen con OpenAI
5. Obtiene o genera imágenes
6. Crea posts pendientes en el backend
7. **Termina la ejecución**

### Modo Real-Time (monitoreo continuo) ⭐ RECOMENDADO

```bash
python main.py --realtime
```

El agente escucha nuevos mensajes indefinidamente:
1. Se conecta a Telegram y **se queda escuchando**
2. Cada vez que llega un **mensaje nuevo** con URLs:
   - Extrae las URLs
   - Las procesa automáticamente (scraping → IA → imagen → API)
   - Crea posts pendientes
3. **Nunca termina** (hasta Ctrl+C)

**Ventajas del modo real-time:**
- ✅ Procesamiento instantáneo de nuevos mensajes
- ✅ No procesa mensajes duplicados (tracking con SQLite)
- ✅ Ideal para producción (corre 24/7)
- ✅ No requiere cron job o ejecución manual

**Detener el agente:**
```
Ctrl+C (Windows/Mac/Linux)
```

El agente mostrará estadísticas al salir:
- Total de mensajes procesados
- Exitosos / Fallidos / Saltados

### Probar módulos individuales

```bash
# Probar Telegram
python telegram_monitor.py

# Probar scraping
python web_scraper.py

# Probar procesamiento
python content_processor.py

# Probar API client
python api_client.py
```

## Flujo del Agente

```
Telegram → URLs → Web Scraping → AI Processing → Image Handling → API → Admin Panel
```

## Configuración Avanzada

Ver `.env.example` para todas las opciones disponibles.

## Troubleshooting

**Error: "Missing required configuration"**
- Verifica que todas las variables obligatorias estén en `.env`

**Error al conectar a Telegram**
- Verifica `TELEGRAM_API_ID` y `TELEGRAM_API_HASH`
- Asegúrate de que el número de teléfono sea correcto
- La primera vez te pedirá un código de verificación

**Error al generar imágenes**
- Verifica tu `OPENAI_API_KEY`
- Asegúrate de tener créditos en tu cuenta de OpenAI

**Playwright browser not found**
- Ejecuta: `playwright install chromium`

## Logs

Los logs se guardan en `agent.log` (configurable en `.env`).

## Próximos Pasos

Después de ejecutar el agente:

1. Abre http://localhost:5000/admin.html
2. Revisa los posts pendientes
3. Aprueba o rechaza según corresponda
4. Los aprobados aparecerán en http://localhost:5000
