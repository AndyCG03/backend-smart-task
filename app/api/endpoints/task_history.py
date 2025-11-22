from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.database_models import TaskHistory, Task
from app.models.pydantic_models import TaskHistoryResponse
from app.security.auth import get_current_active_user

router = APIRouter()

@router.get("/task/{task_id}", response_model=List[TaskHistoryResponse])
def get_task_history(
    task_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener historial de cambios de una tarea específica"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    history = db.query(TaskHistory).filter(
        TaskHistory.task_id == task_id
    ).order_by(TaskHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    return history

@router.get("/user/", response_model=List[TaskHistoryResponse])
def get_user_task_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener historial de cambios de todas las tareas del usuario actual"""
    history = db.query(TaskHistory).filter(
        TaskHistory.user_id == current_user.id
    ).order_by(TaskHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    return history

@router.get("/{history_id}", response_model=TaskHistoryResponse)
def get_history_entry(
    history_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener una entrada específica del historial"""
    history_entry = db.query(TaskHistory).filter(
        TaskHistory.id == history_id,
        TaskHistory.user_id == current_user.id
    ).first()
    if not history_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History entry not found"
        )
    return history_entry