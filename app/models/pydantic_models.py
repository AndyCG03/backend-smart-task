from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    energy_level: Optional[str] = 'medium'
    preferences: Optional[Dict[str, Any]] = None

class UserBase(BaseModel):
    email: EmailStr
    name: str
    preferences: Optional[Dict[str, Any]] = None
    energy_level: Optional[str] = 'medium'

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 72:
            raise ValueError('Password cannot exceed 72 characters')
        return v

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    urgency: Optional[str] = None
    impact: Optional[str] = None
    estimated_duration: Optional[int] = None
    deadline: Optional[datetime] = None
    category_id: Optional[UUID] = None
    energy_required: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: UUID
    user_id: UUID  
    priority_score: Optional[int] = None
    priority_level: Optional[str] = None
    completion_probability: Optional[float] = None
    status: str = 'pending'
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    actual_duration: Optional[int] = None
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    color: Optional[str] = '#007bff'
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class DailyRecommendationBase(BaseModel):
    task_id: UUID
    recommendation_reason: str
    confidence_score: Optional[float] = None

class DailyRecommendationCreate(DailyRecommendationBase):
    recommendation_date: date

class DailyRecommendationResponse(DailyRecommendationBase):
    id: UUID
    user_id: UUID
    status: str = 'pending'
    was_completed: Optional[bool] = None
    completed_on_time: Optional[bool] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class EnergyLogBase(BaseModel):
    energy_level: str
    notes: Optional[str] = None
    task_id: Optional[UUID] = None

class EnergyLogCreate(EnergyLogBase):
    pass

class EnergyLogResponse(EnergyLogBase):
    id: UUID
    user_id: UUID
    logged_at: datetime
    
    class Config:
        from_attributes = True


class TaskHistoryBase(BaseModel):
    change_type: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    change_description: Optional[str] = None

class TaskHistoryResponse(TaskHistoryBase):
    id: UUID
    task_id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True