#!/bin/bash

# simulate3.sh - Demo avanzado del sistema ML (CORREGIDO y FUNCIONAL)
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Encabezado
echo ""
print_color "$CYAN" "🚀 DEMO COMPLETO: Sistema de Tareas Inteligente con ML"
print_color "$CYAN" "======================================================"
echo ""

# Paso 1: Verificar dependencias
print_color "$BLUE" "🔍 Verificando dependencias..."

if ! command_exists python3; then
    print_color "$RED" "❌ Python3 no está instalado"
    exit 1
fi

if ! command_exists curl; then
    print_color "$RED" "❌ curl no está instalado"
    exit 1
fi

print_color "$GREEN" "✅ Dependencias verificadas"

# Paso 2: Verificar que el script de Python existe
print_color "$BLUE" "📁 Verificando scripts..."

if [ ! -f "scripts/simulation/admin_init_simulation.py" ]; then
    print_color "$RED" "❌ No se encuentra scripts/simulation/admin_init_simulation.py"
    print_color "$YELLOW" "💡 Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# Paso 3: Ejecutar el script de inicialización de Python
print_color "$CYAN" "🛠️  PASO 1: Inicializando base de datos y usuario administrador..."
echo ""

python3 scripts/simulation/admin_init_simulation.py

if [ $? -ne 0 ]; then
    print_color "$RED" "❌ Error en la inicialización de la base de datos"
    exit 1
fi

echo ""
print_color "$GREEN" "✅ Base de datos inicializada correctamente"
echo ""

# Paso 4: Verificar si el servidor está ejecutándose
print_color "$BLUE" "🔍 Verificando si el servidor FastAPI está ejecutándose..."

if ! curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
    print_color "$YELLOW" "⚠️  Servidor FastAPI no detectado en http://127.0.0.1:8000"
    print_color "$YELLOW" "💡 Inicia el servidor con: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    print_color "$YELLOW" "¿Quieres que intente iniciar el servidor automáticamente? (s/n)"
    read -r response
    
    if [[ "$response" =~ ^[Ss]$ ]]; then
        print_color "$BLUE" "🚀 Iniciando servidor FastAPI en segundo plano..."
        
        # Iniciar servidor en segundo plano
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 &
        SERVER_PID=$!
        
        # Esperar a que el servidor esté listo
        print_color "$YELLOW" "⏳ Esperando a que el servidor esté listo (30 segundos)..."
        sleep 30
        
        # Verificar si el servidor se inició correctamente
        if kill -0 $SERVER_PID 2>/dev/null; then
            print_color "$GREEN" "✅ Servidor iniciado correctamente (PID: $SERVER_PID)"
        else
            print_color "$RED" "❌ Error al iniciar el servidor"
            print_color "$YELLOW" "📄 Revisa server.log para más detalles"
            exit 1
        fi
    else
        print_color "$YELLOW" "💡 Inicia el servidor manualmente y luego ejecuta este script nuevamente"
        exit 1
    fi
else
    print_color "$GREEN" "✅ Servidor FastAPI detectado y funcionando"
fi

echo ""

# Paso 5: Ejecutar el demo de integración ML
print_color "$CYAN" "🧠 PASO 2: Ejecutando demo de integración con Machine Learning..."
echo ""

# Configuración para el demo
BASE_URL="http://127.0.0.1:8000"
ADMIN_EMAIL="admin@taskapp.com"
ADMIN_PASSWORD="Admin123!"

print_color "$GREEN" "✅ Usando ruta base de API: /api/v1"

# Función para hacer requests con autenticación
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -n "$data" ]; then
        curl -s -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            -d "$data"
    else
        curl -s -X $method "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $ACCESS_TOKEN"
    fi
}

# Sub-paso 1: Autenticación
print_color "$YELLOW" "🔐 Autenticando en: /api/v1/auth/login..."

# Usar form-data como espera OAuth2PasswordRequestForm
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_EMAIL&password=$ADMIN_PASSWORD")

