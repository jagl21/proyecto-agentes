# News Portal - Aplicación Web de Noticias

Una aplicación web completa para gestionar y visualizar noticias, construida con Flask (backend) y JavaScript vanilla (frontend).

## Características

- **Backend REST API** con Flask y SQLite
- **Frontend responsive** con diseño moderno tipo tarjetas
- **Actualización automática** de contenido cada 30 segundos
- **Validación de datos** en el backend
- **Manejo de errores** robusto
- **Diseño mobile-first** totalmente responsive

## Estructura del Proyecto

```
proyecto-agentes/
├── backend/
│   ├── app.py              # Servidor Flask y endpoints API
│   ├── database.py         # Gestión de base de datos SQLite
│   ├── models.py           # Modelos y validación de datos
│   └── requirements.txt    # Dependencias Python
├── frontend/
│   ├── index.html          # Página principal
│   ├── css/
│   │   └── styles.css      # Estilos CSS
│   └── js/
│       └── app.js          # Lógica JavaScript
├── .gitignore
└── README.md
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

## Mejoras Futuras

- Paginación de resultados
- Búsqueda y filtrado de noticias
- Edición y eliminación de posts
- Autenticación de usuarios
- Subida de imágenes al servidor
- Caché de imágenes
- Tests unitarios y de integración

## Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

## Autor

Proyecto creado como aplicación demo para gestión de noticias.
