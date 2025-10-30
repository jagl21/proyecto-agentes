# News Portal - Aplicación Web de Noticias con Agente IA

Sistema completo de curación y publicación automatizada de contenidos con inteligencia artificial.

## Características

### Aplicación Web
- **Backend REST API** con Flask y SQLite
- **Frontend responsive** con diseño moderno tipo tarjetas
- **Panel de Administración** para revisión de contenidos (Human-in-the-Loop)
- **Actualización automática** de contenido cada 30 segundos
- **Validación de datos** en el backend
- **Manejo de errores** robusto
- **Diseño mobile-first** totalmente responsive

### Agente IA (Nuevo)
- **Monitorización de Telegram** para extraer URLs automáticamente
- **Web Scraping con Playwright** (JavaScript rendering)
- **Procesamiento con OpenAI GPT-4** para generar resúmenes
- **Generación de imágenes con DALL-E 3** si no hay imagen disponible
- **Flujo orquestado con LangGraph** para procesamiento complejo
- **Human-in-the-Loop** antes de publicación final

## Estructura del Proyecto

```
proyecto-agentes/
├── backend/
│   ├── app.py              # Servidor Flask y endpoints API (actualizado)
│   ├── database.py         # Gestión de BD SQLite (posts + pending_posts)
│   ├── models.py           # Modelos y validación de datos
│   └── requirements.txt    # Dependencias Python
├── frontend/
│   ├── index.html          # Página pública de noticias
│   ├── admin.html          # Panel de administración (NUEVO)
│   ├── css/
│   │   ├── styles.css      # Estilos página pública
│   │   └── admin.css       # Estilos panel admin (NUEVO)
│   └── js/
│       ├── app.js          # Lógica página pública
│       └── admin.js        # Lógica panel admin (NUEVO)
├── agent/                  # Agente IA (NUEVO)
│   ├── main.py             # Script principal del agente
│   ├── config.py           # Configuración
│   ├── graph.py            # Orquestación con LangGraph
│   ├── telegram_monitor.py # Monitorización de Telegram
│   ├── web_scraper.py      # Scraping con Playwright
│   ├── content_processor.py # Procesamiento con OpenAI
│   ├── image_handler.py    # Gestión de imágenes
│   ├── api_client.py       # Cliente HTTP para Flask API
│   ├── requirements.txt    # Dependencias del agente
│   ├── .env.example        # Template de configuración
│   └── README.md           # Documentación del agente
├── .gitignore
├── claude.md               # Documentación completa del proyecto
└── README.md               # Este archivo
```

## Requisitos Previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- Un navegador web moderno

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd proyecto-agentes
```

### 2. Configurar el Backend

#### En Windows:

```bash
# Navegar a la carpeta backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

#### En Linux/Mac:

```bash
# Navegar a la carpeta backend
cd backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Iniciar el Backend

1. Asegúrate de estar en la carpeta `backend` con el entorno virtual activado
2. Ejecuta el servidor:

```bash
python app.py
```

El servidor estará disponible en: `http://localhost:5000`

**Salida esperada:**
```
Starting Posts API Server...
Server running on http://localhost:5000
API endpoints available at http://localhost:5000/api/posts
Database initialized successfully
 * Running on http://0.0.0.0:5000
```

### Abrir el Frontend

1. Navega a la carpeta `frontend`
2. Abre el archivo `index.html` en tu navegador web

**Opciones para abrir:**
- Doble clic en `index.html`
- Desde el terminal: `start frontend/index.html` (Windows) o `open frontend/index.html` (Mac)
- Usar un servidor web local (recomendado para desarrollo):
  ```bash
  # Con Python
  cd frontend
  python -m http.server 8000
  ```
  Luego visita: `http://localhost:8000`

## API Endpoints

### 1. Obtener todas las noticias

```http
GET http://localhost:5000/api/posts
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "id": 1,
      "title": "Título de la noticia",
      "summary": "Resumen de la noticia...",
      "source_url": "https://example.com/article",
      "image_url": "https://example.com/image.jpg",
      "release_date": "2024-01-15",
      "provider": "CNN",
      "type": "Tecnología",
      "created_at": "2024-01-15 10:30:00"
    }
  ]
}
```

### 2. Obtener una noticia específica

```http
GET http://localhost:5000/api/posts/1
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Título de la noticia",
    ...
  }
}
```

**Noticia no encontrada (404):**
```json
{
  "success": false,
  "error": "Post with ID 1 not found"
}
```

### 3. Crear una nueva noticia

