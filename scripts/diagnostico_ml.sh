#!/bin/bash
# test_ml_endpoints.sh

set -e

BASE_URL="http://127.0.0.1:8000"
ADMIN_EMAIL="admin@taskapp.com"
ADMIN_PASSWORD="Admin123!"

echo "🧪 TEST COMPLETO ENDPOINTS ML"
echo "============================="

# Login
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_EMAIL&password=$ADMIN_PASSWORD")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "✅ Login exitoso"
else
    echo "❌ Login falló"
    exit 1
fi

# Headers para requests
HEADERS=(-H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json")

# Función para hacer requests
api_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    if [ -n "$data" ]; then
        curl -s -X $method "$BASE_URL$endpoint" "${HEADERS[@]}" -d "$data"
    else
        curl -s -X $method "$BASE_URL$endpoint" "${HEADERS[@]}"
    fi
}

echo ""
echo "1. 🧠 Probando GET /api/v1/ml-tasks/prioritized"
RESPONSE=$(api_request "GET" "/api/v1/ml-tasks/prioritized")
if echo "$RESPONSE" | grep -q "ml_priority_score"; then
    echo "✅ OK - Endpoint funciona"
    TASK_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "   Tareas priorizadas: $TASK_COUNT"
else
    echo "❌ FAIL - No retorna scores ML"
fi

echo ""
echo "2. 📝 Obteniendo tareas existentes para testing..."
TASKS_RESPONSE=$(api_request "GET" "/api/v1/tasks/")
TASK_IDS=$(echo "$TASKS_RESPONSE" | python3 -c "
import sys, json
try:
    tasks = json.load(sys.stdin)
    ids = [task['id'] for task in tasks if task.get('status') == 'pending']
    print(' '.join(ids[:3]))  # Tomar primeras 3 tareas pendientes
except:
    print('')
")

if [ -z "$TASK_IDS" ]; then
    echo "❌ No hay tareas pendientes para testing"
    exit 1
fi

# Convertir a array
TASK_ARR=($TASK_IDS)
echo "   Tareas para testing: ${#TASK_ARR[@]}"

echo ""
echo "3. 🎯 Probando POST /api/v1/ml-tasks/{task_id}/train"
if [ ${#TASK_ARR[@]} -gt 0 ]; then
    RESPONSE=$(api_request "POST" "/api/v1/ml-tasks/${TASK_ARR[0]}/train")
    echo "   Respuesta: $RESPONSE"
    if echo "$RESPONSE" | grep -q -E "true|success|message"; then
        echo "✅ OK - Entrenamiento ejecutado"
    else
        echo "⚠️  Respuesta inesperada"
    fi
fi

echo ""
echo "4. ⏰ Probando GET /api/v1/ml-tasks/{task_id}/recommended-time"
if [ ${#TASK_ARR[@]} -gt 1 ]; then
    RESPONSE=$(api_request "GET" "/api/v1/ml-tasks/${TASK_ARR[1]}/recommended-time")
    echo "   Respuesta: $RESPONSE"
    if echo "$RESPONSE" | grep -q "recommended_time"; then
        REC_TIME=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('recommended_time', 'N/A'))")
        echo "✅ OK - Horario recomendado: $REC_TIME"
    else
        echo "⚠️  No se pudo obtener horario recomendado"
    fi
fi

echo ""
echo "5. 📊 Probando POST /api/v1/ml-tasks/{task_id}/feedback"
if [ ${#TASK_ARR[@]} -gt 2 ]; then
    # Probar con parámetros en query string
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/ml-tasks/${TASK_ARR[2]}/feedback?feedback_type=priority&was_useful=true&actual_priority=high&actual_completion_time=90" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    echo "   Respuesta: $RESPONSE"
    if echo "$RESPONSE" | grep -q "message"; then
        echo "✅ OK - Feedback enviado"
    else
        echo "⚠️  Respuesta inesperada"
    fi
fi

echo ""
echo "6. 🔄 Verificar priorización después de las operaciones..."
RESPONSE=$(api_request "GET" "/api/v1/ml-tasks/prioritized")
if echo "$RESPONSE" | grep -q "ml_priority_score"; then
    echo "✅ OK - Priorización ML sigue funcionando"
    echo ""
    echo "📈 RESUMEN FINAL ML:"
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    tasks = json.load(sys.stdin)
    for i, task in enumerate(tasks[:5]):
        title = task.get('title', '')[:30]
        score = task.get('ml_priority_score', 0)
        print(f'   {i+1}. {title:30} - Score: {score:.2f}')
except Exception as e:
    print(f'   Error: {e}')
"
else
    echo "❌ FAIL - Priorización ML no funciona después de operaciones"
fi

echo ""
echo "🎉 TEST ML COMPLETADO"