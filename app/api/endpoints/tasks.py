from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.database_models import Task, User, Category
from app.models.pydantic_models import TaskCreate, TaskResponse
from app.security.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ← AÑADIR
):
    """Obtener lista de tareas del usuario actual"""
    query = db.query(Task).filter(Task.user_id == current_user.id)  # ← Filtrar por usuario actual
    
    if status:
        query = query.filter(Task.status == status)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ← AÑADIR
):
    """Obtener una tarea específica por ID"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id  # ← Verificar que pertenece al usuario
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,  # ← Ahora sin user_id
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ← AÑADIR
):
    """Crear una nueva tarea para el usuario actual"""
    
    # Usar el user_id del usuario autenticado automáticamente
    task_data = task.dict()
    task_data['user_id'] = current_user.id  # ← Asignar user_id automáticamente
    
    # Verificar que la categoría existe y pertenece al usuario (si se proporciona)
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
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID, 
    task_update: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ← AÑADIR
):
    """Actualizar una tarea existente"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id  # ← Verificar propiedad
    ).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
def delete_task(
    task_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ← AÑADIR
):
    """Eliminar una tarea"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id  # ← Verificar propiedad
    ).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}