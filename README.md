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

El sistema incorpora un modelo de Machine Learning para la priorización inteligente de tareas y recomendaciones personalizadas, con capacidad de aprendizaje continuo y adaptación contextual en tiempo real.

### Arquitectura del Sistema IA

#### Componentes Principales

1. **TaskAgent** - Motor principal de ML con post-procesamiento contextual
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
    "eficiencia": 1.71  # calculada automáticamente
}
```

##### 2. **Preprocesamiento de Características**
```python
# Características extraídas para el modelo:
features = {
    'urgencia_encoded': 2,           # Label Encoding: low=0, medium=1, high=2
    'impacto_encoded': 2,            # Label Encoding: low=0, medium=1, high=2  
    'energia_encoded': 2,            # Label Encoding: low=0, medium=1, high=2
    'duracion_estimada': 60,         # Minutos estimados
    'longitud_descripcion': 58,      # Caracteres en descripción
    'tiene_urgente': 1,              # 1 si contiene "urgent", "crític"
    'tiene_bug': 1                   # 1 si contiene "bug", "fix"
}
```

##### 3. **Variable Objetivo: Eficiencia**
La métrica clave que el modelo aprende a predecir:

```python
def calcular_eficiencia(task):
    # Si hay feedback de tiempo real:
    if feedback.actual_completion_time and task.estimated_duration:
        return task.estimated_duration / max(feedback.actual_completion_time, 1)
    
    # Fallback: usar prioridad como proxy
    prioridad_map = {"high": 2.0, "medium": 1.0, "low": 0.5}
    return prioridad_map.get(task.priority_level, 1.0)
```

**Interpretación de Eficiencia:**
- `> 1.0`: Se completó más rápido de lo estimado (BUENO)
- `= 1.0`: Se completó en el tiempo estimado (NEUTRO)  
- `< 1.0`: Se completó más lento de lo estimado (MALO)

### Algoritmo de Machine Learning

#### Modelo: SGDRegressor
```python
modelo = SGDRegressor(
    max_iter=1000,           # Máximo de iteraciones
    tol=1e-3,                # Tolerancia para convergencia
    random_state=42,         # Semilla para reproducibilidad
    learning_rate='adaptive', # Tasa de aprendizaje adaptativa
    eta0=0.1                 # Tasa de aprendizaje inicial
)
```

#### Características del Algoritmo:
- **Online Learning**: Aprende incrementalmente con nuevos datos
- **Eficiente en Memoria**: No necesita cargar todos los datos a la vez
- **Adaptativo**: Se ajusta automáticamente a nuevos patrones

### Proceso de Predicción y Post-procesamiento

#### 1. **Para tareas pendientes:**
```python
# Extraer características en tiempo real
X_pred = [
    [2, 2, 2, 60, 58, 1, 1],  # Tarea crítica
    [1, 1, 1, 120, 45, 0, 0]  # Tarea de mantenimiento
]

# Hacer predicción
scores_ml = modelo.predict(X_pred)
# Resultado: [17.55, 4.27]

# Aplicar post-procesamiento contextual
scores_ajustados = []
for score, task in zip(scores_ml, tasks):
    ajuste = 1.0
    if hora_actual >= 18 and task.energy_required == "high":
        ajuste = 0.7
    scores_ajustados.append(score * ajuste)
```

#### 2. **Interpretación de Scores:**
- **Alto Score (15-20)**: Tareas críticas que suelen completarse rápido
- **Medio Score (8-14)**: Tareas importantes con tiempo normal
- **Bajo Score (1-7)**: Tareas de mantenimiento que toman más tiempo

### Post-procesamiento Contextual

Después de la predicción inicial (ML o reglas), se aplica un **ajuste contextual** para adaptar las recomendaciones al momento actual del usuario:

```python
def _post_procesamiento(self, resultados):
    hora_actual = datetime.now().hour
    
    # Penalizar tareas de alta energía al final del día
    if hora_actual >= 18 and task.energy_required == "high":
        puntaje_ml *= 0.7
        
    # Favorecer tareas ligeras en la noche
    if hora_actual >= 18 and task.energy_required == "low":
        puntaje_ml *= 1.2
        
    # Impulso leve para tareas con feedback negativo reciente
    if task.id in feedback_negativo_reciente:
        puntaje_ml *= 1.1
