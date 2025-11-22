from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

from app.database import get_db
from app.models.database_models import EnergyLog, Task
from app.models.pydantic_models import EnergyLogCreate, EnergyLogResponse
from app.security.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[EnergyLogResponse])
def get_energy_logs(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    task_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener logs de energía del usuario actual"""
    query = db.query(EnergyLog).filter(EnergyLog.user_id == current_user.id)
    
    if start_date:
        query = query.filter(EnergyLog.logged_at >= start_date)
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(EnergyLog.logged_at <= end_datetime)
    if task_id:
        query = query.filter(EnergyLog.task_id == task_id)
    
    logs = query.order_by(EnergyLog.logged_at.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/{log_id}", response_model=EnergyLogResponse)
def get_energy_log(
    log_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener un log de energía específico por ID"""
    energy_log = db.query(EnergyLog).filter(
        EnergyLog.id == log_id,
        EnergyLog.user_id == current_user.id
    ).first()
    if not energy_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy log not found"
        )
    return energy_log

@router.post("/", response_model=EnergyLogResponse)
def create_energy_log(
    energy_log: EnergyLogCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Crear un nuevo log de energía"""
    if energy_log.task_id:
        task = db.query(Task).filter(
            Task.id == energy_log.task_id,
            Task.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
    
    db_energy_log = EnergyLog(**energy_log.dict(), user_id=current_user.id)
    db.add(db_energy_log)
    db.commit()
    db.refresh(db_energy_log)
    return db_energy_log

@router.put("/{log_id}", response_model=EnergyLogResponse)
def update_energy_log(
    log_id: UUID,
    energy_log_update: EnergyLogCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Actualizar un log de energía existente"""
    db_energy_log = db.query(EnergyLog).filter(
        EnergyLog.id == log_id,
        EnergyLog.user_id == current_user.id
    ).first()
    if not db_energy_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy log not found"
        )
    
    for field, value in energy_log_update.dict(exclude_unset=True).items():
        setattr(db_energy_log, field, value)
    
    db.commit()
    db.refresh(db_energy_log)
    return db_energy_log

@router.delete("/{log_id}")
def delete_energy_log(
    log_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Eliminar un log de energía"""
    db_energy_log = db.query(EnergyLog).filter(
        EnergyLog.id == log_id,
        EnergyLog.user_id == current_user.id
    ).first()
    if not db_energy_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy log not found"
        )
    
    db.delete(db_energy_log)
    db.commit()
    return {"message": "Energy log deleted successfully"}