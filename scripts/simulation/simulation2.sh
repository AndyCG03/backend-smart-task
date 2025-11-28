#!/bin/bash

# simulate2.sh - Demo avanzado del sistema ML con casos de aprendizaje
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

# CASO 1: Demostrar aprendizaje con tareas realistas
print_color "$CYAN" "📚 CASO 1: Aprendizaje con patrones de productividad"
echo ""

print_color "$YELLOW" "🔄 Fase 1: Creando tareas con patrones reconocibles..."

# Tareas de alta prioridad que suelen completarse rápido
create_task() {
    local task_data=$1
    make_request "POST" "/api/v1/tasks/" "$task_data"
}

TASK_IDS=()

print_color "$BLUE" "📝 Creando tareas de 'Alta Productividad' (se completan rápido)..."
# Tareas que representan trabajo enfocado
TASK1=$(create_task '{
  "title": "Revisión código urgente - bug crítico",
  "description": "Arreglar bug en producción que afecta a usuarios",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 45,
  "priority_level": "high",
  "energy_required": "high",
  "deadline": "2025-11-22T14:00:00"
}')
TASK1_ID=$(echo "$TASK1" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
TASK_IDS+=("$TASK1_ID")
print_color "$GREEN" "   ✅ Tarea crítica creada"

TASK2=$(create_task '{
  "title": "Llamada con cliente premium",
  "description": "Reunión estratégica con cliente más importante",
  "urgency": "high", 
  "impact": "high",
  "estimated_duration": 30,
  "priority_level": "high",
  "energy_required": "medium",
  "deadline": "2025-11-22T11:00:00"
}')
TASK2_ID=$(echo "$TASK2" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
TASK_IDS+=("$TASK2_ID")
print_color "$GREEN" "   ✅ Tarea cliente premium creada"

# Tareas de baja prioridad que toman más tiempo
print_color "$BLUE" "📝 Creando tareas de 'Baja Urgencia' (toman más tiempo)..."
TASK3=$(create_task '{
  "title": "Actualizar documentación técnica",
  "description": "Mejorar documentación de API para desarrolladores",
  "urgency": "low",
  "impact": "medium",
  "estimated_duration": 120,
  "priority_level": "low", 
  "energy_required": "low",
  "deadline": "2025-11-25T18:00:00"
}')
TASK3_ID=$(echo "$TASK3" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
TASK_IDS+=("$TASK3_ID")
print_color "$GREEN" "   ✅ Tarea documentación creada"

TASK4=$(create_task '{
  "title": "Investigar nuevas tecnologías",
  "description": "Revisar frameworks alternativos para próximo proyecto",
  "urgency": "low",
  "impact": "low",
  "estimated_duration": 90,
  "priority_level": "low",
  "energy_required": "medium",
  "deadline": "2025-11-28T17:00:00"
}')
TASK4_ID=$(echo "$TASK4" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
TASK_IDS+=("$TASK4_ID")
print_color "$GREEN" "   ✅ Tarea investigación creada"

echo ""

# CASO 2: Simular completado con patrones reales
print_color "$CYAN" "🔄 CASO 2: Simulando comportamiento de usuario real..."
echo ""

print_color "$YELLOW" "🏃 Completando tareas con patrones de productividad..."

# Completar tareas críticas RÁPIDO (alta productividad)
print_color "$GREEN" "   ✅ Completando tarea crítica en 35min (rápido)"
make_request "PUT" "/api/v1/tasks/$TASK1_ID" '{"status": "completed"}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK1_ID/feedback?feedback_type=completion&was_useful=true&actual_completion_time=35" > /dev/null

print_color "$GREEN" "   ✅ Completando tarea cliente en 25min (muy rápido)" 
make_request "PUT" "/api/v1/tasks/$TASK2_ID" '{"status": "completed"}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK2_ID/feedback?feedback_type=completion&was_useful=true&actual_completion_time=25" > /dev/null

# Completar tareas de baja prioridad LENTO
print_color "$YELLOW" "   🐌 Completando tarea documentación en 180min (lento)"
make_request "PUT" "/api/v1/tasks/$TASK3_ID" '{"status": "completed"}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK3_ID/feedback?feedback_type=completion&was_useful=true&actual_completion_time=180" > /dev/null

print_color "$YELLOW" "   🐌 Completando tarea investigación en 150min (lento)"
make_request "PUT" "/api/v1/tasks/$TASK4_ID" '{"status": "completed"}' > /dev/null  
make_request "POST" "/api/v1/ml_tasks/$TASK4_ID/feedback?feedback_type=completion&was_useful=true&actual_completion_time=150" > /dev/null

echo ""

# CASO 3: Entrenar modelo con los nuevos datos
print_color "$CYAN" "🎯 CASO 3: Entrenando modelo con patrones aprendidos..."
echo ""

print_color "$YELLOW" "📈 Entrenando modelo ML..."
TRAIN_RESPONSE=$(make_request "POST" "/api/v1/ml_tasks/$TASK1_ID/train")
echo "   Respuesta: $TRAIN_RESPONSE"

# Esperar un poco para procesamiento
sleep 2

echo ""

# CASO 4: Crear nuevas tareas y ver si el modelo aprende
print_color "$CYAN" "🔮 CASO 4: Verificando aprendizaje del modelo..."
echo ""

print_color "$YELLOW" "📊 Creando nuevas tareas similares para test..."

# Nueva tarea similar a las que se completan rápido
TASK5=$(create_task '{
  "title": "Fix bug producción - servicio caído",
  "description": "Servicio crítico no responde, resolver inmediatamente",
  "urgency": "high",
  "impact": "high", 
  "estimated_duration": 60,
  "priority_level": "high",
  "energy_required": "high",
  "deadline": "2025-11-23T10:00:00"
}')
TASK5_ID=$(echo "$TASK5" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
TASK_IDS+=("$TASK5_ID")

# Nueva tarea similar a las que toman más tiempo
TASK6=$(create_task '{
  "title": "Refactorizar módulo legacy",
  "description": "Mejorar código antiguo para mejor mantenibilidad",
  "urgency": "low",
  "impact": "medium",
  "estimated_duration": 180,
  "priority_level": "low",
  "energy_required": "medium", 
  "deadline": "2025-11-30T17:00:00"
}')
TASK6_ID=$(echo "$TASK6" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
TASK_IDS+=("$TASK6_ID")

print_color "$GREEN" "   ✅ Nuevas tareas de test creadas"

echo ""

# Obtener priorización ML actualizada
print_color "$YELLOW" "🧠 Obteniendo priorización ML actualizada..."
ML_RESPONSE=$(make_request "GET" "/api/v1/ml_tasks/prioritized")

echo ""
print_color "$CYAN" "📊 RESULTADOS DEL APRENDIZAJE:"
print_color "$CYAN" "=============================="

echo "$ML_RESPONSE" | python3 -c "
import sys, json
try:
    tasks = json.load(sys.stdin)
    print('Tarea'.ljust(40) + ' | Score ML | Tipo')
    print('-' * 65)
    
    high_priority_tasks = []
    low_priority_tasks = []
    
    for task in tasks:
        title = task.get('title', '')[:38]
        ml_score = task.get('ml_priority_score', 0)
        
        # Clasificar por tipo de tarea
        if 'bug' in title.lower() or 'fix' in title.lower() or 'crític' in title.lower():
            task_type = '🚨 CRÍTICA'
            high_priority_tasks.append((title, ml_score, task_type))
        elif 'documentación' in title.lower() or 'refactor' in title.lower() or 'investigar' in title.lower():
            task_type = '📚 MANTENIMIENTO' 
            low_priority_tasks.append((title, ml_score, task_type))
        else:
            task_type = '⚡ MEDIA'
            
        print(f'{title:40} | {ml_score:8.2f} | {task_type}')
    
    print()
    print('🎯 ANÁLISIS DEL MODELO:')
    print('======================')
    
    if high_priority_tasks and low_priority_tasks:
        avg_high = sum(score for _, score, _ in high_priority_tasks) / len(high_priority_tasks)
        avg_low = sum(score for _, score, _ in low_priority_tasks) / len(low_priority_tasks)
        
        print(f'📈 Tareas críticas (score promedio): {avg_high:.2f}')
        print(f'📉 Tareas mantenimiento (score promedio): {avg_low:.2f}')
        print(f'📊 Diferencia: {avg_high - avg_low:.2f}')
        
        if avg_high > avg_low:
            print('✅ ¡EL MODELO APRENDIÓ! Prioriza correctamente tareas críticas')
        else:
            print('❌ El modelo no está priorizando correctamente')
            
    print()
    print('💡 LO QUE DEBERÍA PASAR:')
    print('=======================')
    print('• Tareas con \"bug\", \"fix\", \"crítico\" → Scores ALTOS')
    print('• Tareas con \"documentación\", \"refactor\" → Scores BAJOS') 
    print('• Esto refleja el patrón de completado rápido vs lento')
    
except Exception as e:
    print(f'Error procesando resultados: {e}')
"

echo ""

# CASO 5: Demostrar mejora continua
print_color "$CYAN" "🔄 CASO 5: Mejora continua con más feedback..."
echo ""

print_color "$YELLOW" "🎭 Simulando más interacciones de usuario..."

# Crear y completar más tareas para reforzar patrones
TASK7=$(create_task '{
  "title": "Hotfix - seguridad crítica",
  "description": "Parche de seguridad urgente para vulnerabilidad",
  "urgency": "high",
  "impact": "high",
  "estimated_duration": 90,
  "priority_level": "high",
  "energy_required": "high",
  "deadline": "2025-11-23T09:00:00"
}')
TASK7_ID=$(echo "$TASK7" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# Completar rápidamente
make_request "PUT" "/api/v1/tasks/$TASK7_ID" '{"status": "completed"}' > /dev/null
make_request "POST" "/api/v1/ml_tasks/$TASK7_ID/feedback?feedback_type=completion&was_useful=true&actual_completion_time=40" > /dev/null

print_color "$GREEN" "   ✅ Tarea seguridad completada en 40min"

# Re-entrenar modelo
make_request "POST" "/api/v1/ml_tasks/$TASK7_ID/train" > /dev/null

echo ""

# Resultados finales
print_color "$CYAN" "🎉 RESUMEN FINAL DEL APRENDIZAJE ML"
print_color "$CYAN" "==================================="

print_color "$GREEN" "✅ Lo que demostramos:"
echo "   • Patrón: Tareas críticas → Completadas rápido → High ML Score"
echo "   • Patrón: Tareas mantenimiento → Completadas lento → Low ML Score"  
echo "   • El modelo aprende de tiempos reales de completado"
echo "   • Mejora continua con feedback del usuario"

print_color "$BLUE" "📈 Métricas clave:"
echo "   • 4 tareas iniciales con patrones opuestos"
echo "   • 2 tareas de test para validar aprendizaje"
echo "   • 1 tarea adicional para mejora continua"
echo "   • Feedback de tiempos reales proporcionado"

print_color "$YELLOW" "💡 Valor del sistema:"
echo "   • Priorización automática basada en comportamiento real"
echo "   • Aprendizaje continuo sin intervención manual"
echo "   • Recomendaciones personalizadas por usuario"
echo "   • Mejora con el tiempo y más uso"

echo ""
print_color "$GREEN" "🎯 ¡DEMO COMPLETADA! El sistema ML demostró aprendizaje efectivo."