```

**Objetivos del post-procesamiento:**
- Evitar sugerir tareas exigentes cuando el usuario probablemente está cansado
- Aprovechar momentos de alta energía para tareas críticas
- Dar seguimiento temporal a feedback reciente del usuario

### Persistencia del Modelo

#### Almacenamiento en PostgreSQL:
```sql
-- Tabla ai_models
id UUID PRIMARY KEY,
user_id UUID REFERENCES users(id),
model_type VARCHAR(50),        -- "priority_predictor_v2"
model_version VARCHAR(20),     -- "2.0"
model_data BYTEA,              -- Modelo serializado con joblib
feature_weights JSONB,         -- Pesos de características
accuracy_metrics JSONB,        -- Métricas de precisión
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

### Sistema de Fallback con Reglas

Cuando no hay suficientes datos para entrenar (< 2 tareas completadas):

```python
def _prioridad_por_reglas(self, tasks):
    prioridad_map = {"high": 3, "medium": 2, "low": 1}
    
    for task in tasks:
        puntaje = prioridad_map.get(task.priority_level, 1)
        
        # Bonus por palabras clave
        if any(word in task.title.lower() for word in ['bug', 'fix', 'crític']):
            puntaje *= 1.8
            
        # Bonus por urgencia e impacto
        if task.urgency == "high":
            puntaje *= 1.5
        if task.impact == "high":
            puntaje *= 1.3
            
        task.puntaje_ml = float(puntaje)
```

### Proceso de Feedback y Mejora Continua

#### 1. **Tipos de Feedback:**
```python
MLFeedback(
    feedback_type="priority",          # priority, schedule, completion
    was_useful=True,                   # Si la predicción fue útil
    actual_priority="high",            # Prioridad real que tuvo
    actual_completion_time=35          # Tiempo real en minutos
)
```

#### 2. **Reentrenamiento Automático:**
- Se activa cuando `was_useful=False` **(feedback negativo)**, lo que:
  1. **Dispara un reentrenamiento inmediato** del modelo con los datos actualizados
  2. **Aplica un impulso temporal** (10%) a esa tarea específica durante las próximas 24h en el post-procesamiento
- Usa todos los datos históricos + nuevo feedback
- Crea nueva versión del modelo
- Mantiene modelo anterior como backup

### Métricas de Evaluación

#### Validación con Datos Reales:
```python
# Resultados del demo avanzado
{
    "tareas_criticas_score_promedio": 17.55,
    "tareas_mantenimiento_score_promedio": 4.27,
    "diferencia": 13.28,
    "ratio_priorizacion": 4.28  # 428% más prioridad
}
```

#### Indicadores de Calidad:
- **Consistencia**: Mismo tipo de tarea → Score similar
- **Diferenciación**: Tipos diferentes → Scores diferentes  
- **Alineación con Comportamiento**: Scores reflejan patrones reales de uso

### Requisitos de Datos Mínimos

#### Para Entrenamiento Inicial:
- **Mínimo**: 2 tareas completadas
- **Óptimo**: 5+ tareas completadas
- **Ideal**: 10+ tareas con feedback de tiempo real

#### Calidad de Datos:
- Tareas con descripciones detalladas
- Tiempos reales de completado (feedback)
- Variedad en tipos de tareas
- Prioridades realistas asignadas

### Limitaciones y Consideraciones

#### Casos Edge:
- **Nuevos usuarios**: Usa sistema de reglas hasta tener datos
- **Tareas atípicas**: Pueden requerir ajuste manual
- **Cambios de patrones**: El modelo se adapta gradualmente

#### Performance:
- **Entrenamiento**: ~1-2 segundos con 10-20 tareas
- **Predicción**: ~100ms por lote de tareas
- **Almacenamiento**: ~1-5MB por modelo de usuario

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

**Flujo de la Simulación:**

1. **Inicialización:** Base de datos y usuario admin
2. **Autenticación:** Login con JWT
3. **Creación de Tareas:** Tareas con patrones de comportamiento claros (críticas vs mantenimiento)
4. **Integración ML:** 
   - Completado de tareas con tiempos reales
   - Entrenamiento del modelo
   - Validación explícita de que el modelo aprende
   - Feedback del usuario
5. **Estadísticas:** Resumen del aprendizaje con métricas de diferenciación

### Características del Modelo ML

#### Algoritmos Utilizados
- **SGDRegressor** para predicción de prioridades
- **TF-IDF Vectorizer** para análisis de texto en descripciones (reservado para futuras mejoras)
- **Label Encoding** para variables categóricas
- **Sistema de Reglas** como fallback cuando no hay datos suficientes
- **Post-procesamiento Contextual** para adaptación en tiempo real

#### Características Consideradas
- Texto de descripción y título (palabras clave)
- Nivel de urgencia e impacto
- Fecha límite y tiempo estimado
- Nivel de energía requerido
- Historial de completado del usuario
- Hora actual del día (post-procesamiento)
- Feedback reciente del usuario (post-procesamiento)

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
- Mínimo 2 tareas completadas para entrenamiento inicial
- Tareas con fechas límite para mejor precisión
- Feedback del usuario para ajuste continuo

