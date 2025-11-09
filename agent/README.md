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

### Modo Real-Time (monitoreo continuo) ⭐ MODO POR DEFECTO

```bash
python main.py
```

**Este es el modo recomendado para producción.**

El agente escucha nuevos mensajes indefinidamente usando **LangGraph**:
1. Se conecta a Telegram y **se queda escuchando**
2. Cada vez que llega un **mensaje nuevo** con URLs:
   - Extrae las URLs
   - Las procesa con el pipeline LangGraph (scraping → IA → imagen → API)
   - Crea posts pendientes en el backend
3. **Nunca termina** (hasta Ctrl+C)

**Ventajas del modo real-time:**
- ✅ Procesamiento instantáneo de nuevos mensajes
- ✅ No procesa mensajes duplicados (tracking con SQLite)
- ✅ Ideal para producción (corre 24/7)
- ✅ No requiere cron job o ejecución manual
- ✅ Usa LangGraph para orquestación consistente

**Detener el agente:**
```
Ctrl+C (Windows/Mac/Linux)
```

El agente mostrará estadísticas al salir:
- Total de mensajes procesados
- Exitosos / Fallidos

### Modo Batch (procesamiento de historial)

```bash
python main.py --batch
```

El agente procesa el historial de mensajes **una sola vez** usando **LangGraph**:
1. Se conecta a Telegram
2. Extrae URLs de los últimos N mensajes
3. Para cada URL, ejecuta el pipeline LangGraph (scraping → IA → imagen → API)
4. Crea posts pendientes en el backend
5. **Termina la ejecución**

**Cuándo usar el modo batch:**
- ✅ Primera ejecución del sistema (procesar mensajes existentes)
- ✅ Recuperación después de downtime (catch-up de mensajes perdidos)
- ✅ Testing y desarrollo (procesar timeframes específicos)
- ✅ Curación manual de contenido antiguo

**Nota:** El modo batch **no tiene deduplicación automática**. Si lo ejecutas varias veces sobre el mismo historial, creará posts duplicados.

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

### Arquitectura Unificada con LangGraph

Ambos modos (real-time y batch) usan el **mismo pipeline LangGraph** para procesar URLs:

```
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTA DE URLs                               │
│  ┌────────────────────┐          ┌────────────────────┐         │
│  │  Modo Real-Time    │          │  Modo Batch        │         │
│  │  (por defecto)     │          │  (--batch)         │         │
│  │                    │          │                    │         │
│  │  Telegram Events   │          │  Telegram History  │         │
│  │  (nuevos mensajes) │          │  (últimos N msgs)  │         │
│  └────────┬───────────┘          └────────┬───────────┘         │
│           │                               │                      │
│           └───────────────┬───────────────┘                      │
│                           ↓                                      │
│                    [ URL extraída ]                              │
└───────────────────────────┬──────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              PIPELINE LANGGRAPH (unificado)                      │
│                                                                  │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│   │ scrape_url   │ →   │ process_     │ →   │ handle_image │   │
│   │              │     │ content      │     │              │   │
│   │ (Playwright) │     │ (OpenAI GPT) │     │ (DALL-E)     │   │
│   └──────────────┘     └──────────────┘     └──────────────┘   │
│                                                    ↓             │
│                                          ┌──────────────┐       │
│                                          │ create_      │       │
│                                          │ pending_post │       │
│                                          │ (API call)   │       │
│                                          └──────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    [ Post pendiente creado ]
                            ↓
                  [ Admin Panel para revisión ]
```

**Diferencias entre modos:**
- **Real-time**: Procesa cada URL inmediatamente cuando llega (event-driven)
- **Batch**: Procesa todas las URLs históricas secuencialmente (loop)

**Pipeline compartido (LangGraph):**
- Mismo código para ambos modos
- Manejo de errores consistente
- Fácil de mantener y testear

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
