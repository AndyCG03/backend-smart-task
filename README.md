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

El sistema incorpora un modelo de Machine Learning para la priorización inteligente de tareas y recomendaciones personalizadas, con capacidad de aprendizaje continuo y adaptación contextual en tiempo real. El diseño prioriza la **robustez con pocos datos** y garantiza un funcionamiento inmediato desde el primer día de uso.

### Arquitectura del Sistema IA

#### Componentes Principales

1. **TaskAgent** - Motor híbrido de ML + reglas con post-procesamiento contextual
2. **Modelos de Base de Datos** - Almacenamiento de modelos y datos de entrenamiento  
3. **Endpoints ML** - API para interactuar con el sistema IA

#### Flujo de Trabajo del Agent

![Flujo de trabajo](images/TaskAgent.drawio.png)

### Arquitectura Técnica del Sistema Agent

#### Flujo de Entrenamiento del Modelo

##### 1. **Recolección de Datos**
```python
# Datos recolectados de tareas completadas
{
    "titulo": "Fix bug producción - servicio caído",
    "descripcion": "Servicio crítico no responde, resolver inmediatamente",
    "urgencia": "high",
    "impacto": "high",  
    "energia_requerida": "high",
    "duracion_estimada": 60,
    "objetivo": 3  # prioridad numérica: low=1, medium=2, high=3
}
```

##### 2. **Preprocesamiento de Características (Sin LabelEncoder)**
```python
# Características extraídas para el modelo usando mapeos fijos:
features = {
    'urgencia_encoded': 2,           # Mapeo fijo: low=0, medium=1, high=2
    'impacto_encoded': 2,            # Mapeo fijo: low=0, medium=1, high=2  
    'energia_encoded': 2,            # Mapeo fijo: low=0, medium=1, high=2
    'duracion_estimada': 60,         # Minutos estimados
    'longitud_descripcion': 58,      # Caracteres en descripción
    'tiene_urgente': 1,              # 1 si contiene "urgent", "crític"
    'tiene_bug': 1                   # 1 si contiene "bug", "fix"
}
```

> **Nota técnica**: Se usan **mapeos fijos** en lugar de `LabelEncoder` para evitar problemas de persistencia. Esto garantiza que el modelo sea 100% portable y no requiera guardar estructuras de estado adicionales.

##### 3. **Variable Objetivo: Prioridad Directa**
El modelo aprende a predecir **la prioridad deseada** en lugar de una métrica derivada:

```python
# Mapeo directo de prioridad a número
PRIORIDAD_NUM = {"low": 1, "medium": 2, "high": 3}
objetivo = PRIORIDAD_NUM.get(task.priority_level, 2)

# En caso de feedback negativo reciente, se usa actual_priority del feedback
if feedback and feedback.actual_priority:
    objetivo = PRIORIDAD_NUM.get(feedback.actual_priority, objetivo)
```

### Algoritmo de Machine Learning

#### Modelo: DecisionTreeClassifier
```python
modelo = DecisionTreeClassifier(
    max_depth=4,           # Evita overfitting con pocos datos
    random_state=42,       # Semilla para reproducibilidad  
    class_weight="balanced" # Maneja desequilibrios en prioridades
)
```

#### Características del Algoritmo:
- **Ideal para pocos datos**: Funciona bien con tan solo 3-5 tareas completadas
- **Interpretable**: Las decisiones del árbol son fáciles de entender y depurar
- **Robusto**: No requiere escalado de características ni ajustes finos
- **Eficiente**: Entrenamiento y predicción en milisegundos

### Proceso de Predicción y Post-procesamiento

#### 1. **Para tareas pendientes:**
```python
# Extraer características en tiempo real
X_pred = [
    [2, 2, 2, 60, 58, 1, 1],  # Hotfix - seguridad
    [0, 1, 1, 180, 45, 0, 0], # Refactorizar notificaciones
    [1, 2, 0, 45, 30, 0, 0]   # Revisar PR de colega
]

# Hacer predicción (prioridad: 1, 2 o 3)
predicciones = modelo.predict(X_pred)
# Resultado: [3, 1, 2]

# Aplicar post-procesamiento contextual
scores_ajustados = []
for prioridad, task in zip(predicciones, tasks):
    score_base = float(prioridad)
    ajuste = 1.0
    
    # Ajuste por deadline próximo
    if task.deadline and dias_hasta_deadline <= 1:
        ajuste *= 1.4
        
    # Ajuste por hora del día y energía
    if hora_actual >= 18 and task.energy_required == "high":
        ajuste *= 0.7
        
    scores_ajustados.append(score_base * ajuste)
```