### Ejemplo de Flujo Completo

```bash
# 1. Inicializar sistema
python scripts/simulation/admin_init_simulation.py

# 2. Ejecutar simulación completa
./simulate3.sh

# 3. Diagnosticar ML específicamente  
./scripts/diagnosticar_ml.sh

# 4. Ver documentación API
# http://localhost:8000/docs
```

### 🔁 ¿Cuándo y cómo se entrena el modelo de IA?

El sistema de inteligencia artificial **no se entrena automáticamente en segundo plano**. En cambio, el entrenamiento se **dispara de forma intencional** en dos momentos muy específicos, y siempre se basa en **datos reales de tu comportamiento** como usuario.

#### 📌 ¿Qué desencadena el entrenamiento?

El entrenamiento ocurre en **dos situaciones**:

1. **Cuando completas una tarea y envías feedback de tiempo real**  
   Si marcas una tarea como "completada" y proporcionas cuánto tiempo **realmente** te tomó terminarla (por ejemplo, estimaste 60 minutos pero tardaste 35), el sistema **puede entrenarse** si hay suficientes datos acumulados.

2. **Cuando indicas que una recomendación del sistema fue incorrecta**  
   Si el sistema te sugiere una prioridad para una tarea y tú respondes **"no fue útil"** (`was_useful=false`), esto **dispara inmediatamente un reentrenamiento**. La idea es: *"El modelo se equivocó, así que aprende de este error ahora mismo."*

En ambos casos, **tú controlas cuándo el sistema aprende**, ya sea al completar tareas con datos reales o al corregir sus errores.

#### 📊 ¿Con qué datos se entrena?

El modelo **solo se entrena con tareas que ya completaste** y que tienen **información real de ejecución**. Específicamente, necesita:

- **Tus tareas marcadas como "completed"**
- **Tiempo estimado** (el que tú asignaste al crear la tarea)
- **Tiempo real** (el que tú reportaste al completarla, a través del feedback)

Con estos datos, el sistema calcula una métrica clave llamada **"eficiencia"**:
```
Eficiencia = Tiempo estimado / Tiempo real
```

- Si completaste una tarea de 60 minutos en solo 30 minutos → Eficiencia = 2.0 ✅ (¡muy eficiente!)
- Si completaste una tarea de 30 minutos en 60 minutos → Eficiencia = 0.5 ❌ (menos eficiente)

Además, el sistema también considera:
- El **título y descripción** de la tarea (para detectar si es un "bug", "urgente", etc.)
- Los **metadatos** que asignaste (urgencia, impacto, energía requerida)
- La **prioridad original** que le diste

#### ⚙️ ¿Cómo funciona el entrenamiento paso a paso?

1. **Recopilación**: El sistema busca **todas tus tareas completadas** que tienen tiempo real registrado.
2. **Preparación**: Convierte cada tarea en un conjunto de números (características) que el modelo puede entender:
   - Código numérico para urgencia, impacto y energía
   - Números que indican si la tarea habla de "bugs" o "urgencias"
   - Duración estimada y longitud de la descripción
3. **Aprendizaje**: El modelo **SGDRegressor** analiza estas características y aprende a predecir la **"eficiencia"** esperada para tareas similares.
4. **Guardado**: Si el entrenamiento tiene éxito, el nuevo modelo se guarda en la base de datos y se activa automáticamente para futuras predicciones.

#### ⏱️ ¿Cuántos datos se necesitan?

- **Mínimo absoluto**: 2 tareas completadas con feedback de tiempo real.
- **Recomendado**: 5 o más tareas para que el modelo comience a hacer predicciones útiles.
- **Ideal**: Cuantas más tareas completes con datos reales, mejor será el modelo.

#### 🔍 ¿Qué pasa si no hay suficientes datos?

Si tienes menos de 2 tareas completadas, el sistema **no entrena ningún modelo**. En su lugar, usa un **sistema de reglas inteligentes** basado en:
- Palabras clave en el título/descripción ("bug", "urgente", "crítico")
- Los niveles de urgencia e impacto que asignaste
- La cercanía de la fecha límite

Este sistema de reglas **siempre está disponible** como plan de respaldo, asegurando que siempre recibas recomendaciones, incluso si eres un usuario nuevo.

#### 💡 En resumen

- **Tú decides cuándo el sistema aprende**: al completar tareas con tiempo real o al corregir errores.
- **El modelo se entrena solo con tu historial personal**: no usa datos de otros usuarios.
- **El objetivo es predecir qué tareas merecen prioridad** porque **tú las completas eficientemente** (rápido y bien).
- **Siempre hay un plan B**: el sistema de reglas garantiza funcionalidad desde el primer día.

