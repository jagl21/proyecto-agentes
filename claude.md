# Agente IA para Curación de Contenidos y Publicación en Aplicación Web

## Visión General del Proyecto

Este proyecto consiste en un sistema completo de curación y publicación automatizada de contenidos que integra:

1. **Aplicación Web de Noticias** - Una plataforma para visualizar y gestionar noticias
2. **Agente IA Autónomo** - Sistema inteligente que monitoriza, procesa y prepara contenido
3. **Panel de Administración** - Interfaz para revisión humana antes de publicación (Human-in-the-Loop)

El objetivo es automatizar el proceso de descubrimiento de contenido relevante desde grupos de mensajería (Telegram), procesarlo con IA para generar resúmenes estructurados, y publicarlo tras aprobación humana en una aplicación web personalizada.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO DEL SISTEMA                    │
└─────────────────────────────────────────────────────────────────┘

   ┌──────────────┐
   │   Telegram   │
   │    (Grupo)   │
   └──────┬───────┘
          │ Mensajes con URLs
          ↓
   ┌─────────────────────────────────────────────────────────────┐
   │                      AGENTE IA                               │
   │  ┌────────────────────────────────────────────────────────┐ │
   │  │  1. Monitorización de Mensajes                         │ │
   │  │     - Conectar a Telegram (Telethon)                   │ │
   │  │     - Extraer URLs de mensajes recientes               │ │
   │  └────────────────────────────────────────────────────────┘ │
   │                          ↓                                   │
   │  ┌────────────────────────────────────────────────────────┐ │
   │  │  2. Procesamiento de URLs                              │ │
   │  │     - Navegar con Playwright (JavaScript rendering)    │ │
   │  │     - Extraer contenido principal                      │ │
   │  │     - Buscar OpenGraph/Twitter Card                    │ │
   │  │     - Generar resumen con OpenAI                       │ │
   │  │     - Generar imagen con DALL-E (si necesario)         │ │
   │  └────────────────────────────────────────────────────────┘ │
   │                          ↓                                   │
   │  ┌────────────────────────────────────────────────────────┐ │
   │  │  3. Envío a Sistema de Aprobación                      │ │
   │  │     - POST a /api/pending-posts                        │ │
   │  │     - Crear registro en pending_posts table            │ │
   │  └────────────────────────────────────────────────────────┘ │
   └─────────────────────────────────────────────────────────────┘
                             ↓
   ┌─────────────────────────────────────────────────────────────┐
   │              APLICACIÓN WEB (Flask + SQLite)                 │
   │                                                              │
   │  ┌─────────────────────────────────────────────────────┐   │
   │  │  Backend (Flask)                                     │   │
   │  │  - POST /api/pending-posts (crear pendiente)         │   │
   │  │  - GET /api/pending-posts (listar pendientes)        │   │
   │  │  - PUT /api/pending-posts/:id/approve (aprobar)      │   │
   │  │  - PUT /api/pending-posts/:id (editar)               │   │
   │  │  - POST /api/posts (publicar aprobado)               │   │
   │  │  - GET /api/posts (listar publicados)                │   │
   │  └─────────────────────────────────────────────────────┘   │
   │                          ↓                                   │
   │  ┌─────────────────────────────────────────────────────┐   │
   │  │  Base de Datos SQLite                                │   │
   │  │  ┌──────────────────┐  ┌──────────────────┐         │   │
   │  │  │ pending_posts    │  │ posts (públicos) │         │   │
   │  │  │ - id             │  │ - id             │         │   │
   │  │  │ - title          │  │ - title          │         │   │
   │  │  │ - summary        │  │ - summary        │         │   │
   │  │  │ - source_url     │  │ - source_url     │         │   │
   │  │  │ - image_url      │  │ - image_url      │         │   │
   │  │  │ - release_date   │  │ - release_date   │         │   │
   │  │  │ - provider       │  │ - provider       │         │   │
   │  │  │ - type           │  │ - type           │         │   │
   │  │  │ - status         │  │ - created_at     │         │   │
   │  │  │ - created_at     │  └──────────────────┘         │   │
   │  │  └──────────────────┘                                │   │
   │  └─────────────────────────────────────────────────────┘   │
   │                          ↓                                   │
   │  ┌─────────────────────────────────────────────────────┐   │
   │  │  Frontend                                            │   │
   │  │  ┌──────────────┐          ┌──────────────┐         │   │
   │  │  │ admin.html   │          │ index.html   │         │   │
   │  │  │ (Revisar)    │          │ (Público)    │         │   │
   │  │  │              │          │              │         │   │
   │  │  │ - Vista      │          │ - Mostrar    │         │   │
   │  │  │   previa     │          │   noticias   │         │   │
   │  │  │ - Aprobar    │          │   aprobadas  │         │   │
   │  │  │ - Rechazar   │          │ - Layout     │         │   │
   │  │  │ - Editar     │          │   tarjetas   │         │   │
   │  │  └──────────────┘          └──────────────┘         │   │
   │  └─────────────────────────────────────────────────────┘   │
   └─────────────────────────────────────────────────────────────┘
                             ↓
                    ┌────────────────┐
                    │ Usuario Final  │
                    │ (Lee noticias) │
                    └────────────────┘
