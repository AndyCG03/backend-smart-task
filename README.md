```markdown
# Smart Task API

Una API REST construida con FastAPI para gestionar tareas con sistema de prioridades inteligente.

## Características

- Gestión completa de usuarios y tareas
- Sistema de categorías personalizadas
- Base de datos PostgreSQL
- API documentada automáticamente con Swagger UI
- Arquitectura escalable y mantenible

## Prerrequisitos

- Python 3.11+
- PostgreSQL 12+
- Git

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/AndyCG03/backend-smart-task
```

### 2. Configurar entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos PostgreSQL

**Opción A: Usar PostgreSQL local**

1. Instalar PostgreSQL
2. Crear base de datos:
```sql
CREATE DATABASE smart_task;
```


### 5. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/smart_task

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# App
DEBUG=true
```

### 6. Ejecutar la aplicación

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Estructura del Proyecto

```
app/
├── main.py                 # Punto de entrada de la aplicación
├── config.py              # Configuración y variables de entorno
├── database.py            # Conexión a la base de datos
├── models/
│   ├── database_models.py # Modelos de SQLAlchemy
│   └── pydantic_models.py # Schemas Pydantic para validación
└── api/
    ├── routes.py          # Router principal
    └── endpoints/         # Endpoints de la API
        ├── users.py       # Gestión de usuarios
        ├── tasks.py       # Gestión de tareas
        ├── categories.py  # Gestión de categorías
        ├── recommendations.py # Recomendaciones diarias
        ├── energy_logs.py # Registros de energía
        └── task_history.py # Historial de tareas
```

## Modelo de Datos

### Tablas Principales:

- **users**: Gestión de usuarios y preferencias
- **tasks**: Tareas con sistema de prioridad
- **categories**: Categorías personalizadas por usuario
- **daily_recommendations**: Recomendaciones diarias
- **energy_logs**: Registros de niveles de energía
- **task_history**: Historial de cambios en tareas

## Endpoints de la API

### Usuarios
- `GET /api/v1/users/` - Listar usuarios
- `GET /api/v1/users/{user_id}` - Obtener usuario específico
- `POST /api/v1/users/` - Crear usuario
- `PUT /api/v1/users/{user_id}` - Actualizar usuario

### Tareas
- `GET /api/v1/tasks/` - Listar tareas
- `GET /api/v1/tasks/{task_id}` - Obtener tarea específica
- `POST /api/v1/tasks/` - Crear tarea
- `PUT /api/v1/tasks/{task_id}` - Actualizar tarea
- `DELETE /api/v1/tasks/{task_id}` - Eliminar tarea

### Categorías
- `GET /api/v1/categories/` - Listar categorías de usuario
- `GET /api/v1/categories/{category_id}` - Obtener categoría específica
- `POST /api/v1/categories/` - Crear categoría
- `PUT /api/v1/categories/{category_id}` - Actualizar categoría
- `DELETE /api/v1/categories/{category_id}` - Eliminar categoría

### Recomendaciones
- `GET /api/v1/recommendations/` - Listar recomendaciones
- `GET /api/v1/recommendations/{recommendation_id}` - Obtener recomendación específica
- `POST /api/v1/recommendations/` - Crear recomendación
- `PUT /api/v1/recommendations/{recommendation_id}` - Actualizar recomendación
- `PUT /api/v1/recommendations/{recommendation_id}/status` - Actualizar estado

### Registros de Energía
- `GET /api/v1/energy-logs/` - Listar registros de energía
- `GET /api/v1/energy-logs/{log_id}` - Obtener registro específico
- `POST /api/v1/energy-logs/` - Crear registro
- `PUT /api/v1/energy-logs/{log_id}` - Actualizar registro
- `DELETE /api/v1/energy-logs/{log_id}` - Eliminar registro

### Historial de Tareas
- `GET /api/v1/task-history/task/{task_id}` - Historial de una tarea
- `GET /api/v1/task-history/user/{user_id}` - Historial de usuario
- `GET /api/v1/task-history/{history_id}` - Entrada específica de historial

## Documentación de la API

Una vez ejecutada la aplicación, la documentación automática estará disponible en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Ejemplos de Uso

### Crear un usuario

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
-H "Content-Type: application/json" \
-d '{
  "email": "usuario@ejemplo.com",
  "name": "Juan Pérez",
  "password": "password123",
  "energy_level": "medium"
}'
```

### Crear una tarea

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
-H "Content-Type: application/json" \
-d '{
  "title": "Completar documentación",
  "description": "Terminar el README del proyecto",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 120,
  "user_id": "uuid-del-usuario"
}'
```

## Configuración de Desarrollo

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| DATABASE_URL | URL de conexión a PostgreSQL | postgresql://postgres:password@localhost:5432/task_priority_db |
| ALLOWED_ORIGINS | Orígenes permitidos para CORS | http://localhost:3000,http://127.0.0.1:3000 |
| DEBUG | Modo debug | true |

### Dependencias Principales

- FastAPI - Framework web
- SQLAlchemy - ORM para base de datos
- PostgreSQL - Base de datos
- Uvicorn - Servidor ASGI
- Pydantic - Validación de datos

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'app.api.users'"

Eliminar el archivo `app/api/__init__.py` si existe.

### Error: "No module named 'psycopg2'"

Ejecutar:
```bash
pip install psycopg2-binary
```

### Error de conexión a la base de datos

Verificar que:
1. PostgreSQL esté ejecutándose
2. Las credenciales en `.env` sean correctas
3. La base de datos `task_priority_db` exista

### Limpiar caché de Python

```bash
# Eliminar archivos __pycache__
find . -name "__pycache__" -type d -exec rm -rf {} +
```

## Próximos Pasos

- [ ] Implementar autenticación JWT
- [ ] Agregar sistema de IA para priorización
- [ ] Implementar tests unitarios
- [ ] Configurar CI/CD
- [ ] Dockerizar la aplicación