¡Por supuesto! Aquí tienes una sección explicativa en el mismo estilo claro y accesible, perfecta para incluir en tu documento markdown:

---

### 🤔 ¿Por qué usamos SGDRegressor y no otro algoritmo de Machine Learning?

Al diseñar el sistema de priorización inteligente, evaluamos varias opciones de algoritmos de machine learning. Elegimos **SGDRegressor** (Stochastic Gradient Descent Regressor) no por ser el más avanzado, sino por ser el **más adecuado** para las necesidades específicas de un sistema de productividad personal. Aquí te explicamos por qué.

#### 🎯 Requisitos clave del sistema

Antes de elegir un algoritmo, definimos lo que **realmente necesitábamos**:

1. **Ligereza**: El sistema debe funcionar rápido, incluso en dispositivos con recursos limitados.
2. **Aprendizaje incremental**: Debe poder aprender de **pocos datos** (muchos usuarios tendrán solo unas pocas tareas completadas al principio).
3. **Bajo costo computacional**: El entrenamiento no debe ralentizar la aplicación ni consumir mucha memoria.
4. **Interpretabilidad parcial**: Si algo falla, debemos poder entender por qué.
5. **Personalización por usuario**: Cada usuario tiene su propio modelo, así que necesitamos algo que se pueda entrenar y guardar fácilmente miles de veces.

#### ❌ ¿Por qué NO usamos otros algoritmos?

- **Redes neuronales**: Requieren muchos datos para entrenar bien y son "cajas negras". Si el modelo se equivoca, es muy difícil entender por qué. Además, son pesadas para un sistema que debe responder en milisegundos.

- **Árboles de decisión o Random Forest**: Aunque son interpretables, **no funcionan bien con pocos datos** (menos de 10-20 ejemplos). También consumen más memoria y son más lentos para guardar/cargar.

- **Regresión lineal clásica**: Es ligera, pero **no maneja bien el aprendizaje incremental**. Cada vez que se añade un nuevo dato, hay que reentrenar todo desde cero, lo que es ineficiente.

- **Modelos basados en instancias (como K-NN)**: Requieren guardar **todos los datos históricos** en memoria para hacer predicciones, lo que no escala bien cuando un usuario tiene cientos de tareas.

#### ✅ ¿Por qué SÍ SGDRegressor?

SGDRegressor cumple **perfectamente** con todos nuestros requisitos:

- **Extremadamente ligero**: Usa muy poca memoria y CPU, ideal para entrenamientos rápidos.
- **Aprendizaje con pocos datos**: Aunque el modelo mejora con más datos, puede **empezar a aprender con solo 2-3 tareas completadas**, lo que es crucial para usuarios nuevos.
- **Entrenamiento eficiente**: Procesa los datos de forma secuencial y **no necesita cargar todo el dataset en memoria**, lo que lo hace ideal para entornos con recursos limitados.
- **Compatible con el flujo de usuario**: Cada vez que completas una tarea, el sistema puede **actualizar el modelo rápidamente** sin reiniciar todo.
- **Suficientemente potente**: Aunque es un modelo lineal, al combinarlo con **características bien diseñadas** (como "tiene_bug", "urgencia_codificada", etc.), logra capturar patrones complejos de comportamiento.
- **Fácil de guardar y cargar**: El modelo entrenado ocupa muy poco espacio (1-5 MB) y se serializa fácilmente con `joblib`, lo que permite almacenarlo en la base de datos sin problemas.

#### 💡 Analogía simple

Piensa en SGDRegressor como un **estudiante muy eficiente**:
- No necesita leer cientos de libros para aprender (pocos datos bastan).
- Aprende de cada experiencia nueva inmediatamente.
- No ocupa mucho espacio en su escritorio (bajo consumo de memoria).
- Puede explicar sus decisiones en términos simples ("le doy más prioridad a las tareas con 'bug' porque históricamente las completas rápido").

En cambio, otros algoritmos serían como estudiantes que necesitan una biblioteca completa, mucho tiempo de estudio y espacio de trabajo, lo que no es práctico para un sistema de productividad personal.

#### 📊 Resultado en la práctica

Gracias a esta elección:
- El **entrenamiento toma menos de 2 segundos** incluso en servidores modestos.
- La **predicción es casi instantánea** (menos de 100ms para decenas de tareas).
- El sistema **empieza a ser útil desde el primer día**, sin necesidad de un largo período de "entrenamiento inicial".
- El **consumo de recursos es mínimo**, permitiendo ejecutar el sistema en casi cualquier entorno.

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