```

---

## Componentes del Sistema

### 1. Aplicación Web de Noticias (Estado Actual - ✅ Implementado)

**Backend (Flask + SQLite)**
- Servidor REST API en Flask
- Base de datos SQLite con tabla `posts`
- Endpoints:
  - `POST /api/posts` - Crear nueva noticia publicada
  - `GET /api/posts` - Obtener todas las noticias
  - `GET /api/posts/<id>` - Obtener noticia específica
- CORS habilitado para frontend
- Validación de datos de entrada

**Frontend (Vanilla JavaScript)**
- Página principal (`index.html`) con visualización de noticias
- Diseño responsive tipo tarjetas
- Actualización automática cada 30 segundos
- CSS moderno con animaciones y estados

**Estructura de Datos - Tabla `posts`:**
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_url TEXT NOT NULL,
    image_url TEXT,
    release_date TEXT NOT NULL,
    provider TEXT,
    type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 2. Panel de Administración (A Implementar - 🔨)

**Nueva Tabla `pending_posts`:**
```sql
CREATE TABLE pending_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_url TEXT NOT NULL,
    image_url TEXT,
    release_date TEXT NOT NULL,
    provider TEXT,
    type TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Nuevos Endpoints Backend:**
- `POST /api/pending-posts` - Crear post pendiente (usado por agente)
- `GET /api/pending-posts` - Listar posts pendientes de revisión
- `PUT /api/pending-posts/<id>/approve` - Aprobar y mover a posts públicos
- `PUT /api/pending-posts/<id>/reject` - Rechazar post
- `PUT /api/pending-posts/<id>` - Editar título/resumen antes de aprobar

**Nueva Interfaz Frontend:**
- `admin.html` - Página de administración
- Vista previa de cada post pendiente con imagen
- Botones de acción: Aprobar, Rechazar, Editar
- Modal para edición inline de contenido
- Indicadores visuales de estado

---

### 3. Agente IA de Curación (A Implementar - 🔨)

**Framework: LangGraph**

El agente será implementado como un grafo de estados usando LangGraph, permitiendo flujos complejos y decisiones condicionales.

#### Módulos del Agente:

**a) telegram_monitor.py**
- **Biblioteca:** Telethon (cliente Telegram MTProto)
- **Función:** Conectar a grupo de Telegram y extraer URLs
- **Proceso:**
  1. Autenticación con API credentials (api_id, api_hash)
  2. Conectar al chat/grupo especificado
  3. Recuperar mensajes recientes
  4. Extraer todas las URLs encontradas
  5. Retornar lista de URLs con metadatos (fecha, autor, etc.)

**b) web_scraper.py**
- **Biblioteca:** Playwright (navegación con JavaScript rendering)
- **Función:** Navegar URLs y extraer contenido
- **Proceso:**
  1. Iniciar navegador headless (Chromium)
  2. Navegar a la URL
  3. Manejar popups, cookies, JavaScript dinámico
  4. Extraer contenido principal:
     - Título de la página
     - Texto principal del artículo
     - Meta tags OpenGraph (`og:title`, `og:description`, `og:image`)
     - Meta tags Twitter Card (`twitter:title`, `twitter:image`)
  5. Limpiar y estructurar el contenido
  6. Retornar diccionario con datos extraídos

**c) content_processor.py**
- **Biblioteca:** OpenAI API (GPT-4)
- **Función:** Generar resúmenes y extraer metadatos
- **Proceso:**
  1. Recibir contenido extraído del scraper
  2. Usar GPT-4 para:
     - Generar resumen conciso (2-3 líneas)
     - Extraer/mejorar título si es necesario
     - Clasificar tipo de contenido (Noticia, Artículo, Video, etc.)
  3. Determinar provider desde la URL (domain parsing)
  4. Retornar post estructurado

