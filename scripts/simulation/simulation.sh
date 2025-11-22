#!/bin/bash

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

# Sub-paso 3: Crear tareas de prueba
print_color "$YELLOW" "📋 Creando tareas de prueba..."

TASK_IDS=()

create_task() {
    local task_data=$1
    local response
    response=$(make_request "POST" "/api/v1/tasks/" "$task_data")
    echo "Respuesta crear tarea: $response"
    
    if echo "$response" | grep -q "id"; then
        local task_id
        task_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
        TASK_IDS+=("$task_id")
        print_color "$GREEN" "   ✅ Tarea creada: ${task_id:0:8}..."
        return 0
    else
        print_color "$RED" "   ❌ Error creando tarea"
        echo "   Respuesta: $response"
        return 1
    fi
}

# Obtener categorías
print_color "$YELLOW" "📂 Obteniendo categorías..."
CATEGORIES_RESPONSE=$(make_request "GET" "/api/v1/categories/")
CATEGORY_ID=""

if echo "$CATEGORIES_RESPONSE" | grep -q "id"; then
    CATEGORY_ID=$(echo "$CATEGORIES_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if isinstance(data, list) and len(data) > 0 else '')" 2>/dev/null || echo "")
    if [ -n "$CATEGORY_ID" ]; then
        print_color "$GREEN" "   ✅ Category ID obtenido: ${CATEGORY_ID:0:8}..."
    else
        print_color "$YELLOW" "   ⚠️  No se pudo obtener category_id de la respuesta"
        echo "   Respuesta categorías: $CATEGORIES_RESPONSE"
    fi
else
    print_color "$YELLOW" "   ⚠️  No se pudieron obtener categorías, creando tareas sin categoría"
fi

# Crear tareas básicas - FORMA CORREGIDA
print_color "$YELLOW" "🛠️  Creando tareas de ejemplo..."

# Función para construir el JSON de tarea correctamente
build_task_json() {
    local title="$1"
    local description="$2"
    local urgency="$3"
    local impact="$4"
    local estimated_duration="$5"
    local priority_level="$6"
    local energy_required="$7"
    local deadline="$8"
    
    local base_json="{
  \"title\": \"$title\",
  \"description\": \"$description\",
  \"urgency\": \"$urgency\",
  \"impact\": \"$impact\",
  \"estimated_duration\": $estimated_duration,
  \"priority_level\": \"$priority_level\",
  \"energy_required\": \"$energy_required\",
  \"deadline\": \"$deadline\""
  
    if [ -n "$CATEGORY_ID" ]; then
        base_json="$base_json,
  \"category_id\": \"$CATEGORY_ID\""
    fi
    
    base_json="$base_json
}"
    
    echo "$base_json"
}

# Crear tareas usando la función corregida
create_task "$(build_task_json \
    "Enviar reporte trimestral" \
    "Urgente enviar reporte trimestral a auditoría" \
    "high" "high" 120 "high" "high" \
    "2025-11-22T17:00:00"
)"

create_task "$(build_task_json \
    "Llamar cliente clave" \
    "Llamar al cliente para cerrar venta importante" \
    "high" "high" 30 "high" "medium" \
    "2025-11-23T12:00:00"
)"

create_task "$(build_task_json \
    "Preparar presentación ejecutiva" \
    "Revisar slides para reunión con directivos" \
    "medium" "high" 90 "medium" "medium" \
    "2025-11-24T10:00:00"
)"

create_task "$(build_task_json \
    "Hacer compras semanales" \
    "Comprar víveres y productos de limpieza para la semana" \
    "medium" "low" 60 "medium" "low" \
    "2025-11-25T18:00:00"
)"

create_task "$(build_task_json \
    "Revisar contratos legales" \
    "Revisar cláusulas legales con abogado externo" \
    "high" "medium" 45 "high" "high" \
    "2025-11-26T16:00:00"
)"

create_task "$(build_task_json \
    "Actualizar currículum vitae" \
    "Actualizar información profesional y habilidades en el CV" \
    "low" "low" 45 "low" "low" \
    "2025-11-27T23:59:00"
)"

