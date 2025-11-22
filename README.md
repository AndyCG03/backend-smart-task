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

**Crear Usuario Administrador**

El sistema incluye un script para crear usuarios administradores:

```bash
# Ejecutar el script de creación de administrador
python scripts/admin_init.py


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

## Sistema de Inteligencia Artificial

El sistema incorpora un modelo de Machine Learning para la priorización inteligente de tareas y recomendaciones personalizadas.

### Arquitectura del Sistema IA

#### Componentes Principales

1. **TaskAgent** - Motor principal de ML
2. **Modelos de Base de Datos** - Almacenamiento de modelos y datos de entrenamiento
3. **Endpoints ML** - API para interactuar con el sistema IA

#### Flujo de Trabajo del ML

```
Tareas Completadas → Entrenamiento → Modelo ML → Predicción → Priorización
     ↑                                      ↓
  Feedback ←─────── Evaluación ←─────── Recomendaciones
```

### Endpoints de Machine Learning

#### 1. Obtener Tareas Priorizadas por ML
```http
GET /api/v1/ml-tasks/prioritized
```

**Descripción:** Obtiene las tareas pendientes ordenadas por el score de prioridad calculado por el modelo ML.

**Ejemplo de respuesta:**
```json
[
  {
    "id": "uuid-tarea",
    "title": "Enviar reporte trimestral",
    "priority_level": "high",
    "ml_priority_score": 4.2,
    "estimated_duration": 120,
    "urgency": "high",
    "impact": "high"
  }
]
```

**Uso:**
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/ml-tasks/prioritized"
```

#### 2. Entrenar Modelo para Tarea
```http
POST /api/v1/ml-tasks/{task_id}/train
```

**Descripción:** Entrena el modelo ML cuando se completa una tarea, usando los datos reales de ejecución.

**Ejemplo:**
```bash
curl -X POST -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/ml-tasks/123e4567-e89b-12d3-a456-426614174000/train"
```

**Respuesta:**
```json
{
  "message": "Modelo actualizado exitosamente",
  "trained": true
}
```

#### 3. Obtener Horario Recomendado
```http
GET /api/v1/ml-tasks/{task_id}/recommended-time
```

**Descripción:** Obtiene el horario óptimo recomendado para ejecutar una tarea específica.

**Ejemplo:**
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/ml-tasks/123e4567-e89b-12d3-a456-426614174000/recommended-time"
```

**Respuesta:**
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "recommended_time": "08:00",
  "message": "Horario recomendado: 08:00"
}
```

#### 4. Enviar Feedback ML
```http
POST /api/v1/ml-tasks/{task_id}/feedback
```

**Parámetros Query:**
- `feedback_type`: Tipo de feedback (priority, schedule, completion)
- `was_useful`: Si la predicción fue útil (true/false)
- `actual_priority`: Prioridad real que tuvo la tarea
- `actual_completion_time`: Tiempo real de completado en minutos

**Ejemplo:**
```bash
curl -X POST \
  "http://localhost:8000/api/v1/ml-tasks/123e4567-e89b-12d3-a456-426614174000/feedback?feedback_type=priority&was_useful=true&actual_priority=high&actual_completion_time=90" \
  -H "Authorization: Bearer {token}"
```

**Respuesta:**
```json
{
  "message": "Feedback registrado exitosamente"
}
```

### Scripts de Simulación y Diagnóstico

#### 1. Script de Diagnóstico ML (`scripts/diagnosticar_ml.sh`)

**Propósito:** Verificar el funcionamiento de todos los endpoints ML y diagnosticar problemas.

**Uso:**
```bash
chmod +x scripts/diagnosticar_ml.sh
./scripts/diagnosticar_ml.sh
```

**Funcionalidades:**
- Verifica autenticación
- Prueba todos los endpoints ML
- Muestra scores de priorización
- Detecta problemas de configuración

#### 2. Script de Inicialización de Simulación (`scripts/simulation/admin_init_simulation.py`)

**Propósito:** Inicializar la base de datos con datos de prueba y usuario administrador.

**Uso:**
```bash
python scripts/simulation/admin_init_simulation.py
```

**Funcionalidades:**
- Crea tablas de base de datos
- Genera usuario administrador
- Crea categorías de ejemplo
- Genera tareas de entrenamiento inicial

**Credenciales por defecto:**
- Email: `admin@taskapp.com`
- Contraseña: `Admin123!`

#### 3. Script Principal de Simulación (`scripts/simulation/simulation.sh`)

**Propósito:** Ejecutar un flujo completo de demostración del sistema.

**Uso:**
```bash
chmod +x scripts/simulation/simulation.sh
./scripts/simulation/simulation.sh
```

**Flujo de la Simulación:**
1. **Inicialización:** Base de datos y usuario admin
2. **Servidor:** Verifica/inicia servidor FastAPI
3. **Autenticación:** Login con JWT
4. **Creación de Tareas:** 6 tareas de ejemplo con diferentes prioridades
5. **Integración ML:** 
   - Priorización inteligente
   - Completado de tareas
   - Entrenamiento del modelo
   - Recomendaciones de horario
   - Feedback del usuario
6. **Estadísticas:** Resumen del flujo completado

### Características del Modelo ML

#### Algoritmos Utilizados
- **SGDRegressor** para predicción de prioridades
- **TF-IDF Vectorizer** para análisis de texto en descripciones
- **Label Encoding** para variables categóricas
- **Sistema de Reglas** como fallback cuando no hay datos suficientes

#### Características Consideradas
- Texto de descripción y título
- Nivel de urgencia e impacto
- Fecha límite y tiempo estimado
- Nivel de energía requerido
- Historial de completado del usuario

#### Persistencia del Modelo
Los modelos entrenados se almacenan en la base de datos PostgreSQL en la tabla `ai_models`, permitiendo:
- Recuperación después de reinicios
- Múltiples versiones de modelos
- Activación/desactivación de modelos

### Requisitos para el Funcionamiento ML

#### Dependencias
```bash
pip install scikit-learn pandas numpy joblib
```

#### Datos Mínimos
- Mínimo 3-5 tareas completadas para entrenamiento inicial
- Tareas con fechas límite para mejor precisión
- Feedback del usuario para ajuste continuo

### Ejemplo de Flujo Completo

```bash
# 1. Inicializar sistema
python scripts/simulation/admin_init_simulation.py

# 2. Ejecutar simulación completa
./scripts/simulation/simulation.sh

# 3. Diagnosticar ML específicamente  
./scripts/diagnosticar_ml.sh

# 4. Ver documentación API
# http://localhost:8000/docs
```

### Solución de Problemas ML

#### Error: "No hay suficientes datos para entrenar"
**Solución:** Completar más tareas para generar historial de entrenamiento.

#### Error: "Endpoints ML no disponibles"
**Solución:** Verificar que las dependencias de ML estén instaladas y reiniciar el servidor.

#### Error: "Modelo no carga correctamente"
**Solución:** Ejecutar el script de diagnóstico para identificar el problema específico.



## Configuración de Desarrollo

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| DATABASE_URL | URL de conexión a PostgreSQL | postgresql://postgres:password@localhost:5432/smart_task |
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
3. La base de datos `smart_task` exista

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