**d) image_handler.py**
- **Bibliotecas:** OpenAI API (DALL-E 3), requests
- **Función:** Obtener o generar imagen para el post
- **Proceso:**
  1. Verificar si hay imagen de OpenGraph/Twitter Card
  2. Validar que la URL de imagen sea accesible
  3. Si no hay imagen válida:
     - Generar prompt para DALL-E basado en título y resumen
     - Llamar a DALL-E 3 para generar imagen
     - Obtener URL de la imagen generada
  4. Retornar URL de imagen final

**e) api_client.py**
- **Biblioteca:** requests
- **Función:** Comunicarse con la API Flask
- **Proceso:**
  1. Método `create_pending_post(post_data)`
  2. Enviar POST request a `/api/pending-posts`
  3. Manejar respuestas y errores
  4. Retornar confirmación

**f) graph.py (LangGraph)**
- **Biblioteca:** LangGraph
- **Función:** Orquestar el flujo completo del agente
- **Estructura del Grafo:**

```python
StateGraph:
  - Estado: {
      urls: List[str],
      current_url: str,
      scraped_content: dict,
      processed_post: dict,
      image_url: str,
      pending_posts: List[dict]
    }

  - Nodos:
    1. monitor_telegram -> Obtener URLs del grupo
    2. scrape_url -> Para cada URL, extraer contenido
    3. process_content -> Generar resumen con IA
    4. handle_image -> Obtener/generar imagen
    5. create_pending -> Enviar a API de pending posts

  - Edges:
    - START -> monitor_telegram
    - monitor_telegram -> scrape_url (conditional: si hay URLs)
    - scrape_url -> process_content
    - process_content -> handle_image
    - handle_image -> create_pending
    - create_pending -> scrape_url (loop: siguiente URL)
    - scrape_url -> END (conditional: no más URLs)
```

**g) main.py**
- **Función:** Script principal de ejecución
- **Proceso:**
  1. Cargar configuración y variables de entorno
  2. Inicializar el grafo LangGraph
  3. Ejecutar el grafo
  4. Reportar resultados (cuántos posts creados, errores, etc.)

**h) config.py**
- **Función:** Gestión de configuración centralizada
- **Contenido:**
  - API keys (OpenAI, Telegram)
  - IDs de chat de Telegram
  - URLs del backend Flask
  - Configuraciones de Playwright

---

## Flujo de Trabajo Completo

### Fase 1: Ejecución del Agente (Manual)

1. Usuario ejecuta: `python agent/main.py`
2. Agente se conecta a Telegram y recupera mensajes con URLs
3. Para cada URL:
   - Navega con Playwright y extrae contenido
   - Busca imagen OpenGraph/Twitter Card
   - Genera resumen con GPT-4
   - Si no hay imagen, genera una con DALL-E
   - Envía el post a `/api/pending-posts`
4. Agente reporta: "X posts creados y enviados a revisión"

### Fase 2: Revisión Humana (Human-in-the-Loop)

1. Administrador abre `admin.html` en navegador
2. Ve lista de posts pendientes con:
   - Imagen de vista previa
   - Título propuesto
   - Resumen generado
   - URL original
   - Metadatos (provider, type, fecha)
3. Para cada post, el admin puede:
   - **Aprobar:** Click en "Aprobar" → se mueve a posts públicos
   - **Editar:** Click en "Editar" → modal para modificar título/resumen → guardar cambios → aprobar
   - **Rechazar:** Click en "Rechazar" → se marca como rechazado (no se publica)

### Fase 3: Publicación Automática

1. Cuando admin aprueba un post:
   - Frontend llama a `PUT /api/pending-posts/{id}/approve`
   - Backend copia el post de `pending_posts` a `posts`
   - Post ahora visible en la página pública (`index.html`)
2. Usuario final ve la noticia en la página principal

---

## Stack Tecnológico

### Backend
- **Python 3.7+**
- **Flask 3.0** - Framework web
- **flask-cors** - CORS support
- **SQLite3** - Base de datos (incluida en Python)

### Frontend
- **HTML5**
- **CSS3** (Grid, Flexbox, Custom Properties)
- **JavaScript ES6+** (Vanilla, Fetch API)

