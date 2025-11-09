# 🤖 TL;DR News - AI-Powered News Curation Platform

> Too Long; Didn't Read? El bot lo leyó por ti.

Sistema completo de curación y publicación automatizada de contenidos con inteligencia artificial, interfaz web moderna y aprobación humana.

## 🌟 Características Principales

### 📱 Aplicación Web (SPA)
- **Single Page Application** con routing client-side (Vanilla JS)
- **Autenticación JWT** con roles de usuario (admin/viewer)
- **Panel de Administración** para revisión de contenidos (Human-in-the-Loop)
- **Diseño responsive** moderno tipo tarjetas
- **Actualización en tiempo real** cada 30 segundos
- **Dark mode ready** con variables CSS

### 🤖 Agente IA Autónomo
- **Monitorización de Telegram** en tiempo real con Telethon
- **Web Scraping inteligente** con Playwright (renderiza JavaScript)
- **Procesamiento con OpenAI GPT-4** para generar resúmenes
- **Generación de imágenes con DALL-E 3** cuando no hay disponibles
- **Orquestación con LangGraph** para flujos complejos
- **Deduplicación automática** con SQLite
- **Modos de ejecución**: Real-time (24/7) y Batch (histórico)

### 🔒 Seguridad
- Autenticación JWT con refresh tokens
- Hashing de contraseñas con bcrypt
- CORS configurado
- Validación de entrada en backend
- Sanitización de HTML en frontend

## 🏗️ Arquitectura del Sistema

```
┌─────────────┐
│  Telegram   │  📱 Mensajes con URLs
│   (Grupo)   │
└──────┬──────┘
       │
       ↓
┌──────────────────────────────────────────────────────┐
│           AGENTE IA (LangGraph Pipeline)             │
│                                                       │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │ Scrape   │ → │ Process  │ → │ Handle   │        │
│  │ URL      │   │ Content  │   │ Image    │        │
│  │(Playwrght│   │ (GPT-4)  │   │(DALL-E)  │        │
│  └──────────┘   └──────────┘   └──────────┘        │
│                                        ↓             │
│                              ┌──────────────┐       │
│                              │ Create       │       │
│                              │ Pending Post │       │
│                              │ (API)        │       │
│                              └──────────────┘       │
└────────────────────────┬─────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────┐
│          BACKEND (Flask + SQLite)                      │
│  ┌──────────────────────────────────────────────┐     │
│  │  API REST (JWT Auth)                         │     │
│  │  - /api/auth/* (login, verify)               │     │
│  │  - /api/posts/* (public posts)               │     │
│  │  - /api/pending-posts/* (admin)              │     │
│  │  - /api/users/* (user management)            │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
│  Database: SQLite                                      │
│  - users (auth)                                        │
│  - posts (published)                                   │
│  - pending_posts (awaiting approval)                   │
└───────────┬────────────────────────────────────────────┘
            │
            ↓
┌────────────────────────────────────────────────────────┐
│         FRONTEND (SPA - Vanilla JS)                    │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Login   │  │  News    │  │  Admin   │           │
│  │  Page    │  │  Feed    │  │  Panel   │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│                                                        │
│  Router: Client-side (SPAs)                           │
│  Auth: JWT stored in localStorage                     │
└────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
proyecto-agentes/
├── backend/
│   ├── app.py              # Flask server + API routes + SPA serving
│   ├── auth.py             # JWT authentication
│   ├── database.py         # SQLite operations (users, posts, pending)
│   ├── models.py           # Data models and validation
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── index.html          # SPA shell
│   ├── css/
│   │   ├── styles.css      # Public pages styling
│   │   ├── admin.css       # Admin panel styling
│   │   └── login.css       # Login page styling
│   └── js/
│       ├── router.js       # Client-side routing
│       ├── auth.js         # JWT handling
│       ├── app.js          # News page logic
│       ├── admin.js        # Admin panel logic
│       └── login.js        # Login page logic
│
├── agent/
│   ├── src/
│   │   ├── main.py                # Entry point (real-time/batch modes)
│   │   ├── graph.py               # LangGraph pipeline
│   │   ├── telegram_monitor.py   # Telegram integration
│   │   ├── web_scraper.py         # Playwright + BeautifulSoup
│   │   ├── content_processor.py  # GPT-4 summarization
│   │   ├── image_handler.py       # DALL-E image generation
│   │   ├── api_client.py          # Flask API client
│   │   ├── state_manager.py       # Deduplication with SQLite
│   │   └── config.py              # Configuration management
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── docs/
│   └── TECHNICAL_REPORT.md  # Technical architecture report
│
├── .gitignore
├── CLAUDE.md                # Complete project context
└── README.md                # This file
```