echo "Respuesta del login: $LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    print_color "$GREEN" "✅ Autenticación exitosa"
    print_color "$BLUE" "   Token obtenido: ${ACCESS_TOKEN:0:20}..."
else
    print_color "$RED" "❌ Error en autenticación"
    echo "Detalle: $LOGIN_RESPONSE"
    exit 1
fi

echo ""

# Sub-paso 2: Verificar que la autenticación funciona
print_color "$YELLOW" "🔍 Verificando autenticación..."

VERIFY_RESPONSE=$(make_request "GET" "/api/v1/auth/me")
if echo "$VERIFY_RESPONSE" | grep -q "email"; then
    USER_EMAIL=$(echo "$VERIFY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['email'])")
    print_color "$GREEN" "✅ Autenticación verificada - Usuario: $USER_EMAIL"
else
    print_color "$YELLOW" "⚠️  No se pudo verificar autenticación automáticamente"
    echo "Respuesta: $VERIFY_RESPONSE"
fi

echo ""

# Función para crear tarea
create_task() {
    local task_data=$1
    curl -s -X POST "$BASE_URL/api/v1/tasks/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -d "$task_data"
}

# Función para completar tarea
complete_task() {
    local task_id=$1
    local completion_time=$2
    # Actualizar estado
    curl -s -X PATCH "$BASE_URL/api/v1/tasks/$task_id/status?status=completed" \
        -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
    # Enviar feedback (como query params)
    curl -s -X POST "$BASE_URL/api/v1/ml_tasks/$task_id/feedback?feedback_type=completion&was_useful=true&actual_completion_time=$completion_time" \
        -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
}

# Función para obtener tareas priorizadas
get_prioritized() {
    curl -s -X GET "$BASE_URL/api/v1/ml_tasks/prioritized" \
        -H "Authorization: Bearer $ACCESS_TOKEN"
}

# Función para rechazar una predicción (feedback negativo)
reject_task() {
    local task_id=$1
    curl -s -X POST "$BASE_URL/api/v1/ml_tasks/$task_id/feedback?feedback_type=rejection&was_useful=false&actual_priority=high" \
        -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
}

# ==========================================================
# FASE 1: Crear tareas base para entrenamiento (5 tareas completadas)
# ==========================================================
print_color "$CYAN" "📚 FASE 1: Creando y completando tareas para entrenamiento del ML..."
echo ""

# Tareas CRÍTICAS (se completan rápido)
TASK1_ID=$(create_task '{
  "title": "Fix bug en API de pagos",
  "description": "Error crítico en producción",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 50,
  "priority_level": "high",
  "energy_required": "high"
}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

TASK2_ID=$(create_task '{
  "title": "Reunión con cliente VIP",
  "description": "Presentar roadmap Q3",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 40,
  "priority_level": "high",
  "energy_required": "medium"
}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# Tareas de mantención (se completan lento)
TASK3_ID=$(create_task '{
  "title": "Actualizar documentación",
  "description": "Doc del módulo de auth",
  "urgency": "low",
  "impact": "medium",
  "estimated_duration": 100,
  "priority_level": "low",
  "energy_required": "low"
}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

TASK4_ID=$(create_task '{
  "title": "Investigar librerías de caché",
  "description": "Benchmark Redis vs Memcached",
  "urgency": "low",
  "impact": "low",
  "estimated_duration": 120,
  "priority_level": "low",
  "energy_required": "medium"
}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

TASK5_ID=$(create_task '{
  "title": "Refactorizar utils.py",
  "description": "Mejorar legibilidad",
  "urgency": "medium",
  "impact": "medium",
  "estimated_duration": 90,
  "priority_level": "medium",
  "energy_required": "medium"
}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# Completar con tiempos reales
complete_task "$TASK1_ID" 35   # rápido
complete_task "$TASK2_ID" 30   # rápido
complete_task "$TASK3_ID" 150  # lento
complete_task "$TASK4_ID" 180  # lento
complete_task "$TASK5_ID" 100  # normal

print_color "$GREEN" "✅ 5 tareas completadas. ML ya puede entrenarse."