### Agente IA
- **LangGraph** - Orquestación del agente
- **Telethon** - Cliente Telegram MTProto
- **Playwright** - Automatización de navegador
- **OpenAI API** - GPT-4 (resúmenes) + DALL-E 3 (imágenes)
- **BeautifulSoup4** - Parsing HTML adicional
- **requests** - HTTP client
- **python-dotenv** - Gestión de variables de entorno

---

## Estructura de Archivos del Proyecto

```
proyecto-agentes/
├── backend/
│   ├── app.py              # Servidor Flask con todos los endpoints
│   ├── database.py         # Gestión de BD (posts + pending_posts)
│   ├── models.py           # Modelos y validación
│   └── requirements.txt    # Dependencias backend
│
├── frontend/
│   ├── index.html          # Página pública de noticias (✅ existente)
│   ├── admin.html          # Panel de administración (🔨 nuevo)
│   ├── css/
│   │   ├── styles.css      # Estilos página pública (✅ existente)
│   │   └── admin.css       # Estilos panel admin (🔨 nuevo)
│   └── js/
│       ├── app.js          # Lógica página pública (✅ existente)
│       └── admin.js        # Lógica panel admin (🔨 nuevo)
│
├── agent/                  # (🔨 TODO - Nuevo directorio)
│   ├── main.py             # Script principal del agente
│   ├── config.py           # Configuración centralizada
│   ├── graph.py            # Definición del grafo LangGraph
│   ├── telegram_monitor.py # Módulo de Telegram
│   ├── web_scraper.py      # Módulo de scraping con Playwright
│   ├── content_processor.py # Módulo de procesamiento IA
│   ├── image_handler.py    # Módulo de gestión de imágenes
│   ├── api_client.py       # Cliente HTTP para API Flask
│   ├── requirements.txt    # Dependencias del agente
│   ├── .env.example        # Template de variables de entorno
│   └── README.md           # Documentación específica del agente
│
├── .gitignore              # Archivos a ignorar por git
├── README.md               # Documentación principal del proyecto
└── claude.md               # Este archivo - Contexto para Claude
```

---

## Variables de Entorno Necesarias

```bash
# OpenAI API
OPENAI_API_KEY=sk-...

# Telegram API (obtener de https://my.telegram.org)
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=abcdef1234567890
TELEGRAM_PHONE=+34123456789  # Tu número de teléfono
TELEGRAM_CHAT_ID=-1001234567890  # ID del grupo a monitorizar

# Flask Backend
FLASK_API_URL=http://localhost:5000

# Opcional: Configuración de Playwright
HEADLESS=true
BROWSER_TIMEOUT=30000
```

---

## Estado de Implementación

### ✅ Completado

- [x] Backend Flask con API REST básica
- [x] Base de datos SQLite con tabla `posts`
- [x] Frontend público con visualización de noticias
- [x] Diseño responsive y moderno
- [x] Actualización automática de contenido
- [x] Endpoints: POST/GET posts

### 🔨 Por Implementar

**Fase 1: Extensión de la Aplicación Web**
- [ ] Actualizar `backend/database.py` con tabla `pending_posts`
- [ ] Añadir funciones CRUD para pending posts
- [ ] Actualizar `backend/app.py` con nuevos endpoints
- [ ] Crear `frontend/admin.html` (panel de administración)
- [ ] Crear `frontend/css/admin.css`
- [ ] Crear `frontend/js/admin.js`

**Fase 2: Agente IA**
- [ ] Crear estructura del directorio `agent/`
- [ ] Implementar `telegram_monitor.py`
- [ ] Implementar `web_scraper.py` con Playwright
- [ ] Implementar `content_processor.py` con OpenAI
- [ ] Implementar `image_handler.py` con DALL-E
- [ ] Implementar `api_client.py`
- [ ] Crear grafo LangGraph en `graph.py`
- [ ] Implementar `main.py`
- [ ] Configurar `config.py` y `.env.example`

**Fase 3: Documentación**
- [ ] Actualizar `README.md` principal
- [ ] Crear `agent/README.md`
- [ ] Documentar proceso de configuración de Telegram
- [ ] Añadir ejemplos de uso

---

## Casos de Uso

### Caso de Uso 1: Curación Diaria Manual