## 🚀 Instalación Rápida

### 1. Requisitos Previos
- Python 3.7+
- Node.js (opcional, para tools de desarrollo)
- Credenciales de OpenAI API
- Credenciales de Telegram API (opcional, para el agente)

### 2. Backend Setup

```bash
# Navegar a backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python app.py
```

El servidor estará en: `http://localhost:5000`

### 3. Acceso a la Aplicación

**Página Pública:**
```
http://localhost:5000/
```

**Login:**
```
http://localhost:5000/login
```

**Panel Admin (requiere login):**
```
http://localhost:5000/admin
```

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`
- ⚠️ **CAMBIAR EN PRODUCCIÓN**

### 4. Agente IA Setup (Opcional)

Ver documentación completa en [`agent/README.md`](agent/README.md)

```bash
cd agent

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar navegador Chromium para Playwright
playwright install chromium

# Configurar credenciales
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar en modo real-time (recomendado)
python main.py

# O en modo batch (procesar historial)
python main.py --batch
```

## 📖 Uso del Sistema

### Flujo de Trabajo Completo

1. **Agente IA** monitoriza Telegram → extrae URLs → procesa contenido → crea posts pendientes
2. **Admin** revisa posts en `/admin` → edita si necesario → aprueba/rechaza
3. **Público** ve noticias aprobadas en `/` → diseño tipo feed de noticias

### Panel de Administración

**Funcionalidades:**
- ✅ Ver todos los posts pendientes con vista previa
- ✅ Filtrar por estado (pendiente/aprobado/rechazado)
- ✅ Editar título y resumen antes de aprobar
- ✅ Aprobar posts (se mueven a página pública)
- ✅ Rechazar posts (se marcan como rechazados)
- ✅ Eliminar posts pendientes
- ✅ Ver estadísticas en tiempo real

### Modos del Agente

#### Real-Time Mode (Por Defecto) ⭐
```bash
python main.py
```
- Monitoriza continuamente Telegram
- Procesa URLs inmediatamente cuando llegan
- Deduplicación automática
- Ideal para producción (24/7)

#### Batch Mode
```bash
python main.py --batch
```
- Procesa historial de mensajes de Telegram
- Ejecución única (termina después de procesar)
- Útil para configuración inicial o catch-up

## 🔧 API Endpoints

### Autenticación
- `POST /api/auth/login` - Login con username/password
- `POST /api/auth/verify` - Verificar token JWT

### Posts Públicos
- `GET /api/posts` - Obtener posts publicados
- `GET /api/posts/<id>` - Obtener post específico
- `POST /api/posts` - Crear post público (admin only)

### Posts Pendientes (Admin)
- `GET /api/pending-posts` - Listar pendientes
- `POST /api/pending-posts` - Crear pendiente (agente)
- `GET /api/pending-posts/<id>` - Obtener específico
- `PUT /api/pending-posts/<id>` - Editar
- `PUT /api/pending-posts/<id>/approve` - Aprobar y publicar
- `PUT /api/pending-posts/<id>/reject` - Rechazar
- `DELETE /api/pending-posts/<id>` - Eliminar

### Usuarios (Admin)
- `GET /api/users` - Listar usuarios
- `POST /api/users` - Crear usuario
- `GET /api/users/<id>` - Obtener usuario
- `PUT /api/users/<id>` - Actualizar usuario
- `DELETE /api/users/<id>` - Eliminar usuario

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.7+**
- **Flask 3.0** - Framework web
- **SQLite3** - Base de datos
- **bcrypt** - Hashing de contraseñas
- **PyJWT** - JSON Web Tokens
- **flask-cors** - CORS support

### Frontend
- **HTML5**
- **CSS3** (Grid, Flexbox, Custom Properties, Animations)
- **JavaScript ES6+** (Vanilla, Fetch API, Async/Await)
- **SPA Architecture** con client-side routing

### Agente IA
- **LangGraph** - Orquestación de workflows
- **Telethon** - Cliente Telegram MTProto
- **Playwright** - Browser automation con JavaScript rendering
- **OpenAI API** - GPT-4 (summarization) + DALL-E 3 (images)
- **BeautifulSoup4** - HTML parsing
- **Requests** - HTTP client

## 📊 Base de Datos

### Tabla: `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabla: `posts` (Públicos)
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