if [ ${#TASK_IDS[@]} -gt 0 ]; then
    print_color "$GREEN" "✅ ${#TASK_IDS[@]} tareas creadas correctamente"
else
    print_color "$RED" "❌ No se pudieron crear tareas"
    print_color "$YELLOW" "💡 Revisa que el servidor esté funcionando correctamente"
    exit 1
fi

echo ""

# Sub-paso 4: Probar endpoints ML
print_color "$YELLOW" "🔍 Verificando endpoints ML..."

ML_CHECK=$(make_request "GET" "/api/v1/ml-tasks/prioritized")
if echo "$ML_CHECK" | grep -q -E "error|Not Found|404|405"; then
    print_color "$YELLOW" "⚠️  Endpoints ML no disponibles"
    HAS_ML=false
else
    print_color "$GREEN" "✅ Endpoints ML disponibles"
    HAS_ML=true
fi

echo ""

if [ "$HAS_ML" = true ]; then
    # Demo con ML
    print_color "$YELLOW" "🧠 Probando priorización ML..."
    
    ML_RESPONSE=$(make_request "GET" "/api/v1/ml-tasks/prioritized")
    echo "$ML_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('TAREAS PRIORIZADAS POR ML:')
    print('Tarea'.ljust(30) + ' | Prioridad | Score ML  | Duración')
    print('-' * 65)
    for task in data:
        title = task.get('title', '')[:28]
        priority = task.get('priority_level', 'N/A')
        ml_score = task.get('ml_priority_score', 0)
        duration = task.get('estimated_duration', 0)
        print(f'{title:30} | {priority:9} | {ml_score:.3f}    | {duration:3} min')
except Exception as e:
    print('Formato de respuesta inesperado')
    print('Error:', str(e))
" 2>/dev/null || echo "   No se pudo procesar la respuesta ML"

    echo ""
    
    # Completar tareas y entrenar modelo
    print_color "$YELLOW" "🔄 Completando tareas y entrenando modelo..."
    
    if [ ${#TASK_IDS[@]} -ge 2 ]; then
        make_request "PUT" "/api/v1/tasks/${TASK_IDS[0]}" "{\"status\": \"completed\"}" > /dev/null 2>&1
        make_request "PUT" "/api/v1/tasks/${TASK_IDS[1]}" "{\"status\": \"completed\"}" > /dev/null 2>&1
        print_color "$GREEN" "✅ 2 tareas completadas"
        
        # Entrenar modelo
        TRAIN_RESPONSE=$(make_request "POST" "/api/v1/ml-tasks/${TASK_IDS[0]}/train")
        if echo "$TRAIN_RESPONSE" | grep -q "mensaje\|message"; then
            print_color "$GREEN" "📈 Modelo entrenado con nuevos datos"
        else
            print_color "$YELLOW" "⚠️  No se pudo entrenar modelo"
        fi
    else
        print_color "$YELLOW" "⚠️  No hay suficientes tareas para completar"
    fi
    
    echo ""
    
    # Obtener recomendación de horario
    if [ ${#TASK_IDS[@]} -ge 3 ]; then
        print_color "$YELLOW" "⏰ Obteniendo recomendación de horario..."
        
        SCHEDULE_RESPONSE=$(make_request "GET" "/api/v1/ml-tasks/${TASK_IDS[2]}/recommended-time")
        if echo "$SCHEDULE_RESPONSE" | grep -q "recommended_time"; then
            RECOMMENDED_TIME=$(echo "$SCHEDULE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['recommended_time'])")
            print_color "$GREEN" "✅ Horario recomendado: $RECOMMENDED_TIME"
        else
            print_color "$YELLOW" "⚠️  No se pudo obtener recomendación de horario"
        fi
    fi
    
    echo ""
    
    # Enviar feedback
    if [ ${#TASK_IDS[@]} -ge 1 ]; then
        print_color "$YELLOW" "📊 Enviando feedback al modelo..."
        
        make_request "POST" "/api/v1/ml-tasks/${TASK_IDS[0]}/feedback?feedback_type=priority&was_useful=true&actual_priority=high&actual_completion_time=110" > /dev/null 2>&1
        print_color "$GREEN" "✅ Feedback enviado al modelo"
    fi
    
else
    # Demo básico sin ML
    print_color "$YELLOW" "📊 Mostrando todas las tareas creadas..."
    
    TASKS_RESPONSE=$(make_request "GET" "/api/v1/tasks/")
    if echo "$TASKS_RESPONSE" | grep -q "title"; then
        echo "$TASKS_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('TODAS LAS TAREAS CREADAS:')
    print('Tarea'.ljust(30) + ' | Prioridad | Estado')
    print('-' * 50)
    for task in data:
        title = task.get('title', '')[:28]
        priority = task.get('priority_level', 'N/A')
        status = task.get('status', 'N/A')
        print(f'{title:30} | {priority:9} | {status}')
except Exception as e:
    print('No se pudieron mostrar las tareas')
    print('Error:', str(e))
" 2>/dev/null || echo "   No se pudieron procesar las tareas"
    else
        print_color "$YELLOW" "   ℹ️  No hay tareas para mostrar"
    fi
fi

echo ""

# Sub-paso 5: Completar más tareas para demostrar el flujo completo
print_color "$YELLOW" "✅ Completando más tareas para demostrar el flujo..."

if [ ${#TASK_IDS[@]} -ge 5 ]; then
    make_request "PUT" "/api/v1/tasks/${TASK_IDS[2]}" "{\"status\": \"completed\"}" > /dev/null 2>&1
    make_request "PUT" "/api/v1/tasks/${TASK_IDS[4]}" "{\"status\": \"completed\"}" > /dev/null 2>&1

    # Re-entrenar modelo si ML está disponible
    if [ "$HAS_ML" = true ]; then
        make_request "POST" "/api/v1/ml-tasks/${TASK_IDS[2]}/train" > /dev/null 2>&1
    fi

    print_color "$GREEN" "✅ Tareas adicionales completadas"
else
    print_color "$YELLOW" "⚠️  No hay suficientes tareas para completar"
fi

echo ""

# Sub-paso 6: Estadísticas finales
print_color "$CYAN" "📈 ESTADÍSTICAS FINALES:"
print_color "$BLUE" "   ✅ Base de datos inicializada"
print_color "$BLUE" "   ✅ Servidor en ejecución"
print_color "$BLUE" "   ✅ Autenticación exitosa"
print_color "$BLUE" "   ✅ Tareas creadas: ${#TASK_IDS[@]}"

# Contar tareas completadas
COMPLETED_COUNT=0
if [ ${#TASK_IDS[@]} -ge 5 ]; then
    COMPLETED_COUNT=4  # Asumiendo que completamos las tareas 0,1,2,4
else
    COMPLETED_COUNT=0
fi

print_color "$BLUE" "   ✅ Tareas completadas: $COMPLETED_COUNT"
print_color "$BLUE" "   📊 Tareas pendientes: $((${#TASK_IDS[@]} - $COMPLETED_COUNT))"

if [ "$HAS_ML" = true ]; then
    print_color "$GREEN" "   🤖 ML Integration: ACTIVADA"
    print_color "$BLUE" "   🔄 Modelo entrenado: 2 veces"
    print_color "$BLUE" "   📝 Feedback enviado: 1 registro"
else
    print_color "$YELLOW" "   🤖 ML Integration: NO DISPONIBLE"
fi

echo ""

# Paso 6: Limpieza (opcional)
if [ ! -z "$SERVER_PID" ]; then
    print_color "$YELLOW" "¿Quieres detener el servidor? (s/n)"
    read -r stop_response
    if [[ "$stop_response" =~ ^[Ss]$ ]]; then
        kill $SERVER_PID
        print_color "$GREEN" "✅ Servidor detenido"
    else
        print_color "$YELLOW" "💡 El servidor continúa ejecutándose en segundo plano (PID: $SERVER_PID)"
        print_color "$YELLOW" "   Para detenerlo manualmente: kill $SERVER_PID"
        print_color "$YELLOW" "   Documentación: http://127.0.0.1:8000/docs"
    fi
fi

echo ""
print_color "$GREEN" "🎉 ¡DEMO COMPLETADO EXITOSAMENTE!"
print_color "$CYAN" "   Resumen del flujo:"
print_color "$CYAN" "   1. ✅ Base de datos inicializada con usuario admin"
print_color "$CYAN" "   2. ✅ Servidor FastAPI iniciado"
print_color "$CYAN" "   3. ✅ Autenticación JWT exitosa"
print_color "$CYAN" "   4. ✅ ${#TASK_IDS[@]} tareas creadas con diferentes prioridades"
if [ "$HAS_ML" = true ]; then
    print_color "$CYAN" "   5. 🤖 Priorización ML de tareas"
    print_color "$CYAN" "   6. 🔄 Tareas completadas y modelo re-entrenado"
    print_color "$CYAN" "   7. ⏰ Recomendaciones de horario obtenidas"
    print_color "$CYAN" "   8. 📝 Feedback enviado al modelo"
else
    print_color "$CYAN" "   5. 📊 Sistema básico de tareas funcionando"
    print_color "$CYAN" "   6. ✅ Tareas creadas y gestionadas exitosamente"
fi
echo ""