#### 2. **Interpretación de Scores:**
- **Score 3.0+**: Tareas críticas (bugs, seguridad, deadlines vencidos)
- **Score 2.0-2.9**: Tareas importantes con impacto alto  
- **Score 1.0-1.9**: Tareas de mantenimiento o bajo impacto

### Post-procesamiento Contextual

Después de la predicción (ML o reglas), se aplica un **ajuste dinámico** basado en el contexto actual del usuario:

```python
def _post_procesamiento(self, resultados):
    hora_actual = datetime.now().hour
    
    # Ajuste por hora del día
    if hora_actual >= 18:
        if task.energy_required == "high":
            puntaje_ml *= 0.7  # Penalizar tareas exigentes al final del día
        elif task.energy_required == "low":
            puntaje_ml *= 1.3  # Favorecer tareas ligeras en la noche
            
    # Ajuste por feedback negativo reciente (últimas 24h)
    if task.id in tareas_con_feedback_negativo_24h:
        puntaje_ml *= 1.3  # El sistema subestimó esta tarea, aumentar prioridad
        
    # Ajuste por deadline
    if task.deadline:
        dias = (task.deadline - datetime.now()).days
        if dias < 0:
            puntaje_ml *= 2.5  # Deadline vencido
        elif dias == 0:
            puntaje_ml *= 2.0  # Deadline hoy
```

### Persistencia del Modelo

#### Almacenamiento en PostgreSQL:
```sql
-- Tabla ai_models
id UUID PRIMARY KEY,
user_id UUID REFERENCES users(id),
model_type VARCHAR(50),        -- "priority_predictor_v3"
model_version VARCHAR(20),     -- "3.1"
model_data BYTEA,              -- Modelo serializado con joblib
is_active BOOLEAN,             -- Modelo activo
trained_at TIMESTAMP
```

#### Serialización con Joblib:
```python
# Guardar modelo
buffer = BytesIO()
joblib.dump(modelo, buffer)
modelo_bin = buffer.getvalue()

# Cargar modelo
modelo = joblib.load(BytesIO(modelo_bin))
```

> **Ventaja clave**: Al no depender de `LabelEncoder`, el modelo guardado es **completo y autocontenido**, eliminando errores comunes de "categoría desconocida" al reiniciar el servidor.

### Sistema de Fallback con Reglas

El sistema **siempre usa reglas como base**, y solo activa el ML cuando hay suficientes datos:

```python
def predecir_prioridad_tareas(self, tasks):
    completed_count = contar_tareas_completadas()
    
    # Solo usa ML si hay ≥3 tareas completadas
    if self.modelo is not None and completed_count >= 3:
        return self._predecir_con_ml(tasks)
    else:
        return self._prioridad_por_reglas(tasks)
```

#### Reglas Inteligentes:
```python
def _prioridad_por_reglas(self, tasks):
    for task in tasks:
        puntaje = 2.0  # base medium
        
        # Ajuste por palabras clave
        if any(kw in task.title.lower() for kw in ['bug', 'fix', 'hotfix', 'seguridad']):
            puntaje = 3.0  # Siempre alta prioridad
            
        # Ajuste por metadatos  
        if task.urgency == "high":
            puntaje *= 1.4
        if task.impact == "high":
            puntaje *= 1.3
            
        # Ajuste por deadline
        if task.deadline and dias_hasta_deadline <= 1:
            puntaje *= 1.7
            
        task.puntaje_ml = puntaje
```

### Proceso de Feedback y Mejora Continua

#### 1. **Reentrenamiento automático**
El sistema **reentrena el modelo inmediatamente** cuando recibe feedback negativo:

```python
@router.post("/{task_id}/feedback")
def submit_ml_feedback(...):
    # Guardar feedback
    if not was_useful:  # Feedback negativo
        agent = TaskAgent(db, user_id)
        agent.entrenar_modelo_prioridad()  # Reentrena con datos actualizados
```

#### 2. **Impacto inmediato**
- El feedback negativo **aumenta temporalmente** la prioridad de esa tarea (1.3x) durante 24h
- El **reentrenamiento usa todos los datos históricos + el nuevo feedback**
- Se crea una **nueva versión del modelo** y se activa automáticamente

### Métricas de Evaluación

