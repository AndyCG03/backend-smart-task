from fastapi import APIRouter

# Importaciones directas SIN usar el archivo __init__.py
from app.api.endpoints.users import router as users_router
from app.api.endpoints.tasks import router as tasks_router
from app.api.endpoints.categories import router as categories_router
from app.api.endpoints.recommendations import router as recommendations_router
from app.api.endpoints.energy_logs import router as energy_logs_router
from app.api.endpoints.task_history import router as task_history_router
from app.api.endpoints.auth import router as auth_router 

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"]) 
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(energy_logs_router, prefix="/energy-logs", tags=["energy-logs"])
api_router.include_router(task_history_router, prefix="/task-history", tags=["task-history"])