### Tabla: `pending_posts` (Pendientes de Aprobación)
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
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 Características Técnicas Destacadas

### Agente IA
- **Pipeline LangGraph** para orquestación compleja
- **State Management** con SQLite para evitar duplicados
- **Playwright** con anti-detection (user agents realistas, headers, etc.)
- **BeautifulSoup** con filtrado avanzado (elimina sidebars, ads, nav)
- **Retry logic** con exponential backoff (planeado)
- **Rate limiting** (planeado)

### Web Scraping
- Renderiza JavaScript con Playwright
- Acepta cookies automáticamente
- Extrae OpenGraph y Twitter Card metadata
- Limpieza inteligente de contenido (elimina ruido)
- Extracción solo de párrafos (`<p>` tags)

### Generación de Imágenes
- Valida imágenes de OpenGraph primero
- Genera con DALL-E 3 si no hay imagen
- **Descarga y guarda localmente** en `/images/generated/`
- Prompt optimizado: "Professional editorial illustration..."
- Limpieza de títulos (elimina nombres de sitios)

### Frontend (SPA)
- Router client-side sin dependencias
- JWT en localStorage con expiración
- Auto-refresh cada 30 segundos
- Notificaciones visuales (success/error)
- Modal system para confirmaciones
- Responsive design (mobile-first)

## 🐛 Solución de Problemas

### Backend no arranca
```bash
# Verificar que el entorno virtual esté activado
which python  # Debería apuntar a venv/

# Reinstalar dependencias
pip install -r requirements.txt
```

### Login no funciona
- Verificar que la base de datos exista: `backend/posts.db`
- Probar credenciales: `admin` / `admin123`
- Revisar consola del navegador (F12) para errores

### Agente no procesa URLs
- Verificar `.env` con credenciales correctas
- Confirmar que Chromium esté instalado: `playwright install chromium`
- Revisar logs del agente en consola

### F5 en `/admin` da error 404
- **SOLUCIONADO**: El error handler 404 ahora sirve `index.html` para rutas SPA

## 📚 Documentación Adicional

- **[TECHNICAL_REPORT.md](docs/TECHNICAL_REPORT.md)** - Informe técnico detallado
- **[agent/README.md](agent/README.md)** - Guía completa del agente
- **[CLAUDE.md](CLAUDE.md)** - Contexto completo para Claude

## 🚀 Deployment (Producción)

### Consideraciones
1. **Cambiar credenciales por defecto**
2. **Usar PostgreSQL** en lugar de SQLite
3. **Configurar HTTPS** (Nginx + Let's Encrypt)
4. **Usar Gunicorn** para servir Flask
5. **Separar frontend** (Nginx, CDN)
6. **Implementar logging** estructurado
7. **Añadir monitoreo** (Sentry, Prometheus)
8. **Configurar backups** automáticos

## 🎯 Roadmap

### Corto Plazo
- [ ] Tests automatizados (Pytest + Jest)
- [ ] Logging framework (replace print statements)
- [ ] Health check endpoints
- [ ] Rate limiting para API
- [ ] Retry logic con exponential backoff

### Mediano Plazo
- [ ] Búsqueda y filtros avanzados
- [ ] Notificaciones (Email/Slack) para posts pendientes
- [ ] Analytics dashboard
- [ ] Bulk operations (aprobar/rechazar múltiple)
- [ ] Migración a PostgreSQL

### Largo Plazo
- [ ] Multi-source support (RSS, Twitter/X, Reddit)
- [ ] ML-based content quality scoring
- [ ] Scheduled publishing
- [ ] Mobile apps (React Native)
- [ ] Multi-tenant support

## 📝 Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

## 👨‍💻 Autor

Proyecto desarrollado como demostración de sistemas de agentes IA con LangGraph.

---

**TL;DR News** - Curado por IA, aprobado por humanos. 🤖✨