#### Validación con Datos Reales:
```python
# Resultados del demo avanzado
{
    "hotfix_score": 3.0,
    "revisar_pr_score_antes": 2.8,
    "revisar_pr_score_despues": 3.64,  # Aumentó tras feedback negativo
    "refactor_score": 2.0
}
```

#### Indicadores de Calidad:
- **Diferenciación clara**: Tareas críticas vs mantenimiento tienen scores distintos
- **Respuesta al feedback**: El sistema corrige sus errores inmediatamente  
- **Consistencia**: Mismo tipo de tarea → Score similar

### Requisitos de Datos Mínimos

#### Para Activar ML:
- **Mínimo**: 3 tareas completadas con prioridad definida
- **Óptimo**: 5+ tareas con variedad de tipos (críticas, normales, mantenimiento)
- **Ideal**: Tareas con deadlines y feedback de usuario

#### Calidad de Datos:
- Tareas con descripciones claras
- Variedad en prioridades asignadas  
- Feedback ocacional para ajuste fino

### Limitaciones y Consideraciones

#### Casos Especiales:
- **Nuevos usuarios**: Usa reglas desde el primer minuto (ML se activa tras 3 tareas completadas)
- **Tareas atípicas**: El sistema de reglas garantiza un comportamiento razonable
- **Cambios de patrones**: El reentrenamiento automático adapta el modelo gradualmente

#### Performance:
- **Entrenamiento**: ~500ms con 5-10 tareas
- **Predicción**: ~50ms por lote de tareas  
- **Almacenamiento**: ~200KB-1MB por modelo de usuario

### Endpoints de Machine Learning

#### 1. Obtener Tareas Priorizadas por ML
```http
GET /api/v1/ml_tasks/prioritized
```

**Descripción:** Obtiene las tareas pendientes ordenadas por el score de prioridad calculado por el modelo ML (incluyendo ajustes de post-procesamiento contextual).

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
  "http://localhost:8000/api/v1/ml_tasks/prioritized"
```

#### 2. Entrenar Modelo para Tarea
```http
POST /api/v1/ml_tasks/{task_id}/train
```

**Descripción:** Entrena el modelo ML cuando se completa una tarea, usando los datos reales de ejecución.

**Ejemplo:**
```bash
curl -X POST -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/ml_tasks/123e4567-e89b-12d3-a456-426614174000/train"
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
GET /api/v1/ml_tasks/{task_id}/recommended-time
```

**Descripción:** Obtiene el horario óptimo recomendado para ejecutar una tarea específica basado en su nivel de energía requerido y tipo de tarea.

**Ejemplo:**
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/ml_tasks/123e4567-e89b-12d3-a456-426614174000/recommended-time"
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
POST /api/v1/ml_tasks/{task_id}/feedback
```

**Parámetros en cuerpo (JSON):**
- `feedback_type`: Tipo de feedback (priority, schedule, completion)
- `was_useful`: Si la predicción fue útil (true/false)
- `actual_priority`: Prioridad real que tuvo la tarea (opcional)
- `actual_completion_time`: Tiempo real de completado en minutos (opcional)

**Ejemplo:**
```bash
curl -X POST \
  "http://localhost:8000/api/v1/ml_tasks/123e4567-e89b-12d3-a456-426614174000/feedback" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_type": "completion",
    "was_useful": true,
    "actual_completion_time": 35
  }'
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

#### 3. Script Principal de Simulación (`simulate3.sh`)

**Propósito:** Ejecutar un flujo completo de demostración del sistema ML con validación de aprendizaje.

**Uso:**
```bash
chmod +x simulate3.sh
./simulate3.sh
```

#### Flujo de la Simulación (`simulate3.sh`):
1. **Inicialización**: Base de datos y usuario admin
2. **Creación y completado**: 5 tareas con patrones claros  
3. **Entrenamiento**: Se activa ML tras completar 5 tareas
4. **Validación**: Se crean 3 tareas de prueba y se verifica que el modelo prioriza correctamente
5. **Feedback y mejora**: Se rechaza una predicción y se verifica que el score aumenta tras el reentrenamiento

### Características del Modelo ML

#### Algoritmos Utilizados
- **DecisionTreeClassifier** para clasificación de prioridades
- **Mapeos fijos** para variables categóricas  
- **Sistema de Reglas Inteligentes** como base permanente
- **Post-procesamiento Contextual** para adaptación en tiempo real

#### Características Consideradas
- Palabras clave en título y descripción ("bug", "urgente", "seguridad")
- Metadatos de la tarea (urgencia, impacto, energía requerida)  
- Deadline y tiempo estimado
- Feedback reciente del usuario (últimas 24h)
- Hora actual del día

### Requisitos para el Funcionamiento ML

#### Dependencias
```bash
pip install scikit-learn pandas numpy joblib
```

#### Datos Mínimos
- **3 tareas completadas** para activar el modelo ML
- Sistema de reglas **siempre disponible** desde el primer día

### Ejemplo de Flujo Completo

```bash
# 1. Inicializar sistema
python scripts/simulation/admin_init_simulation.py

