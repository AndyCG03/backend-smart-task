#!/bin/bash

# simulate3.sh - Demo avanzado del sistema ML (¡CORREGIDO y FUNCIONAL!)
# Usa las rutas reales: /api/v1/ml_tasks/ (con guión bajo _)
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Configuración
BASE_URL="http://127.0.0.1:8000"
ADMIN_EMAIL="admin@taskapp.com"
ADMIN_PASSWORD="Admin123!"

echo ""
print_color "$CYAN" "🧠 DEMO AVANZADO: Sistema de Aprendizaje ML"
print_color "$CYAN" "============================================"
echo ""

# Función para hacer requests
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

# Login
print_color "$YELLOW" "🔐 Autenticando..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_EMAIL&password=$ADMIN_PASSWORD")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    print_color "$GREEN" "✅ Autenticación exitosa"
else
    print_color "$RED" "❌ Error en autenticación"
    exit 1
fi

echo ""

# Función para crear tarea
create_task() {
    local task_data=$1
    make_request "POST" "/api/v1/tasks/" "$task_data"
}

# CASO 1: Crear tareas con patrones de comportamiento
print_color "$CYAN" "📚 CASO 1: Creando tareas con patrones reconocibles"
echo ""

print_color "$BLUE" "📝 Creando tareas CRÍTICAS (se completan RÁPIDO en la realidad)..."
TASK1=$(create_task '{
  "title": "Fix bug producción - servicio caído",
  "description": "Error crítico en API de pagos",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 45,
  "priority_level": "high",
  "energy_required": "high"
}')
TASK1_ID=$(echo "$TASK1" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
print_color "$GREEN" "   ✅ Tarea crítica creada"

TASK2=$(create_task '{
  "title": "Llamada con cliente premium",
  "description": "Reunión con cliente top",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 30,
  "priority_level": "high",
  "energy_required": "medium"
}')
TASK2_ID=$(echo "$TASK2" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
print_color "$GREEN" "   ✅ Tarea cliente premium creada"

print_color "$BLUE" "📝 Creando tareas de MANTENIMIENTO (se completan LENTO)..."
TASK3=$(create_task '{
  "title": "Actualizar documentación técnica",
  "description": "Docs del módulo de autenticación",
  "urgency": "low",
  "impact": "medium",
  "estimated_duration": 120,
  "priority_level": "low",
  "energy_required": "low"
}')
TASK3_ID=$(echo "$TASK3" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
print_color "$GREEN" "   ✅ Tarea documentación creada"

TASK4=$(create_task '{
  "title": "Investigar nuevas librerías de ML",
  "description": "Estudio de frameworks para próxima versión",
  "urgency": "low",
  "impact": "low",
  "estimated_duration": 90,
  "priority_level": "low",
  "energy_required": "medium"
}')
TASK4_ID=$(echo "$TASK4" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
print_color "$GREEN" "   ✅ Tarea investigación creada"

echo ""

# CASO 2: Simular completado con tiempos reales
print_color "$CYAN" "🔄 CASO 2: Simulando comportamiento de usuario real"
echo ""

print_color "$GREEN" "   ✅ Completando tarea crítica en 35min (rápido)"
make_request "PUT" "/api/v1/tasks/$TASK1_ID" '{"status": "completed"}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK1_ID/feedback" '{"feedback_type":"completion","was_useful":true,"actual_completion_time":35}' > /dev/null

print_color "$GREEN" "   ✅ Completando tarea cliente en 25min (muy rápido)"
make_request "PUT" "/api/v1/tasks/$TASK2_ID" '{"status": "completed"}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK2_ID/feedback" '{"feedback_type":"completion","was_useful":true,"actual_completion_time":25}' > /dev/null

print_color "$YELLOW" "   🐌 Completando documentación en 180min (lento)"
make_request "PUT" "/api/v1/tasks/$TASK3_ID" '{"status": "completed"}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK3_ID/feedback" '{"feedback_type":"completion","was_useful":true,"actual_completion_time":180}' > /dev/null

print_color "$YELLOW" "   🐌 Completando investigación en 150min (lento)"
make_request "PUT" "/api/v1/tasks/$TASK4_ID" '{"status": "completed"}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK4_ID/feedback" '{"feedback_type":"completion","was_useful":true,"actual_completion_time":150}' > /dev/null

echo ""

# CASO 3: Entrenar modelo
print_color "$CYAN" "🎯 CASO 3: Entrenando modelo con patrones aprendidos"
echo ""

print_color "$YELLOW" "📈 Entrenando modelo ML..."
TRAIN_RESPONSE=$(make_request "POST" "/api/v1/ml_tasks/$TASK1_ID/train")
print_color "$GREEN" "   Respuesta: $TRAIN_RESPONSE"

sleep 2

echo ""

# CASO 4: Crear tareas de test y verificar aprendizaje
print_color "$CYAN" "🔮 CASO 4: Verificando que el modelo aprendió"
echo ""

print_color "$BLUE" "📊 Creando nuevas tareas de prueba..."
TASK5=$(create_task '{
  "title": "Hotfix - vulnerabilidad seguridad",
  "description": "Parche urgente para CVE-2025-XXXX",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 60,
  "priority_level": "high",
  "energy_required": "high"
}')
TASK5_ID=$(echo "$TASK5" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

TASK6=$(create_task '{
  "title": "Refactorizar módulo de notificaciones",
  "description": "Mejorar código legacy",
  "urgency": "low",
  "impact": "medium",
  "estimated_duration": 180,
  "priority_level": "low",
  "energy_required": "medium"
}')
TASK6_ID=$(echo "$TASK6" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

print_color "$GREEN" "   ✅ Tareas de test creadas"

# Obtener priorización
print_color "$YELLOW" "🧠 Obteniendo priorización ML actualizada..."
ML_RESPONSE=$(make_request "GET" "/api/v1/ml_tasks/prioritized")

echo ""
print_color "$CYAN" "📊 RESULTADOS DEL APRENDIZAJE:"
print_color "$CYAN" "=============================="

# Procesar resultados en Python
echo "$ML_RESPONSE" | python3 -c "
import sys, json
try:
    tasks = json.load(sys.stdin)
    if not isinstance(tasks, list):
        print('❌ Respuesta inesperada:', tasks)
        sys.exit(1)
        
    print('Tarea'.ljust(42) + ' | Score ML')
    print('-' * 55)
    
    hotfix_task = None
    refactor_task = None
    
    for task in tasks:
        title = task.get('title', '')[:40]
        score = task.get('ml_priority_score', 0)
        print(f'{title:42} | {score:8.2f}')
        
        if 'Hotfix' in title:
            hotfix_task = task
        elif 'Refactor' in title:
            refactor_task = task
    
    print()
    if hotfix_task and refactor_task:
        diff = hotfix_task['ml_priority_score'] - refactor_task['ml_priority_score']
        print(f'📈 Hotfix score: {hotfix_task[\"ml_priority_score\"]:.2f}')
        print(f'📉 Refactor score: {refactor_task[\"ml_priority_score\"]:.2f}')
        print(f'📊 Diferencia: {diff:.2f}')
        
        if diff > 0:
            print()
            print('✅ ¡EL MODELO APRENDIÓ! Prioriza tareas críticas con scores más altos.')
        else:
            print()
            print('❌ El modelo NO está priorizando correctamente.')
    else:
        print('⚠️ No se encontraron las tareas de test esperadas.')
        
except Exception as e:
    print(f'❌ Error al procesar resultados: {e}')
    import traceback
    traceback.print_exc()
"

echo ""

# CASO 5: Mejora continua (opcional)
print_color "$CYAN" "🔄 CASO 5: Simulando mejora continua"
print_color "$YELLOW" "🎭 Agregando una tarea crítica adicional..."
TASK7=$(create_task '{
  "title": "Arreglar error en facturación",
  "description": "Clientes no reciben facturas",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 50,
  "priority_level": "high",
  "energy_required": "high"
}')
TASK7_ID=$(echo "$TASK7" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

make_request "PUT" "/api/v1/tasks/$TASK7_ID" '{"status": "completed"}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK7_ID/feedback" '{"feedback_type":"completion","was_useful":true,"actual_completion_time":40}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK7_ID/train" > /dev/null
print_color "$GREEN" "   ✅ Tarea adicional procesada y modelo reentrenado"

echo ""
print_color "$GREEN" "🎯 ¡DEMO COMPLETADA! El sistema ML aprende de tu comportamiento real."
print_color "$YELLOW" "💡 Cuantas más tareas completes con feedback, ¡mejor priorizará!"