```http
POST http://localhost:5000/api/posts
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "title": "Nueva noticia importante",
  "summary": "Este es un resumen de la noticia que describe brevemente su contenido.",
  "source_url": "https://example.com/news/article-123",
  "release_date": "2024-01-15",
  "image_url": "https://example.com/images/news.jpg",
  "provider": "BBC News",
  "type": "Internacional"
}
```

**Campos obligatorios:**
- `title` (string, max 500 caracteres)
- `summary` (string, max 2000 caracteres)
- `source_url` (string, debe comenzar con http:// o https://)
- `release_date` (string, formato fecha)

**Campos opcionales:**
- `image_url` (string, debe comenzar con http:// o https://)
- `provider` (string)
- `type` (string)

**Respuesta exitosa (201):**
```json
{
  "success": true,
  "message": "Post created successfully",
  "data": {
    "id": 3,
    "title": "Nueva noticia importante",
    ...
  }
}
```

**Error de validación (400):**
```json
{
  "success": false,
  "error": "Missing required field: title"
}
```

## Probar la API

### Usando curl (Terminal)

**Crear una noticia:**
```bash
curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Avances en IA\",\"summary\":\"Nuevos desarrollos en inteligencia artificial...\",\"source_url\":\"https://example.com\",\"release_date\":\"2024-01-15\",\"provider\":\"Tech News\",\"type\":\"Tecnología\"}"
```

**Obtener todas las noticias:**
```bash
curl http://localhost:5000/api/posts
```

### Usando Python

```python
import requests
import json

# URL base
BASE_URL = "http://localhost:5000/api/posts"

# Crear una noticia
new_post = {
    "title": "Título de prueba",
    "summary": "Este es un resumen de prueba.",
    "source_url": "https://example.com/article",
    "release_date": "2024-01-15",
    "image_url": "https://example.com/image.jpg",
    "provider": "Test Provider",
    "type": "Prueba"
}

response = requests.post(BASE_URL, json=new_post)
print(json.dumps(response.json(), indent=2))

# Obtener todas las noticias
response = requests.get(BASE_URL)
print(json.dumps(response.json(), indent=2))
```

## Características del Frontend

- **Diseño responsive:** Se adapta a móviles, tablets y escritorio
- **Tarjetas interactivas:** Efecto hover y animaciones suaves
- **Actualización automática:** Refresca el contenido cada 30 segundos
- **Manejo de errores:** Muestra mensajes claros y botón de reintento
- **Estado vacío:** Mensaje amigable cuando no hay noticias
- **Imágenes con fallback:** Placeholder cuando la imagen no carga
- **Enlaces externos seguros:** Abre artículos en nueva pestaña con rel="noopener"

## Base de Datos

La base de datos SQLite (`posts.db`) se crea automáticamente al iniciar el servidor por primera vez.

**Esquema de la tabla `posts`:**

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| title | TEXT | NOT NULL |
| summary | TEXT | NOT NULL |
| source_url | TEXT | NOT NULL |
| image_url | TEXT | NULL |
| release_date | TEXT | NOT NULL |
| provider | TEXT | NULL |
| type | TEXT | NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Desarrollo

### Desactivar el entorno virtual

```bash
deactivate
```

### Limpiar la base de datos

Para empezar de cero, simplemente elimina el archivo `posts.db` en la carpeta `backend`:

```bash
rm backend/posts.db  # Linux/Mac
del backend\posts.db  # Windows
```

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'flask'"

**Solución:** Asegúrate de haber activado el entorno virtual y ejecutado `pip install -r requirements.txt`

### Error: "CORS policy" en el navegador

**Solución:** Verifica que el servidor Flask esté corriendo y que `flask-cors` esté instalado.

### La página no muestra noticias

**Solución:**
1. Verifica que el servidor backend esté corriendo en `http://localhost:5000`
2. Abre la consola del navegador (F12) para ver errores
3. Prueba el endpoint directamente: `http://localhost:5000/api/posts`

### Error: "Address already in use"

**Solución:** El puerto 5000 ya está en uso. Puedes:
1. Detener el proceso que usa el puerto
2. Cambiar el puerto en `app.py` (línea final: `app.run(port=XXXX)`)

## Tecnologías Utilizadas

**Backend:**
- Python 3
- Flask (Framework web)
- flask-cors (CORS support)
- SQLite3 (Base de datos)

**Frontend:**
- HTML5
- CSS3 (Grid, Flexbox, Animaciones)
- JavaScript (ES6+, Fetch API)

## Agente IA de Curación de Contenidos

### ¿Qué hace el agente?

El agente IA automatiza completamente el proceso de curación de contenidos:

1. **Monitoriza Telegram** - Se conecta a un grupo/canal y extrae URLs
2. **Navega las URLs** - Usa Playwright para cargar páginas con JavaScript
3. **Extrae contenido** - Obtiene título, contenido, imágenes y metadatos
4. **Genera resúmenes** - Usa GPT-4 para crear resúmenes de 2-3 líneas
5. **Maneja imágenes** - Extrae OpenGraph o genera con DALL-E 3
6. **Crea posts pendientes** - Envía al backend para revisión humana

### Instalación del Agente

Ver documentación completa en [`agent/README.md`](agent/README.md)

**Resumen rápido:**

```bash
cd agent
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install chromium

# Configurar .env con credenciales
cp .env.example .env
# Editar .env con tus API keys
```

### Configuración Necesaria

El agente requiere:

- **OpenAI API Key** (https://platform.openai.com/api-keys)
- **Telegram API credentials** (https://my.telegram.org/apps)
- **Chat ID** del grupo de Telegram a monitorizar

Ver `.env.example` en la carpeta `agent/` para detalles completos.

### Ejecutar el Agente

```bash
cd agent
python main.py
```

El agente procesará automáticamente todos los mensajes del grupo de Telegram y creará posts pendientes de revisión.

### Flujo Completo del Sistema

```
┌─────────────┐
│  Telegram   │ URLs compartidas en grupo
│   (Grupo)   │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│        AGENTE IA (LangGraph)        │
│  1. Extraer URLs                    │
│  2. Scraping (Playwright)           │
│  3. Procesar contenido (GPT-4)      │
│  4. Generar/validar imagen (DALL-E) │
│  5. Crear post pendiente (API)      │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│   PANEL DE ADMINISTRACIÓN           │
│   (http://localhost:5000/admin.html)│
│   - Ver posts pendientes            │
│   - Editar título/resumen           │
│   - Aprobar o rechazar              │
└──────┬──────────────────────────────┘
       │ (Aprobar)
       ↓
┌─────────────────────────────────────┐
│   PÁGINA PÚBLICA                    │
│   (http://localhost:5000)           │
│   - Mostrar noticias aprobadas      │
│   - Diseño tipo tarjetas            │
└─────────────────────────────────────┘
```

## Panel de Administración

El panel de administración (`admin.html`) permite revisar posts antes de publicarlos:

**Características:**
- Vista previa completa de cada post (título, resumen, imagen, fuente)
- Filtros por estado (Pendiente, Aprobado, Rechazado)
- Edición inline de título y resumen
- Botones de aprobar/rechazar
- Estadísticas en tiempo real
- Actualización automática cada 30 segundos

**Acceso:**
```
http://localhost:5000/admin.html
```

## API Endpoints (Actualizado)

### Posts Públicos
- `GET /api/posts` - Obtener posts publicados
- `POST /api/posts` - Crear post público directamente

### Posts Pendientes (Nuevo)
- `GET /api/pending-posts` - Listar posts pendientes
- `POST /api/pending-posts` - Crear post pendiente (usado por agente)
- `PUT /api/pending-posts/<id>` - Editar post pendiente
- `PUT /api/pending-posts/<id>/approve` - Aprobar y publicar
- `PUT /api/pending-posts/<id>/reject` - Rechazar post
- `DELETE /api/pending-posts/<id>` - Eliminar post pendiente

Ver `http://localhost:5000/` para lista completa de endpoints.

## Tecnologías Utilizadas

**Backend:**
- Python 3.7+
- Flask 3.0 (Framework web)
- flask-cors (CORS support)
- SQLite3 (Base de datos)

**Frontend:**
- HTML5
- CSS3 (Grid, Flexbox, Animaciones)
- JavaScript Vanilla (ES6+, Fetch API)

**Agente IA:**
- LangGraph (Orquestación de agentes)
- Telethon (Cliente Telegram)
- Playwright (Web scraping con JavaScript)
- OpenAI API (GPT-4 + DALL-E 3)
- BeautifulSoup4 (Parsing HTML)

## Documentación Adicional

- [`claude.md`](claude.md) - Documentación completa del proyecto para Claude
- [`agent/README.md`](agent/README.md) - Guía completa del agente IA

## Mejoras Futuras

**Corto plazo:**
- Autenticación para panel de administración
- Logs detallados del agente
- Persistencia de mensajes procesados (evitar duplicados)
- Notificaciones cuando hay posts pendientes

**Largo plazo:**
- Ejecución automática con cron job
- Soporte para múltiples fuentes (WhatsApp, RSS, Twitter)
- Dashboard de estadísticas
- Machine learning para scoring de calidad

## Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

## Autor

Proyecto de agentes IA para curación automatizada de contenidos.
