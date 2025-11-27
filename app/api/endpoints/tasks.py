from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.database_models import Task, User, Category, TaskHistory
from app.models.pydantic_models import TaskCreate, TaskResponse
from app.security.auth import get_current_active_user

router = APIRouter()

# Lista de estados válidos para las tareas
VALID_STATUSES = ['pending', 'in_progress', 'completed', 'archived', 'postponed']

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) 
):
    """Obtener lista de tareas del usuario actual"""
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be one of: {', '.join(VALID_STATUSES)}"
            )
        query = query.filter(Task.status == status)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  
):
    """Obtener una tarea específica por ID"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id  
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) 
):
    """Crear una nueva tarea para el usuario actual"""
    
    task_data = task.dict()
    task_data['user_id'] = current_user.id 
    
    if task.category_id:
        category = db.query(Category).filter(
            Category.id == task.category_id,
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or doesn't belong to user"
            )
    
    db_task = Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Registrar en el historial
    history_entry = TaskHistory(
        task_id=db_task.id,
        user_id=current_user.id,
        change_type='created',
        new_values={
            'title': db_task.title,
            'status': db_task.status,
            'description': db_task.description
        },
        change_description='Task created'
    )
    db.add(history_entry)
    db.commit()
    
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID, 
    task_update: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar una tarea existente"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id 
    ).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Guardar el estado anterior para el historial
    old_status = db_task.status
    
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    
    # Registrar cambios en el historial si hubo modificaciones
    if task_update.dict(exclude_unset=True):
        history_entry = TaskHistory(
            task_id=task_id,
            user_id=current_user.id,
            change_type='updated',
            new_values=task_update.dict(exclude_unset=True),
            change_description='Task updated'
        )
        db.add(history_entry)
        db.commit()
    
    return db_task

@router.patch("/{task_id}/status")
def update_task_status(
    task_id: UUID,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar solo el estado de una tarea"""
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of: {', '.join(VALID_STATUSES)}"
        )
    
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Guardar estado anterior para el historial
    old_status = db_task.status
    
    # Actualizar estado
    db_task.status = status
    
    # Si se marca como completada, registrar fecha de completado
    if status == 'completed' and not db_task.completed_at:
        db_task.completed_at = func.now()
    
    db.commit()
    db.refresh(db_task)
    
    # Registrar cambio de estado en el historial
    history_entry = TaskHistory(
        task_id=task_id,
        user_id=current_user.id,
        change_type='status_changed',
        old_values={'status': old_status},
        new_values={'status': status},
        change_description=f'Status changed from {old_status} to {status}'
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "message": f"Task status updated to {status}",
        "task_id": str(task_id),
        "new_status": status
    }


@router.delete("/{task_id}")
def delete_task(
    task_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) 
):
    """Eliminar una tarea"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Registrar eliminación en el historial antes de borrar
    history_entry = TaskHistory(
        task_id=task_id,
        user_id=current_user.id,
        change_type='deleted',
        old_values={
            'title': db_task.title,
            'status': db_task.status
        },
        change_description='Task deleted'
    )
    db.add(history_entry)
    
    db.delete(db_task)
    db.commit()
    
    return {"message": "Task deleted successfully"}