from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.database_models import Category
from app.models.pydantic_models import CategoryCreate, CategoryResponse
from app.security.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener categorías del usuario actual"""
    categories = db.query(Category).filter(
        Category.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Obtener una categoría específica por ID"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Crear una nueva categoría para el usuario actual"""
    existing_category = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == category.name
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    db_category = Category(**category.dict(), user_id=current_user.id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: UUID, 
    category_update: CategoryCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Actualizar una categoría existente"""
    db_category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    for field, value in category_update.dict(exclude_unset=True).items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}")
def delete_category(
    category_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Eliminar una categoría"""
    db_category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}