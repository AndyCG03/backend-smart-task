from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.database import get_db
from app.models.database_models import DailyRecommendation, Task
from app.models.pydantic_models import DailyRecommendationCreate, DailyRecommendationResponse
from app.security.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[DailyRecommendationResponse])
def get_recommendations(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener recomendaciones diarias del usuario actual"""
    query = db.query(DailyRecommendation).filter(
        DailyRecommendation.user_id == current_user.id
    )
    
    if start_date:
        query = query.filter(DailyRecommendation.recommendation_date >= start_date)
    if end_date:
        query = query.filter(DailyRecommendation.recommendation_date <= end_date)
    if status:
        query = query.filter(DailyRecommendation.status == status)
    
    recommendations = query.offset(skip).limit(limit).all()
    return recommendations

@router.get("/{recommendation_id}", response_model=DailyRecommendationResponse)
def get_recommendation(
    recommendation_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener una recomendación específica por ID"""
    recommendation = db.query(DailyRecommendation).filter(
        DailyRecommendation.id == recommendation_id,
        DailyRecommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    return recommendation

@router.post("/", response_model=DailyRecommendationResponse)
def create_recommendation(
    recommendation: DailyRecommendationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Crear una nueva recomendación diaria"""
    existing_recommendation = db.query(DailyRecommendation).filter(
        DailyRecommendation.user_id == current_user.id,
        DailyRecommendation.recommendation_date == recommendation.recommendation_date
    ).first()
    
    if existing_recommendation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation already exists for this date"
        )
    
    task = db.query(Task).filter(
        Task.id == recommendation.task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db_recommendation = DailyRecommendation(
        **recommendation.dict(),
        user_id=current_user.id
    )
    
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

@router.put("/{recommendation_id}", response_model=DailyRecommendationResponse)
def update_recommendation(
    recommendation_id: UUID,
    recommendation_update: DailyRecommendationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Actualizar una recomendación existente"""
    db_recommendation = db.query(DailyRecommendation).filter(
        DailyRecommendation.id == recommendation_id,
        DailyRecommendation.user_id == current_user.id
    ).first()
    
    if not db_recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    for field, value in recommendation_update.dict(exclude_unset=True).items():
        setattr(db_recommendation, field, value)
    
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

@router.put("/{recommendation_id}/status")
def update_recommendation_status(
    recommendation_id: UUID,
    status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Actualizar el estado de una recomendación"""
    valid_statuses = ['pending', 'accepted', 'rejected', 'postponed']
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of: {', '.join(valid_statuses)}"
        )
    
    db_recommendation = db.query(DailyRecommendation).filter(
        DailyRecommendation.id == recommendation_id,
        DailyRecommendation.user_id == current_user.id
    ).first()
    
    if not db_recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    db_recommendation.status = status
    db.commit()
    
    return {"message": "Recommendation status updated successfully"}

@router.delete("/{recommendation_id}")
def delete_recommendation(
    recommendation_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Eliminar una recomendación"""
    db_recommendation = db.query(DailyRecommendation).filter(
        DailyRecommendation.id == recommendation_id,
        DailyRecommendation.user_id == current_user.id
    ).first()
    
    if not db_recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    db.delete(db_recommendation)
    db.commit()
    return {"message": "Recommendation deleted successfully"}