# 2. Ejecutar simulación completa  
./simulate3.sh

# 3. Diagnosticar ML
./scripts/diagnosticar_ml.sh
```

### 🔁 ¿Cuándo y cómo se entrena el modelo de IA?

El sistema de inteligencia artificial se entrena **de forma intencional y basada en datos reales**, con un enfoque híbrido que combina ML y reglas.

#### 📌 ¿Qué desencadena el entrenamiento?

1. **Llamada explícita al endpoint `/train`**:  
   Puede ser invocada manualmente o automáticamente tras completar tareas.

2. **Feedback negativo del usuario** (`was_useful=false`):  
   **Dispara inmediatamente un reentrenamiento** para corregir errores.

#### 📊 ¿Con qué datos se entrena?

- **Tareas marcadas como "completed"**
- **Prioridad original** y **prioridad real** (del feedback)
- **Metadatos**: urgencia, impacto, energía requerida
- **Características derivadas**: palabras clave, deadline, duración

#### ⚙️ ¿Cómo funciona el entrenamiento?

1. **Verificación**: Solo entrena si hay ≥3 tareas completadas
2. **Preparación**: Convierte tareas a características numéricas usando **mapeos fijos**  
3. **Aprendizaje**: `DecisionTreeClassifier` predice prioridad (1, 2, o 3)
4. **Guardado**: El modelo se serializa y almacena en la base de datos

#### ⏱️ ¿Cuántos datos se necesitan?

- **Reglas**: Siempre activas (desde la primera tarea)
- **ML**: Se activa automáticamente con **3+ tareas completadas**

#### 🔍 ¿Qué pasa si no hay suficientes datos?

El sistema **nunca falla**. Usa el **sistema de reglas inteligentes** que considera:
- Palabras clave en títulos ("bug", "urgente", "seguridad")
- Niveles de urgencia e impacto  
- Deadlines próximos
- Energía requerida vs hora del día

### 🤔 ¿Por qué usamos DecisionTreeClassifier y mapeos fijos?

La elección se basa en **requisitos prácticos** para un sistema de productividad personal:

#### 🎯 Requisitos del sistema
1. **Funcionamiento inmediato**: Debe ser útil desde el primer día
2. **Robustez con pocos datos**: Muchos usuarios tendrán pocas tareas completadas
3. **Cero dependencia de estado**: No debe fallar al reiniciar el servidor
4. **Interpretabilidad**: Las decisiones deben ser lógicas y predecibles

#### ✅ Por qué DecisionTreeClassifier + mapeos fijos

- **DecisionTreeClassifier**:  
  - Funciona **con pocos datos** (3-10 ejemplos)  
  - Es **interpretable** y **no requiere escalado**  
  - **Evita overfitting** con `max_depth=3`

- **Mapeos fijos** (en lugar de LabelEncoder):  
  - **Elimina errores de persistencia** ("categoría desconocida")  
  - El modelo es **100% portable** y **autocontenido**  
  - **Nunca falla** al cargar después de un reinicio

#### 💡 Resultado en la práctica

- **Entrenamiento**: < 1 segundo con 5 tareas  
- **Predicción**: Instantánea (< 50ms)  
- **Robustez**: Funciona perfectamente tras reinicios del servidor  
- **Utilidad**: Prioridades inteligentes desde el primer día, mejorando continuamente con el uso

### Solución de Problemas ML

#### Error: "No hay suficientes datos para entrenar"
**Solución:** Completar más tareas para generar historial de entrenamiento (mínimo 2 tareas completadas).

#### Error: "Endpoints ML no disponibles"
**Solución:** Verificar que las rutas usen **`/ml_tasks/`** (con guión bajo `_`) y no `/ml-tasks/`. Verificar que las dependencias de ML estén instaladas y reiniciar el servidor.

#### Error: "Modelo no carga correctamente"
**Solución:** Ejecutar el script de diagnóstico para identificar el problema específico. Verificar permisos de base de datos y espacio de almacenamiento.

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