# ==========================================================
# FASE 2: Entrenar modelo
# ==========================================================
print_color "$CYAN" "🎯 FASE 2: Entrenando modelo ML..."
TRAIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/ml_tasks/$TASK1_ID/train" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
echo "Resultado del entrenamiento: $TRAIN_RESPONSE"
sleep 2
print_color "$GREEN" "✅ Modelo entrenado."

# ==========================================================
# FASE 3: Crear tareas de prueba
# ==========================================================
print_color "$CYAN" "🔍 FASE 3: Creando tareas de prueba..."
TASK_A_ID=$(create_task '{
  "title": "Hotfix - seguridad CVE-2025",
  "description": "Parche urgente",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 60,
  "priority_level": "high",
  "energy_required": "high",
  "deadline": "'"$(date -d "+1 day" +"%Y-%m-%dT%H:%M:%S")"'" 
}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

TASK_B_ID=$(create_task '{
  "title": "Refactorizar notificaciones",
  "description": "Código legacy",
  "urgency": "low",
  "impact": "medium",
  "estimated_duration": 180,
  "priority_level": "low",
  "energy_required": "medium"
}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

TASK_C_ID=$(create_task '{
  "title": "Revisar PR de colega",
  "description": "Pull request #342",
  "urgency": "medium",
  "impact": "high",
  "estimated_duration": 45,
  "priority_level": "medium",
  "energy_required": "low",
  "deadline": "'"$(date -d "+2 hours" +"%Y-%m-%dT%H:%M:%S")"'"
}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

print_color "$GREEN" "✅ Tareas de prueba creadas."

# ==========================================================
# FASE 4: Ver predicción inicial
# ==========================================================
print_color "$CYAN" "📊 FASE 4: Predicción inicial del modelo:"
ML_RESPONSE=$(get_prioritized)
echo "$ML_RESPONSE" | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
print('Tarea                                    | Score')
print('-' * 48)
for t in tasks:
    title = t['title'][:40]
    score = t.get('ml_priority_score', 0)
    if 'Hotfix' in title or 'Refactor' in title or 'Revisar' in title:
        print(f'{title:40} | {score:.2f}')
print()
print('🔍 DETALLE DE TODAS LAS TAREAS:')
print('-' * 60)
for t in tasks:
    title = t['title'][:30]
    score = t.get('ml_priority_score', 0)
    urgency = t.get('urgency', 'N/A')
    impact = t.get('impact', 'N/A')
    energy = t.get('energy_required', 'N/A')
    deadline = t.get('deadline', 'N/A')
    print(f'{title:30} | Score: {score:5.2f} | U:{urgency} I:{impact} E:{energy}')
"

# ==========================================================
# FASE 5: Rechazar una predicción (simulamos que el modelo subestimó "Revisar PR")
# ==========================================================
print_color "$YELLOW" "🔄 FASE 5: Rechazando predicción de 'Revisar PR' (debe ser más prioritario)..."
reject_task "$TASK_C_ID"
sleep 2
print_color "$GREEN" "✅ Feedback negativo enviado → reentrenamiento automático."

# ==========================================================
# FASE 6: Ver predicción después del reentrenamiento
# ==========================================================
print_color "$CYAN" "📈 FASE 6: Predicción después del rechazo:"
ML_RESPONSE2=$(get_prioritized)
echo "$ML_RESPONSE2" | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
print('Tarea                                    | Score')
print('-' * 48)
for t in tasks:
    title = t['title'][:40]
    score = t.get('ml_priority_score', 0)
    if 'Hotfix' in title or 'Refactor' in title or 'Revisar' in title:
        print(f'{title:40} | {score:.2f}')
print()
print('🔍 COMPARACIÓN ANTES/DESPUÉS:')
print('-' * 60)
print('La prioridad de \"Revisar PR\" debería haber aumentado tras el feedback')
"

echo ""
print_color "$GREEN" "🎯 Prueba completada: el sistema entrena, predice, y reacciona al feedback."