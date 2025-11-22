# app/api/endpoints/ml_tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.database_models import Task, User, TaskMLData, MLFeedback
from app.models.pydantic_models import TaskResponse
from app.security.auth import get_current_active_user
from app.services.ai_service import TaskAgent

router = APIRouter()

class MLTaskResponse(TaskResponse):
    ml_priority_score: float = None
    recommended_schedule: str = None

@router.get("/prioritized", response_model=List[MLTaskResponse])
def get_prioritized_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener tareas ordenadas por el modelo ML"""
    # Obtener tareas pendientes
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status.in_(['pending', 'in_progress'])
    ).offset(skip).limit(limit).all()

    # Usar el agente ML para priorizar
    agent = TaskAgent(db, current_user.id)
    prioritized_tasks = agent.predecir_prioridad_tareas(tasks)
    
    # Convertir a respuesta
    response = []
    for task_data in prioritized_tasks:
        task_dict = TaskResponse.from_orm(task_data['task_obj']).dict()
        task_dict['ml_priority_score'] = task_data['puntaje_ml']
        response.append(MLTaskResponse(**task_dict))
    
    return response

@router.post("/{task_id}/train")
def train_model_for_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Entrenar modelo cuando se completa una tarea"""
    agent = TaskAgent(db, current_user.id)
    success = agent.entrenar_modelo_prioridad()
    
    return {
        "message": "Modelo actualizado exitosamente" if success else "No hay suficientes datos para entrenar",
        "trained": success
    }

@router.get("/{task_id}/recommended-time")
def get_recommended_time(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener horario recomendado para una tarea"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    agent = TaskAgent(db, current_user.id)
    recommended_time = agent.recomendar_horario(task)
    
    return {
        "task_id": task_id,
        "recommended_time": recommended_time,
        "message": f"Horario recomendado: {recommended_time}"
    }

@router.post("/{task_id}/feedback")
def submit_ml_feedback(
    task_id: UUID,
    feedback_type: str,
    was_useful: bool,
    actual_priority: str = None,
    actual_completion_time: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Enviar feedback sobre las predicciones del ML"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    feedback = MLFeedback(
        task_id=task_id,
        user_id=current_user.id,
        feedback_type=feedback_type,
        was_useful=was_useful,
        actual_priority=actual_priority,
        actual_completion_time=actual_completion_time
    )
    
    db.add(feedback)
    db.commit()
    
    # Si el feedback es negativo, reentrenar el modelo
    if not was_useful:
        agent = TaskAgent(db, current_user.id)
        agent.entrenar_modelo_prioridad()
    
    return {"message": "Feedback registrado exitosamente"}