1. Por la mañana, el administrador ejecuta: `python agent/main.py`
2. El agente procesa todos los mensajes del grupo de Telegram del día anterior
3. Genera resúmenes y prepara 10 posts pendientes
4. Administrador revisa en `admin.html`
5. Aprueba 8 posts, rechaza 2
6. Los 8 posts aprobados se publican automáticamente

### Caso de Uso 2: Edición antes de Aprobar

1. Agente genera un post con título "New AI Model Released"
2. Administrador lo ve en panel y decide mejorarlo
3. Click en "Editar"
4. Cambia título a "OpenAI Lanza GPT-5: Revolución en IA"
5. Ajusta el resumen para audiencia española
6. Click en "Guardar y Aprobar"
7. Post se publica con cambios

### Caso de Uso 3: Regeneración de Imagen

1. Agente genera post con imagen genérica
2. Administrador ve que la imagen no representa bien el contenido
3. En el futuro (mejora): botón "Regenerar Imagen"
4. Sistema llama a DALL-E con nuevo prompt
5. Nueva imagen se muestra
6. Administrador aprueba

---

## Consideraciones Técnicas

### Seguridad

- API keys en variables de entorno (nunca en código)
- Validación de entrada en todos los endpoints
- Sanitización de URLs antes de navegar
- CORS configurado específicamente (no wildcard en producción)
- Autenticación de administrador (mejora futura)

### Escalabilidad

- SQLite apropiado para volumen bajo-medio (< 100k posts)
- Migración a PostgreSQL si crece (estructura compatible)
- Rate limiting para APIs externas (OpenAI, Telegram)
- Caché de imágenes (mejora futura)

### Manejo de Errores

- Reintentos automáticos para scraping fallido
- Logs detallados del agente
- Notificaciones de errores críticos
- Fallbacks para generación de contenido

### Testing

- Tests unitarios para funciones de procesamiento
- Tests de integración para endpoints API
- Mocking de APIs externas (OpenAI, Telegram)
- Tests E2E con Playwright para frontend admin

---

## Mejoras Futuras (Roadmap)

### Corto Plazo
- [ ] Autenticación de administrador con JWT
- [ ] Logs del agente con timestamps
- [ ] Persistencia de mensajes procesados (evitar duplicados)
- [ ] Notificaciones Telegram cuando hay posts pendientes

### Medio Plazo
- [ ] Ejecución automática con cron job
- [ ] Dashboard de estadísticas (posts por día, fuentes, etc.)
- [ ] Categorización automática de contenido
- [ ] Soporte para múltiples idiomas

### Largo Plazo
- [ ] Soporte para múltiples fuentes (WhatsApp, RSS, Twitter)
- [ ] Sistema de etiquetas y búsqueda
- [ ] API pública para consumo externo
- [ ] Versión mobile de admin panel
- [ ] Machine Learning para scoring de calidad de posts

---

## Comandos Útiles

### Desarrollo

```bash
# Iniciar backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app.py

# Ejecutar agente
cd agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Instalar Playwright browsers
playwright install chromium
```

### Testing

```bash
# Test API endpoints
curl http://localhost:5000/api/posts
curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","summary":"Test","source_url":"https://example.com","release_date":"2024-01-15"}'

# Test pending posts endpoint
curl http://localhost:5000/api/pending-posts
```

---

## Referencias y Recursos

### Documentación Oficial
- [Flask Documentation](https://flask.palletsprojects.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Telethon Documentation](https://docs.telethon.dev/)
- [Playwright Python](https://playwright.dev/python/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

### Tutoriales Útiles
- Obtener Telegram API credentials: https://my.telegram.org
- Configurar Telegram bot: https://core.telegram.org/bots
- Web scraping con Playwright: https://playwright.dev/python/docs/intro

---

## Notas para Claude

Este archivo sirve como contexto completo del proyecto. Cuando trabajes en este proyecto:

1. **Prioriza la arquitectura modular** - Cada componente debe ser independiente
2. **Comenta el código extensivamente** - Este proyecto será usado como referencia educativa
3. **Maneja errores gracefully** - APIs externas pueden fallar
4. **Sigue las convenciones de Python** - PEP 8, type hints, docstrings
5. **Testing es importante** - Implementa tests cuando sea posible

Cuando implementes nuevas features:
- Actualiza este documento
- Añade ejemplos de uso
- Documenta decisiones de diseño
- Considera impacto en otros módulos

---

**Última actualización:** 2024-01-15
**Versión:** 1.0.0
**Autor:** Proyecto Agentes IA
